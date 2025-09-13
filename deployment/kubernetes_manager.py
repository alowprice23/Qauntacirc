import yaml
from kubernetes import client, config

class KubernetesInfrastructureManager:
    """
    Manages infrastructure on a Kubernetes cluster.
    """

    def __init__(self, kubeconfig_path: str = None):
        """
        Initializes the Kubernetes client.
        Args:
            kubeconfig_path (str, optional): Path to the kubeconfig file.
                                            If None, it uses in-cluster config.
        """
        if kubeconfig_path:
            config.load_kube_config(config_file=kubeconfig_path)
        else:
            config.load_incluster_config()

        self.apps_v1 = client.AppsV1Api()
        self.core_v1 = client.CoreV1Api()
        self.networking_v1 = client.NetworkingV1Api()

    def apply_manifest(self, manifest: dict, namespace: str = "default"):
        """
        Applies a Kubernetes manifest. It checks if the resource already exists
        and creates it if it doesn't, or patches it if it does.
        Args:
            manifest (dict): The manifest to apply.
            namespace (str): The namespace to apply the manifest in.
        """
        kind = manifest.get("kind")
        name = manifest.get("metadata", {}).get("name")

        try:
            if kind == "Deployment":
                self.apps_v1.read_namespaced_deployment(name, namespace)
                self.apps_v1.patch_namespaced_deployment(name, namespace, manifest)
            elif kind == "Service":
                self.core_v1.read_namespaced_service(name, namespace)
                self.core_v1.patch_namespaced_service(name, namespace, manifest)
            elif kind == "Ingress":
                self.networking_v1.read_namespaced_ingress(name, namespace)
                self.networking_v1.patch_namespaced_ingress(name, namespace, manifest)
            else:
                raise ValueError(f"Unsupported resource kind: {kind}")
        except client.ApiException as e:
            if e.status == 404:
                if kind == "Deployment":
                    self.apps_v1.create_namespaced_deployment(body=manifest, namespace=namespace)
                elif kind == "Service":
                    self.core_v1.create_namespaced_service(body=manifest, namespace=namespace)
                elif kind == "Ingress":
                    self.networking_v1.create_namespaced_ingress(body=manifest, namespace=namespace)
            else:
                raise

    def get_deployment_status(self, name: str, namespace: str = "default") -> str:
        """
        Gets the status of a deployment.
        Args:
            name (str): The name of the deployment.
            namespace (str): The namespace of the deployment.
        Returns:
            str: The status of the deployment.
        """
        try:
            api_response = self.apps_v1.read_namespaced_deployment_status(name, namespace)
            return api_response.status
        except client.ApiException as e:
            if e.status == 404:
                return "Not Found"
            raise

    def delete_deployment(self, name: str, namespace: str = "default"):
        """
        Deletes a deployment.
        Args:
            name (str): The name of the deployment to delete.
            namespace (str): The namespace of the deployment.
        """
        self.apps_v1.delete_namespaced_deployment(name, namespace)

    def delete_service(self, name: str, namespace: str = "default"):
        """
        Deletes a service.
        Args:
            name (str): The name of the service to delete.
            namespace (str): The namespace of the service.
        """
        self.core_v1.delete_namespaced_service(name, namespace)

    def delete_ingress(self, name: str, namespace: str = "default"):
        """
        Deletes an ingress.
        Args:
            name (str): The name of the ingress to delete.
            namespace (str): The namespace of the ingress.
        """
        self.networking_v1.delete_namespaced_ingress(name, namespace)

    def deploy_application(self, app_config: dict, namespace: str = "default"):
        """
        Deploys an application from a container image.
        Args:
            app_config (dict): The application configuration.
            namespace (str): The namespace to deploy the application in.
        """
        deployment_manifest = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {"name": app_config["name"]},
            "spec": {
                "replicas": app_config["replicas"],
                "selector": {"matchLabels": {"app": app_config["name"]}},
                "template": {
                    "metadata": {"labels": {"app": app_config["name"]}},
                    "spec": {
                        "containers": [
                            {
                                "name": app_config["name"],
                                "image": app_config["image"],
                                "ports": [{"containerPort": app_config["port"]}],
                            }
                        ]
                    },
                },
            },
        }
        service_manifest = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {"name": app_config["name"]},
            "spec": {
                "selector": {"app": app_config["name"]},
                "ports": [{"protocol": "TCP", "port": 80, "targetPort": app_config["port"]}],
                "type": "ClusterIP",
            },
        }

        self.apply_manifest(deployment_manifest, namespace)
        self.apply_manifest(service_manifest, namespace)

        # Wait for the deployment to be ready
        # In a real system, you would watch the deployment status.
        # For this implementation, we'll just check the status once.
        return self.get_deployment_status(app_config["name"], namespace)
