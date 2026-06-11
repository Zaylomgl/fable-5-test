-- Catalogue initial (~40 produits typiques PME/MSP), volontairement restreint :
-- la qualité du mapping bat la couverture.
--
-- ⚠ AVANT IMPORT EN PROD : vérifier chaque paire (vendor, product) contre le
-- dictionnaire CPE officiel (https://nvd.nist.gov/products/cpe/search) — les
-- segments CPE réels divergent parfois du nom commercial (ex. Veeam).
-- Les entrées marquées TODO ci-dessous sont à confirmer en priorité.

INSERT OR IGNORE INTO products (vendor, product, display) VALUES
-- Réseau / sécurité périmétrique
('fortinet', 'fortios', 'Fortinet FortiOS'),
('fortinet', 'fortiproxy', 'Fortinet FortiProxy'),
('paloaltonetworks', 'pan-os', 'Palo Alto PAN-OS'),
('sonicwall', 'sonicos', 'SonicWall SonicOS'),
('cisco', 'ios', 'Cisco IOS'),
('cisco', 'ios_xe', 'Cisco IOS XE'),
('cisco', 'adaptive_security_appliance_software', 'Cisco ASA'),
('mikrotik', 'routeros', 'MikroTik RouterOS'),
('pfsense', 'pfsense', 'pfSense'),                          -- TODO vérifier vendor CPE (netgate ?)
('zyxel', 'usg_flex_firmware', 'Zyxel USG Flex'),           -- TODO vérifier
-- Virtualisation / hyperviseurs
('vmware', 'esxi', 'VMware ESXi'),
('vmware', 'vcenter_server', 'VMware vCenter'),
('proxmox', 'virtual_environment', 'Proxmox VE'),           -- TODO vérifier
('citrix', 'hypervisor', 'Citrix Hypervisor'),
-- Microsoft
('microsoft', 'windows_server_2019', 'Windows Server 2019'),
('microsoft', 'windows_server_2022', 'Windows Server 2022'),
('microsoft', 'windows_server_2025', 'Windows Server 2025'),
('microsoft', 'exchange_server', 'Microsoft Exchange Server'),
('microsoft', 'sql_server', 'Microsoft SQL Server'),
('microsoft', 'sharepoint_server', 'Microsoft SharePoint'),
-- Linux / infra
('canonical', 'ubuntu_linux', 'Ubuntu Linux'),
('debian', 'debian_linux', 'Debian Linux'),
('redhat', 'enterprise_linux', 'Red Hat Enterprise Linux'),
('vmware', 'spring_framework', 'Spring Framework'),
('apache', 'http_server', 'Apache HTTP Server'),
('f5', 'nginx', 'NGINX'),                                   -- TODO vérifier (nginx/nginx ?)
('haproxy', 'haproxy', 'HAProxy'),
('openbsd', 'openssh', 'OpenSSH'),
('openssl', 'openssl', 'OpenSSL'),
-- Sauvegarde / outils MSP
('veeam', 'veeam_backup_\&_replication', 'Veeam Backup & Replication'),  -- TODO vérifier l'échappement exact
('connectwise', 'screenconnect', 'ConnectWise ScreenConnect'),
('n-able', 'n-central', 'N-able N-central'),                -- TODO vérifier
('teamviewer', 'teamviewer', 'TeamViewer'),                 -- TODO vérifier (remote/full_client ?)
-- Collaboration / services exposés
('atlassian', 'confluence_server', 'Atlassian Confluence'),
('atlassian', 'jira_software', 'Atlassian Jira'),           -- TODO vérifier
('gitlab', 'gitlab', 'GitLab'),
('nextcloud', 'nextcloud_server', 'Nextcloud'),
('zimbra', 'collaboration', 'Zimbra Collaboration'),
('citrix', 'netscaler_application_delivery_controller', 'Citrix NetScaler ADC'),
('ivanti', 'connect_secure', 'Ivanti Connect Secure'),
('progress', 'moveit_transfer', 'Progress MOVEit Transfer');
