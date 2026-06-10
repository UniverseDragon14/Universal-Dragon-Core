# Universal Dragon NOVA Pi5 Sync Guide v1.3

Generated: 2026-06-11 02:51:27

TERMUX SIDE:
1. Run: nova syncpack
2. When Pi5 is ON, copy pack:
   scp ~/nova-lang/backups/termux_to_pi5_sync_*.tar.gz aslam@192.168.1.80:/home/aslam/

PI5 SIDE:
1. SSH: ssh aslam@192.168.1.80
2. Extract:
   mkdir -p ~/nova-sync-preview
   tar -xzf ~/termux_to_pi5_sync_*.tar.gz -C ~/nova-sync-preview
   cd ~/nova-sync-preview/nova-lang
   bash pi5_install_nova.sh

TEST:
   nova version
   nova doctor
   nova backup
