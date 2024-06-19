node='' # insert nodename

helm repo add bitnami https://charts.bitnami.com/bitnami
helm install mongodb bitnami/mongodb-sharded --namespace mongo --create-namespace --values values-mongo.yaml --set nodeselector=${node}
