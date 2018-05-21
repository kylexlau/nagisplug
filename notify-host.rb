#!/bin/env ruby 
# encoding: UTF-8

# How to test?
# notify-host.rb "$NOTIFICATIONTYPE$" "$HOSTNAME$" "$HOSTADDRESS$" "$HOSTSTATE$" "$HOSTOUTPUT$" "$LONGDATETIME$" "$HOSTNOTES$" "$CONTACTEMAIL$"
# notify-host.rb DOWNTIMESTART HD-CW-GDB01 172.25.27.129 OK OK 2011-11-01:10:00 liuxk@szlanyou.com 

$notification_type = ARGV[0]
$host_name = ARGV[1]
$host_address = ARGV[2]
$host_state = ARGV[3]
$host_output = ARGV[4]
$long_datetime = ARGV[5]
$contact_email = ARGV[6]
$host_notes = ARGV[7]


def notify_problem()
  subject = "主机宕机：主机#{$host_name}(#{$host_address})当前状态为#{$host_state}"
  body = "各位好：\n\n主机#{$host_name}(#{$host_address})发生故障，当前状态为#{$host_state}，故障发生时间为#{$long_datetime}。\n\n当前监控输出为#{$host_output}。\n\n主机相关信息：#{$host_notes}"
  system("/bin/echo '#{body}' | /usr/bin/mutt -s '#{subject}' #{$contact_email}")
end

def notify_recovery()
  subject = "主机恢复：主机#{$host_name}(#{$host_address})当前状态为#{$host_state}"
  body ="各位好：\n\n主机#{$host_name}(#{$host_address})故障恢复，当前状态为#{$host_state}，故障恢复时间为#{$long_datetime}。\n\n监控输出为#{$host_output}。\n\n主机相关信息：#{$host_notes}"
  system("/bin/echo '#{body}' | /usr/bin/mutt -s '#{subject}' #{$contact_email}")
end

def notify_acknowledgement()
  subject = "主机通知：主机#{$host_name}(#{$host_address})故障管理工程师已经确认"
  body ="各位好：\n\n主机#{$host_name}(#{$host_address})故障已通知到管理工程师，工程师确认故障的时间为#{$long_datetime}。当前监控输出为#{$host_output}。\n\n主机相关信息：#{$host_notes}"
  system("/bin/echo '#{body}' | /usr/bin/mutt -s '#{subject}' #{$contact_email}")
end

def notify_flapping_start()
end

def notify_flapping_stop()
end

def notify_flapping_disabled()
end

def notify_downtime_start()
  subject = "计划停机：主机#{$host_name}(#{$host_address})从#{$long_datetime}开始计划停机。"
  body ="各位好：\n\n主机#{$host_name}(#{$host_address})从#{$long_datetime}开始计划停机。\n\n主机相关信息：#{$host_notes}"
  system("/bin/echo '#{body}' | /usr/bin/mutt -s '#{subject}' #{$contact_email}")
end

def notify_downtime_end()
  subject = "计划停机：主机#{$host_name}(#{$host_address})计划停机从#{$long_datetime}结束。"
  body ="各位好：\n\n主机#{$host_name}(#{$host_address})计划停机从#{$long_datetime}结束。\n\n主机相关信息：#{$host_notes}"
  system("/bin/echo '#{body}' | /usr/bin/mutt -s '#{subject}' #{$contact_email}")
end

def notify_downtime_cancelled()
  subject = "计划停机：管理员在#{$long_datetime}取消了主机#{$host_name}(#{$host_address})的计划停机。"
  body ="各位好：\n\n管理员在#{$long_datetime}取消了主机#{$host_name}(#{$host_address})的计划停机。\n主机相关信息：#{$host_notes}"
  system("/bin/echo '#{body}' | /usr/bin/mutt -s '#{subject}' #{$contact_email}")
end

case $notification_type
when "PROBLEM"
    notify_problem
when "RECOVERY"
    notify_recovery
when "ACKNOWLEDGEMENT"
    notify_acknowledgement
when "FLAPPINGSTART"
    notify_flapping_start
when "FLAPPINGSTOP"
    notify_flapping_stop
when "FLAPPINGDISABLED"
    notify_flapping_disabled
when "DOWNTIMESTART"
    notify_downtime_start
when "DOWNTIMEEND"
    notify_downtime_end
when "DOWNTIMECANCELLED"
    notify_downtime_cancelled
end
