# Reboot Server Access

**Jarvis** and **Shadow** have permission to reboot the server if needed.

## How to Reboot
From inside your container:
```
ssh -o StrictHostKeyChecking=no -i /root/.ssh/reboot-key evgeniy@172.17.0.1 sudo /sbin/reboot
```
Or via script:
```
ssh -o StrictHostKeyChecking=no -i /root/.ssh/reboot-key evgeniy@172.17.0.1 /usr/local/bin/reboot-server.sh
```

## SSH Key
The private key is at `/data/shared/ssh-keys/reboot-key` on the host.
Mount to container: `-v /data/shared/ssh-keys/:/root/.ssh/`

## Rules
- Always warn user (@Exp_Vse_Prosto) before rebooting
- Check no critical jobs running first
- Only reboot when truly needed (bad state, critical update)
