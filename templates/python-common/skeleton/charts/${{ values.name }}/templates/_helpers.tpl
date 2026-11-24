{{/* Resource name: fixed to the chart name so other services can reach it as http://<name>. */}}
{{- define "svc.name" -}}
{{- .Chart.Name | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/* CloudNativePG cluster name; the operator creates the Secret "<name>-db-app". */}}
{{- define "svc.dbName" -}}
{{- printf "%s-db" (include "svc.name" .) -}}
{{- end -}}

{{- define "svc.selectorLabels" -}}
app.kubernetes.io/name: {{ include "svc.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}

{{/* backstage.io/kubernetes-id lets the Backstage Kubernetes plugin find these objects. */}}
{{- define "svc.labels" -}}
{{ include "svc.selectorLabels" . }}
app.kubernetes.io/version: {{ (.Values.image.tag | default .Chart.AppVersion) | trunc 63 | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
helm.sh/chart: {{ printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" }}
backstage.io/kubernetes-id: {{ include "svc.name" . }}
{{- end -}}

{{- define "svc.image" -}}
{{ .Values.image.repository }}:{{ .Values.image.tag | default .Chart.AppVersion }}
{{- end -}}

{{/* Env shared by the app and the migration Job. */}}
{{- define "svc.env" -}}
- name: PORT
  value: {{ .Values.containerPort | quote }}
- name: ALLOWED_HOSTS
  value: {{ printf "%s,%s.%s,%s.%s.svc,%s.%s.svc.cluster.local,localhost,127.0.0.1" (include "svc.name" .) (include "svc.name" .) .Release.Namespace (include "svc.name" .) .Release.Namespace (include "svc.name" .) .Release.Namespace | quote }}
{{- range $k, $v := .Values.env }}
- name: {{ $k }}
  value: {{ $v | quote }}
{{- end }}
{{- range $k, $v := .Values.secretEnv }}
- name: {{ $k }}
  valueFrom:
    secretKeyRef:
      name: {{ $v.secretName | replace "{db}" (printf "%s-app" (include "svc.dbName" $)) }}
      key: {{ $v.key }}
{{- end }}
{{- end -}}
