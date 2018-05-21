#!/usr/bin/env ruby
# encoding: UTF-8

# How to test:
# notify-service.rb "$NOTIFICATIONTYPE$" "$HOSTNAME$" "$HOSTADDRESS$" "$SERVICEDESC$" "$SERVICESTATE$" "$SERVICEOUTPUT$" "$LONGDATETIME$" "$HOSTNOTES$" "$CONTACTEMAIL$"
# notify-service.rb DOWNTIMESTART HD-CW-GDB01 172.25.27.129 CPU_LOAD OK OK 2011-11-01:10:00 liuxk@szlanyou.com 主机所属系统为DCS

$notification_type = ARGV[0]
$host_name = ARGV[1]
$host_address = ARGV[2]
$service_desc = ARGV[3]
$service_state = ARGV[4]
$service_output = ARGV[5]
$long_datetime = ARGV[6]
$contact_email = ARGV[7]
$host_note = ARGV[8]

def notify_problem ()
  subject = "故障 (服务)：主机#{$host_name} (#{$host_address})的服务#{$service_desc}当前状态为#{$service_state}"
  body = "各位好：\n\n主机#{$host_name} (#{$host_address})的服务#{$service_desc}发生故障，当前状态为#{$service_state}，故障发生时间为#{$long_datetime}。\n\n控详细输出为#{$service_output}。\n\n主机相关信息：#{$host_note}"
  system ("/bin/echo '#{body}' | /usr/bin/mutt -s '#{subject}' #{$contact_email}")
end

def notify_recovery ()
  subject = "恢复 (服务)：主机#{$host_name} (#{$host_address})的服务#{$service_desc}当前状态为#{$service_state}"
  body = "各位好：\n\n主机#{$host_name} (#{$host_address})的服务#{$service_desc}故障已经恢复，当前状态为#{$service_state}，故障恢复时间为#{$long_datetime}。\n\n监控详细输出为#{$service_output}。\n\n主机相关信息：#{$host_note}"
  system ("/bin/echo '#{body}' | /usr/bin/mutt -s '#{subject}' #{$contact_email}")
end

def notify_acknowledgement ()
  subject = "通知 (服务)：主机#{$host_name} (#{$host_address})的服务#{$service_desc}故障管理工程师已经确认"
  body = "各位好：\n\n主机#{$host_name} (#{$host_address})的服务#{$service_desc}故障已经通知到管理工程师，工程师确认故障的时间是#{$long_datetime}。\n\n当前监控详细输出为#{$service_output}。\n\n主机相关信息：#{$host_note}"
  system ("/bin/echo '#{body}' | /usr/bin/mutt -s '#{subject}' #{$contact_email}")
end

def notify_flapping_start ()
end

def notify_flapping_stop ()
end

def notify_flapping_disabled ()
end

def notify_downtime_start ()
  subject = "停机通知：主机#{$host_name} (#{$host_address})的服务#{$service_desc}从#{$long_datetime}开始停机通知。"
  body ="各位好：\n\n主机#{$host_name} (#{$host_address})的服务#{$service_desc}从#{$long_datetime}开始停机通知。\n\n主机相关信息为：#{$host_note}"
  system ("/bin/echo '#{body}' | /usr/bin/mutt -s '#{subject}' #{$contact_email}")
end

def notify_downtime_end ()
  subject = "停机通知：主机#{$host_name} (#{$host_address})的服务#{$service_desc}停机通知从#{$long_datetime}结束。"
  body ="各位好：\n\n主机#{$host_name} (#{$host_address})的服务#{$service_desc}停机通知从#{$long_datetime}结束。\n\n主机相关信息为：#{$host_note}"
  system ("/bin/echo '#{body}' | /usr/bin/mutt -s '#{subject}' #{$contact_email}")
end

def notify_downtime_cancelled ()
  subject = "停机通知：管理员在#{$long_datetime}取消了主机#{$host_name} (#{$host_address})的服务#{$service_desc}的停机通知。"
  body ="各位好：\n\n管理员在#{$long_datetime}取消了主机#{$host_name} (#{$host_address})的服务#{$service_desc}的停机通知。取消停机时间为#{$long_datetime}\n\n主机相关信息为：#{$host_note}"
  system ("/bin/echo '#{body}' | /usr/bin/mutt -s '#{subject}' #{$contact_email}")
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
