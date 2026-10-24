# -*- coding: utf-8 -*-
"""Filters used by the preflight role to analyse cluster data.

All functions are pure: they take objects returned by kubernetes.core.k8s_info
and return plain dicts/lists that the report template can render.
"""

from __future__ import annotations

import re

ODF_LABEL = "cluster.ocs.openshift.io/openshift-storage"
KVM_RESOURCE = "devices.kubevirt.io/kvm"
CPU_MODEL_PREFIX = "cpu-model.node.kubevirt.io/"
HOST_MODEL_PREFIX = "host-model-cpu.node.kubevirt.io/"
NFD_VMX = "feature.node.kubernetes.io/cpu-cpuid.VMX"
NFD_SVM = "feature.node.kubernetes.io/cpu-cpuid.SVM"
ROLE_PREFIX = "node-role.kubernetes.io/"

_MEM_SUFFIX = {
    "Ki": 1024, "Mi": 1024 ** 2, "Gi": 1024 ** 3, "Ti": 1024 ** 4, "Pi": 1024 ** 5, "Ei": 1024 ** 6,
    "k": 1000, "K": 1000, "M": 1000 ** 2, "G": 1000 ** 3, "T": 1000 ** 4, "P": 1000 ** 5, "E": 1000 ** 6,
    "m": 0.001,
}


def k8s_cpu_to_millis(value) -> int:
    """'250m' -> 250, '2' -> 2000, '1.5' -> 1500."""
    if value is None or value == "":
        return 0
    value = str(value)
    if value.endswith("m"):
        return int(float(value[:-1]))
    return int(float(value) * 1000)


def k8s_mem_to_bytes(value) -> int:
    """'512Mi' -> 536870912, '1G' -> 1000000000, '1e3' -> 1000."""
    if value is None or value == "":
        return 0
    value = str(value)
    match = re.match(r"^([0-9.eE+-]+)([A-Za-z]*)$", value)
    if not match:
        return 0
    number, suffix = match.groups()
    return int(float(number) * _MEM_SUFFIX.get(suffix, 1))


def _pod_requests(pod) -> tuple[int, int]:
    """Effective requests of a pod: max(sum(containers), max(initContainers)) + overhead."""
    spec = pod.get("spec", {})

    def _sum(containers):
        cpu = mem = 0
        for c in containers or []:
            req = (c.get("resources") or {}).get("requests") or {}
            cpu += k8s_cpu_to_millis(req.get("cpu"))
            mem += k8s_mem_to_bytes(req.get("memory"))
        return cpu, mem

    cpu, mem = _sum(spec.get("containers"))
    for ic in spec.get("initContainers") or []:
        req = (ic.get("resources") or {}).get("requests") or {}
        cpu = max(cpu, k8s_cpu_to_millis(req.get("cpu")))
        mem = max(mem, k8s_mem_to_bytes(req.get("memory")))
    overhead = spec.get("overhead") or {}
    cpu += k8s_cpu_to_millis(overhead.get("cpu"))
    mem += k8s_mem_to_bytes(overhead.get("memory"))
    return cpu, mem


