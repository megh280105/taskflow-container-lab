package main

workload_kinds := {"Deployment", "StatefulSet"}
readonly_components := {"backend", "worker", "frontend"}

is_workload if {
  workload_kinds[input.kind]
}

component := value if {
  value := object.get(object.get(input.metadata, "labels", {}), "app.kubernetes.io/component", "")
  value != ""
}

component := value if {
  value := object.get(object.get(object.get(input.spec.template, "metadata", {}), "labels", {}), "app.kubernetes.io/component", "")
  value != ""
}

component := value if {
  value := object.get(object.get(input.metadata, "labels", {}), "app", "")
  value != ""
}

component := value if {
  value := object.get(object.get(object.get(input.spec.template, "metadata", {}), "labels", {}), "app", "")
  value != ""
}

deny contains msg if {
  is_workload
  not input.spec.template.spec.serviceAccountName
  msg := sprintf("%s must define a dedicated serviceAccountName", [input.metadata.name])
}

deny contains msg if {
  is_workload
  input.spec.template.spec.automountServiceAccountToken != false
  msg := sprintf("%s must disable automountServiceAccountToken", [input.metadata.name])
}

deny contains msg if {
  is_workload
  input.spec.template.spec.securityContext.seccompProfile.type != "RuntimeDefault"
  msg := sprintf("%s must use RuntimeDefault seccomp", [input.metadata.name])
}

deny contains msg if {
  is_workload
  container := input.spec.template.spec.containers[_]
  container.securityContext.runAsNonRoot != true
  msg := sprintf("%s/%s must runAsNonRoot", [input.metadata.name, container.name])
}

deny contains msg if {
  is_workload
  container := input.spec.template.spec.containers[_]
  container.securityContext.allowPrivilegeEscalation != false
  msg := sprintf("%s/%s must disable privilege escalation", [input.metadata.name, container.name])
}

deny contains msg if {
  is_workload
  container := input.spec.template.spec.containers[_]
  not "ALL" in object.get(object.get(container.securityContext, "capabilities", {}), "drop", [])
  msg := sprintf("%s/%s must drop ALL Linux capabilities", [input.metadata.name, container.name])
}

deny contains msg if {
  is_workload
  readonly_components[component]
  container := input.spec.template.spec.containers[_]
  container.securityContext.readOnlyRootFilesystem != true
  msg := sprintf("%s/%s must use a read-only root filesystem", [input.metadata.name, container.name])
}

deny contains msg if {
  is_workload
  container := input.spec.template.spec.containers[_]
  not container.resources.requests.cpu
  msg := sprintf("%s/%s must define cpu requests", [input.metadata.name, container.name])
}

deny contains msg if {
  is_workload
  container := input.spec.template.spec.containers[_]
  not container.resources.requests.memory
  msg := sprintf("%s/%s must define memory requests", [input.metadata.name, container.name])
}

deny contains msg if {
  is_workload
  container := input.spec.template.spec.containers[_]
  not container.resources.limits.cpu
  msg := sprintf("%s/%s must define cpu limits", [input.metadata.name, container.name])
}

deny contains msg if {
  is_workload
  container := input.spec.template.spec.containers[_]
  not container.resources.limits.memory
  msg := sprintf("%s/%s must define memory limits", [input.metadata.name, container.name])
}
