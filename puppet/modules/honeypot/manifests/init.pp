class honeypot {    
  exec { 'apt-update':
    command => '/usr/bin/apt-get update',
  }
  package { 'git':
    require => Exec['apt-update'],
    ensure => installed,
  }
  package { 'python3-pip':
    require => Exec['apt-update'],
    ensure => installed,
  }
  exec {'pip3-docker':
    require => Package['python3-pip'],
    command => '/usr/bin/pip3 install docker',
  }
  exec {'log-dir':
    unless => '/usr/bin/test -d /var/log/hms/',
    command => '/bin/mkdir -p /var/log/hms/',
  }
  exec { 'clone-repo':
    unless => '/usr/bin/test -d /root/telnet-honeypot/',
    command => '/usr/bin/git clone https://github.com/h-m-s/telnet-honeypot.git',
  }
  exec { 'install-docker':
    unless => '/usr/bin/test -f /usr/bin/docker',
    command => '/usr/bin/wget -qO- https://get.docker.com/ | sh',
  }
  exec { 'build-container':
    require => Exec['install-docker'],
    command => '/usr/bin/docker build -t honeybox /root/telnet-honeypot/images/',
  }  
  exec { 'start-server':
    require => Exec['build-container'],
    cwd => '/root/telnet-honeypot',
    command => '/usr/bin/nohup /usr/bin/python3 /root/telnet-honeypot/telnet.py &',
  }
}