def preflight_nodes(nodes, pods, exclude_odf=True, probe=None):
    """Summarise every node and decide which workers can run VMs.

    probe: optional dict {node_name: {"kvm": bool, "cpu_model_name": str}} from the
    privileged probe pods.
    """
    probe = probe or {}
    requests = {}
    for pod in pods or []:
        node = pod.get("spec", {}).get("nodeName")
        if not node:
            continue
        if pod.get("status", {}).get("phase") in ("Succeeded", "Failed"):
            continue
        cpu, mem = _pod_requests(pod)
        cur = requests.setdefault(node, [0, 0])
        cur[0] += cpu
        cur[1] += mem

    result = []
    for node in nodes or []:
        meta = node.get("metadata", {})
        name = meta.get("name")
        labels = meta.get("labels") or {}
        spec = node.get("spec", {})
        status = node.get("status", {})
        roles = sorted(k[len(ROLE_PREFIX):] for k in labels if k.startswith(ROLE_PREFIX))
        taints = spec.get("taints") or []
        hard_taints = [t for t in taints if t.get("effect") in ("NoSchedule", "NoExecute")]
        odf = ODF_LABEL in labels
        ready = any(c.get("type") == "Ready" and c.get("status") == "True"
                    for c in status.get("conditions") or [])
        allocatable = status.get("allocatable") or {}
        capacity = status.get("capacity") or {}

        # /dev/kvm: KubeVirt/CNV device plugin > KubeVirt node labels > NFD CPU flags >
        # probe pod > unknown. Capacity 0 only means the device plugin is not running
        # (e.g. right after OpenShift Virtualization was removed), not "no KVM".
        kvm, kvm_source = None, "unknown"
        has_kubevirt_labels = any(k.startswith((CPU_MODEL_PREFIX, HOST_MODEL_PREFIX)) for k in labels)
        if k8s_mem_to_bytes(capacity.get(KVM_RESOURCE)) > 0:
            # Capacity is a quantity such as "1k" (KubeVirt advertises 1000 slots).
            kvm, kvm_source = True, "device-plugin"
        elif has_kubevirt_labels:
            kvm, kvm_source = True, "kubevirt node labels"
        elif labels.get(NFD_VMX) == "true" or labels.get(NFD_SVM) == "true":
            kvm, kvm_source = True, "nfd (cpu flags only)"
        elif name in probe:
            kvm, kvm_source = bool(probe[name].get("kvm")), "probe"

        host_model = next((k[len(HOST_MODEL_PREFIX):] for k in labels
                           if k.startswith(HOST_MODEL_PREFIX)), None)
        supported_models = sorted(k[len(CPU_MODEL_PREFIX):] for k in labels
                                  if k.startswith(CPU_MODEL_PREFIX) and labels[k] == "true")
        cpu_model_name = probe.get(name, {}).get("cpu_model_name")

        alloc_cpu = k8s_cpu_to_millis(allocatable.get("cpu"))
        alloc_mem = k8s_mem_to_bytes(allocatable.get("memory"))
        req_cpu, req_mem = requests.get(name, [0, 0])

        reasons = []
        if "worker" not in roles:
            reasons.append("not a worker")
        if spec.get("unschedulable"):
            reasons.append("cordoned")
        if not ready:
            reasons.append("not Ready")
        if hard_taints:
            reasons.append("tainted: " + ", ".join(
                "%s:%s" % (t.get("key"), t.get("effect")) for t in hard_taints))
        if odf and exclude_odf:
            reasons.append("ODF storage node")
        if kvm is False:
            reasons.append("no /dev/kvm")

        result.append({
            "name": name,
            "roles": roles,
            "ready": ready,
            "odf": odf,
            "taints": ["%s=%s:%s" % (t.get("key"), t.get("value", ""), t.get("effect")) for t in taints],
            "labels": {k: v for k, v in labels.items()
                       if not k.startswith((CPU_MODEL_PREFIX, "cpu-feature.node.kubevirt.io/",
                                            "cpu-timer.node.kubevirt.io/", "feature.node.kubernetes.io/",
                                            "hyperv.node.kubevirt.io/", "scheduling.node.kubevirt.io/",
                                            "host-model-required-features.node.kubevirt.io/"))},
            "kvm": kvm,
            "kvm_source": kvm_source,
            "host_model": host_model,
            "supported_cpu_models": supported_models,
            "cpu_model_name": cpu_model_name,
            "cpu_alloc_m": alloc_cpu,
            "cpu_req_m": req_cpu,
            "cpu_free_m": alloc_cpu - req_cpu,
            "mem_alloc": alloc_mem,
            "mem_req": req_mem,
            "mem_free": alloc_mem - req_mem,
            "eligible": not reasons,
            "reasons": reasons,
        })
    return sorted(result, key=lambda n: n["name"])


