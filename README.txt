Full set-up & installation
--------------------------

https://www.raspberrypi.org/files/legacy/qsg.pdf

Language setting (initially: German):
    * Menu > Einstellungen > Raspberry Pi Configuration > Localisation
    * reboot
    
Update & Upgrade
----------------

sudo apt-get update
sudo apt-get upgrade

Camera
------

* insert the camera cable in the camera port (between the ethernet & HDMI ports), with the silver connectors facing the HDMI port
* boot up the Raspberry Pi
* sudo raspi-config
* enable camera & finish
* reboot
