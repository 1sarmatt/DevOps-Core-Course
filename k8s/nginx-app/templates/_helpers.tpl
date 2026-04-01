{{/* Delegate all helpers to common-lib */}}
{{- define "nginx-app.name" -}}
{{- include "common.name" . }}
{{- end }}

{{- define "nginx-app.fullname" -}}
{{- include "common.fullname" . }}
{{- end }}

{{- define "nginx-app.labels" -}}
{{- include "common.labels" . }}
{{- end }}

{{- define "nginx-app.selectorLabels" -}}
{{- include "common.selectorLabels" . }}
{{- end }}
