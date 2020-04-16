This playbook is used to update Drupal 7 core.

It works by having a /var/www/drupal symlink that points to a download of the core, e.g. /var/www/drupal-7.6.7. 
When an update occurs it then downloads the new core, copies over the sites folder, etc. and then updates
the symlink
