# Kubernetes Manifests for QuantaCirc

## Managed by Helm

The Kubernetes manifests for this project are managed by the Helm chart located in the `/deployment/helm` directory. This approach allows for templatized, configurable, and repeatable deployments.

The files in this directory are provided as examples of the rendered templates from the Helm chart. **Do not edit these files directly.** Any changes should be made to the Helm chart values or templates.

To generate the latest version of these manifests, you can run the following command from the `/deployment/helm` directory:

```bash
helm template . > ../k8s/rendered-manifests.yaml
```
