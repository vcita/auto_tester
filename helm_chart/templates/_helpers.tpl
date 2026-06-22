{{/* vim: set filetype=mustache: */}}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "autotester.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "autotester.labels" -}}
helm.sh/chart: {{ include "autotester.chart" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Expand the release name of the chart.
*/}}
{{- define "autotester.releaseName" -}}
{{- default .Release.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/*
Render envFrom for secrets unless explicitly disabled.
Each secret item is a map with fields:
  - name: <string>
  - as: <env|file> (optional, defaults to env)
  - referenced: <bool> (optional, defaults to true)
*/}}
{{- define "autotester.envFromForSecrets" -}}
{{- $release := .releaseName -}}
{{- $refs := list -}}
{{- range .secrets }}
  {{- $ref := .referenced | default true -}}
  {{- if and $ref (ne (.as | default "env") "file") -}}
    {{- $refs = append $refs (printf "%s-%s" $release .name) -}}
  {{- end -}}
{{- end -}}
{{- if gt (len $refs) 0 }}
envFrom:
{{- range $refs }}
  - secretRef:
      name: {{ . }}
      optional: false
{{- end }}
{{- end -}}
{{- end }}

{{/*
Build and render a single volumes: block by merging user-defined .volumes
with file-based secrets (referenced=true, as=file).
User volumes override on name collisions.
*/}}
{{- define "autotester.mergedVolumes" -}}
{{- $release := .releaseName -}}
{{- $userVolumes := .volumes | default (list) -}}
{{- $seen := dict -}}
{{- range $userVolumes }}
  {{- $_ := set $seen .name true -}}
{{- end -}}
{{- $secretVols := list -}}
{{- range .secrets }}
  {{- $ref := .referenced | default true -}}
  {{- if and $ref (eq (.as | default "env") "file") -}}
    {{- $vname := printf "sec-%s" .name -}}
    {{- if not (hasKey $seen $vname) -}}
      {{- $key := default .filename .name -}}
      {{- $vol := dict
          "name" $vname
          "secret" (dict
            "secretName" (printf "%s-%s" $release .name)
            "defaultMode" ((.defaultMode | default 444) | int)
            "items" (list (dict "key" $key "path" $key)) ) -}}
      {{- $secretVols = append $secretVols $vol -}}
    {{- end -}}
  {{- end -}}
{{- end -}}
{{- $total := add (len $userVolumes) (len $secretVols) -}}
{{- if gt $total 0 }}
volumes:
{{- range $userVolumes }}
  - {{- toYaml . | nindent 4 -}}
{{- end }}
{{- range $secretVols }}
  - name: {{ .name }}
    secret:
      secretName: {{ .secret.secretName }}
      defaultMode: {{ .secret.defaultMode }}
      items:
      {{- range .secret.items }}
        - key: {{ .key }}
          path: {{ .path }}
      {{- end }}
{{- end }}
{{- end -}}
{{- end }}

{{/*
Build and render a single volumeMounts: block by merging user-defined .volumeMounts
with mounts for file-based secrets (referenced=true, as=file).
User mounts override on name collisions.
*/}}
{{- define "autotester.mergedVolumeMounts" -}}
{{- $userMounts := .volumeMounts | default (list) -}}
{{- $seen := dict -}}
{{- range $userMounts }}
  {{- $_ := set $seen .name true -}}
{{- end -}}
{{- $secMounts := list -}}
{{- range .secrets }}
  {{- $ref := .referenced | default true -}}
  {{- if and $ref (eq (.as | default "env") "file") -}}
    {{- $name := printf "sec-%s" .name -}}
    {{- if not (hasKey $seen $name) -}}
      {{- $mp := required (printf "mountPath required for file secret '%s'" .name) .mountPath -}}
      {{- $secMounts = append $secMounts (dict "name" $name "mountPath" $mp "readOnly" true) -}}
    {{- end -}}
  {{- end -}}
{{- end -}}
{{- $total := add (len $userMounts) (len $secMounts) -}}
{{- if gt $total 0 }}
volumeMounts:
{{- range $userMounts }}
  - {{- toYaml . | nindent 4 -}}
{{- end }}
{{- range $secMounts }}
  - name: {{ .name }}
    mountPath: {{ .mountPath }}
    readOnly: {{ .readOnly }}
{{- end }}
{{- end -}}
{{- end }}
