{{/* Delegate all helpers to common-lib */}}
{{- define "devops-info-service.name" -}}
{{- include "common.name" . }}
{{- end }}

{{- define "devops-info-service.fullname" -}}
{{- include "common.fullname" . }}
{{- end }}

{{- define "devops-info-service.chart" -}}
{{- include "common.chart" . }}
{{- end }}

{{- define "devops-info-service.labels" -}}
{{- include "common.labels" . }}
{{- end }}

{{- define "devops-info-service.selectorLabels" -}}
{{- include "common.selectorLabels" . }}
{{- end }}

{{/*
Named template for common environment variables (bonus: DRY principle).
*/}}
{{- define "devops-info-service.envVars" -}}
- name: PORT
  value: {{ .Values.env | toJson | fromJson | first | dig "value" "5000" | quote }}
- name: HOST
  value: "0.0.0.0"
- name: DEBUG
  value: {{ .Values.debug | default "False" | quote }}
{{- end }}
