Run as:

```shell
ansible-playbook --become -u $username --private-key $path_to_private_key -i ./hosts --limit "ci_ip" --extra-vars "ciuser=<user name> ci_user_pubkey=<path to public key>" ansible-playbook.yml
```
