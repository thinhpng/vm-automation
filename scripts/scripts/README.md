# build_windows_binary.cmd
Used to build standalone Windows binary. Required [Nuitka](https://nuitka.net/) and, optionally, [UPX](https://upx.github.io/).

# Guest scripts examples
Those are examples of script to run before (--pre 'C:\start.cmd') and after (--post 'C:\stop.cmd') analysis on guest OS.
Can gather additional information about behavior (processes, files, registry, network activity etc.).
Must be placed on guest's filesystem.

# Sysinternals System Monitor (Sysmon)
Download: https://docs.microsoft.com/en-us/sysinternals/downloads/sysmon
Scripts:
* sysmon_pre.cmd
* sysmon_post.cmd

# NoVirusThanks Event Monitor Service
Download: https://www.novirusthanks.org/products/event-monitor-service/
Scripts:
* eventmon_pre.cmd
* eventmon_post.cmd

