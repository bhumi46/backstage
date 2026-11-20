{{/* Resource name: fixed to the chart name. */}}
{{- define "bs.name" -}}
{{- .Chart.Name | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "bs.pgName" -}}
{{- printf "%s-postgresql" (include "bs.name" .) -}}
{{- end -}}

{{- define "bs.selectorLabels" -}}
app.kubernetes.io/name: {{ include "bs.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}

{{- define "bs.pgSelectorLabels" -}}
app.kubernetes.io/name: {{ include "bs.pgName" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}

{{- define "bs.commonLabels" -}}
app.kubernetes.io/part-of: {{ include "bs.name" . }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
helm.sh/chart: {{ printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" }}
{{/* backstage.io/kubernetes-id lets the Backstage Kubernetes plugin find these objects. */}}
backstage.io/kubernetes-id: {{ include "bs.name" . }}
{{- end -}}

{{- define "bs.labels" -}}
{{ include "bs.selectorLabels" . }}
app.kubernetes.io/version: {{ (.Values.image.tag | default .Chart.AppVersion) | trunc 63 | quote }}
{{ include "bs.commonLabels" . }}
{{- end -}}

{{- define "bs.pgLabels" -}}
{{ include "bs.pgSelectorLabels" . }}
{{ include "bs.commonLabels" . }}
{{- end -}}
