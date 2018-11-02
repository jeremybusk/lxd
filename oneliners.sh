for i in $(lxc ls --format=json | jq -r '.[].name'); do lxc delete --force $i; done
