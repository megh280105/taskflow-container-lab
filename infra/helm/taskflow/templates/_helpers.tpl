{{- define "taskflow.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "taskflow.fullname" -}}
{{- printf "%s-%s" .Release.Name (include "taskflow.name" .) | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "taskflow.labels" -}}
app.kubernetes.io/name: {{ include "taskflow.name" . }}
helm.sh/chart: {{ .Chart.Name }}-{{ .Chart.Version | replace "+" "_" }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end -}}

{{- define "taskflow.selectorLabels" -}}
app.kubernetes.io/name: {{ include "taskflow.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}

{{- define "taskflow.serviceAccountName" -}}
{{- $root := index . 0 -}}
{{- $component := index . 1 -}}
{{- printf "%s-%s" (include "taskflow.fullname" $root) $component | trunc 63 | trimSuffix "-" -}}
{{- end -}}
