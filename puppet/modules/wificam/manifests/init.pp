class wificam {    
  exec { 'clone-wificam-repo':
    unless => '/usr/bin/test -d /root/wificam/',
    command => '/usr/bin/git clone https://github.com/h-m-s/wificam.git',
  }
  exec { 'start-wificam-server':
    require => Exec['clone-wificam-repo'],
    cwd => '/root/wificam',
    command => '/usr/bin/nohup /usr/bin/python3 /root/wificam/wificam.py &',
  }
}
