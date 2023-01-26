
## offline

alias is-offline="sudo sh -c 'chat -t 1 -sv \'\' AT OK \'AT+CFUN=4\' OK < /dev/ttyUSB2 > /dev/ttyUSB2'"

## serving cell metrics
alias get-serving-metrics="sudo sh -c \'chat -t 1 -sv \'\' AT OK \'AT+QENG=\"servingcell\"\' OK < /dev/ttyUSB2 > /dev/ttyUSB2\' 2>&1 | grep -A1 TDD"

## check IMSI
alias check-imsi="sudo sh -c \'chat -t 1 -sv \'\' AT OK \'AT+CIMI\' OK < /dev/ttyUSB2 > /dev/ttyUSB2\'"

## check mode_pref; should be NR5G
alias check-mode="sudo sh -c \'chat -t 1 -sv \'\' AT OK \'AT+QNWPREFCFG=\"mode_pref\"\' < /dev/ttyUSB2 > /dev/ttyUSB2\' 2>&1"

