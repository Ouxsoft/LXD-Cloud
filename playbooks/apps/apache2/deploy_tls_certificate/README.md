This playbook will automatically deploy the certs inside the certs folder to the apache2 SSL cert directory and restart apache2 service.

For security purposes, it is best to generate a new certificate for each server. This playbook does not handle the generation; it only deploys the cert.