def preflight_cpu_model(eligible, preference):
    """Propose a cpuModel for the KubeVirt CR.

    Returns {"value": str, "confidence": "high|medium|low", "note": str}.
    """
    if not eligible:
        return {"value": "", "confidence": "low", "note": "no eligible workers"}

    host_models = {n["host_model"] for n in eligible if n.get("host_model")}
    names = {n["cpu_model_name"] for n in eligible if n.get("cpu_model_name")}

    if len(host_models) == 1 and all(n.get("host_model") for n in eligible):
        return {"value": "", "confidence": "high",
                "note": "all eligible workers report host model %s: keep the default (host-model)"
                        % next(iter(host_models))}

    sets = [set(n["supported_cpu_models"]) for n in eligible if n.get("supported_cpu_models")]
    if sets and len(sets) == len(eligible):
        common = set.intersection(*sets)
        for model in preference:
            if model in common:
                return {"value": model, "confidence": "high",
                        "note": "workers have different CPUs; %s is the newest model all of them support"
                                % model}
        if common:
            model = sorted(common)[-1]
            return {"value": model, "confidence": "medium",
                    "note": "picked %s from the common models (not in the preference list)" % model}
        return {"value": "", "confidence": "low", "note": "no CPU model common to all workers"}

    if names and len(names) == 1 and len([n for n in eligible if n.get("cpu_model_name")]) == len(eligible):
        return {"value": "", "confidence": "medium",
                "note": "probe: every worker has '%s'; host-model should migrate fine" % next(iter(names))}
    if len(names) > 1:
        return {"value": "", "confidence": "low",
                "note": "probe: workers have different CPUs (%s). Set kubevirt_cpu_model to a named "
                        "model they all support (check `virsh domcapabilities` or rerun after KubeVirt "
                        "is installed to get the cpu-model labels)" % ", ".join(sorted(names))}
    return {"value": "", "confidence": "low",
            "note": "CPU model unknown (no KubeVirt/CNV labels and probe disabled)"}


def preflight_free_nics(nns_list, node_names=None):
    """Return {node: [nic, ...]} of ethernet NICs not used by anything else.

    A NIC is "free" when it is ethernet, has no controller (not enslaved to a bond or
    bridge), has no IPv4/IPv6 address, and is not used by a route.
    """
    out = {}
    for nns in nns_list or []:
        node = nns.get("metadata", {}).get("name")
        if node_names and node not in node_names:
            continue
        current = (nns.get("status") or {}).get("currentState") or {}
        ifaces = current.get("interfaces") or []
        routes = ((current.get("routes") or {}).get("running") or [])
        route_ifaces = {r.get("next-hop-interface") for r in routes}
        # Ports used by bridges/bonds/ovs.
        used = set()
        for i in ifaces:
            bridge = i.get("bridge") or {}
            for p in bridge.get("port") or []:
                used.add(p.get("name"))
            agg = i.get("link-aggregation") or {}
            for p in agg.get("port") or agg.get("slaves") or []:
                used.add(p if isinstance(p, str) else p.get("name"))
        free = []
        for i in ifaces:
            if i.get("type") != "ethernet":
                continue
            name = i.get("name")
            if name in used or name in route_ifaces:
                continue
            if i.get("controller") or i.get("master"):
                continue
            v4 = i.get("ipv4") or {}
            v6 = i.get("ipv6") or {}
            if (v4.get("enabled") and v4.get("address")) or (v6.get("enabled") and [
                    a for a in v6.get("address") or [] if not str(a.get("ip", "")).startswith("fe80")]):
                continue
            free.append({"name": name, "state": i.get("state"), "mac": i.get("mac-address")})
        out[node] = free
    return out


def preflight_common_nic(free_nics):
    """Return the NIC name that is free on every node, or ''."""
    sets = [set(n["name"] for n in nics) for nics in free_nics.values()]
    if not sets:
        return ""
    common = set.intersection(*sets)
    return sorted(common)[0] if common else ""


def preflight_node_placement(eligible, all_workers):
    """Propose spec.workloads.nodePlacement."""
    names = sorted(n["name"] for n in eligible)
    worker_names = sorted(n["name"] for n in all_workers)
    if not names:
        return {}
    if names == worker_names:
        return {"nodeSelector": {"node-role.kubernetes.io/worker": ""}}
    return {"affinity": {"nodeAffinity": {"requiredDuringSchedulingIgnoredDuringExecution": {
        "nodeSelectorTerms": [{"matchExpressions": [{
            "key": "kubernetes.io/hostname", "operator": "In", "values": names}]}]}}}}


def human_bytes(value):
    value = float(value or 0)
    for unit in ("B", "KiB", "MiB", "GiB", "TiB", "PiB"):
        if abs(value) < 1024 or unit == "PiB":
            return "%.1f %s" % (value, unit)
        value /= 1024
    return "%.1f PiB" % value


class FilterModule(object):
    def filters(self):
        return {
            "k8s_cpu_to_millis": k8s_cpu_to_millis,
            "k8s_mem_to_bytes": k8s_mem_to_bytes,
            "preflight_nodes": preflight_nodes,
            "preflight_cpu_model": preflight_cpu_model,
            "preflight_free_nics": preflight_free_nics,
            "preflight_common_nic": preflight_common_nic,
            "preflight_node_placement": preflight_node_placement,
            "human_bytes": human_bytes,
        }
