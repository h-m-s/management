node default {
  include honeypot
  include wificam
}

node /honey-\d+/ {
  include honeypot
  include wificam
  }
