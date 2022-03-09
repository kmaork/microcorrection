function write(e) {
    writen(e + "\n")
}
function writen(e) {
    document.getElementById("responses").textContent += e,
    setTimeout(function() {
        $(".replresponsesouter").animate({
            scrollTop: $("#responses").height()
        }, 0)
    }, 0)
}
function write_io(e) {
    document.getElementById("ioresponses").textContent += e,
    setTimeout(function() {
        $(".ioresponsesouter").animate({
            scrollTop: $("#ioresponses").height()
        }, 0)
    }, 0)
}
function history_prev() {
    var e = $("#textentry").val()
      , t = chistory.pop();
    $("#textentry").val(t),
    chistory.unshift(e)
}
function history_next() {
    var e = $("#textentry").val()
      , t = chistory.shift();
    $("#textentry").val(t),
    chistory.push(e)
}
function dolist(e) {
    if (0 != e.length) {
        var t;
        do {
            if (t = e.shift(),
            void 0 == t)
                return;
            t = t.trim()
        } while (!t);if (t) {
            parse(t, 1);
            var n = function(t) {
                1 != t.state && 3 != t.state ? dolist(e) : cpu.update(n)
            };
            cpu.update(n)
        }
    }
}
function parse(e, t) {
    if (("" == e || void 0 == e) && (e = cpu.prev_cmd),
    0 == e.indexOf("#define")) {
        var n = e.split(" ");
        n.shift();
        var i = n.shift();
        return functions[i] = n.join(" "),
        write("> " + e),
        void write("  defined " + i + " to run " + functions[i])
    }
    if (-1 != e.indexOf(";")) {
        chistory[chistory.length - 1] == e || t || chistory.push(e),
        write("> " + e),
        cpu.prev_cmd = e,
        cpu.prev_cmd_time = Date.now();
        var o = e.split(";");
        return void dolist(o)
    }
    if (functions[e]) {
        chistory[chistory.length - 1] == e || t || chistory.push(e),
        cpu.prev_cmd = e,
        cpu.prev_cmd_time = Date.now();
        var o = e.split(";");
        return void parse(functions[e])
    }
    /^b /.test(e) || /^brea/.test(e) || (e = e.toLowerCase()),
    t || (cpu.prev_cmd = e,
    cpu.prev_cmd_time = Date.now()),
    cmd = e.split(" "),
    cpu.is_over || cpu.debugmode && (chistory[chistory.length - 1] == e || t || chistory.push(e),
    "solve" == cmd[0] ? (setTimeout(function() {
        $("#textentry").prop("disabled", !0),
        $("#io_wait").hide()
    }, 5),
    changemode(false),
    cpu._reset(function() {
        cpu._continue()
    })) : "help" == cmd[0] ? (write("> " + e),
    cpu._help()) : -1 != e.indexOf("=") ? (write("> " + e),
    cmd = e.replace("=", " = "),
    cmd = cmd.replace(/  /g, " ").split(" "),
    cpu._let(cmd)) : "_" + cmd[0]in cpu ? (write("> " + e),
    cpu["_" + cmd[0]](cmd)) : (write("> " + e),
    write("   Unknown Command.")),
    setTimeout(function() {
        focusTextEntry()
    }, 30),
    setTimeout(function() {
        focusTextEntry()
    }, 200),
    focusTextEntry(),
    cpu.reset_expirey())
}
function pad(e, t) {
    for ("number" == typeof e && (e = "" + e); e.length < t; )
        e = "0" + e;
    return e
}
function scrollToElement(e) {
    if (element = $(e),
    element.offset()) {
        var t = element.offset().top;
        t += $("#asmbox").scrollTop(),
        $("#asmbox").animate({
            scrollTop: t - 200
        }, 0)
    }
}
function randmsg() {
    var e = Math.random();
    return 1.99 > e ? "" : .992 > e ? "   yessir\n" : .994 > e ? "   as you command\n" : .996 > e ? "   NOU (just kidding)\n" : .998 > e ? "   fine...\n" : "   you want me to what?!\n"
}
function youwin(e, t) {
    window.onbeforeunload = function() {}
    ,
    isreal_glob = e,
    $("#gray_bg").show(),
    e ? ($("#youwin_outer h1 center").text("Door Unlocked"),
    $("#youwintext").text("Our operatives are entering the building. Go back to the world map to see what new warehouses they find.\nThe CPU completed in " + t + " instructions.\n\n"),
    $("#MYFORM").show(),
    $("#nextlevelbutton").click(function() {
        window.location = "/"
    }),
    $("#nextlevelbutton").val("Back to the map.")) : ($("#youwin_outer h1 center").text("Caught Unlock Interrupt"),
    window.in_tutorial ? (window.in_tutorial = !1,
    $("#youwintext").text("If you were not connected to the debug lock, the door would now be open.\nThe CPU completed in " + t + " cycles.")) : $("#youwintext").text('If you were not connected to the debug lock, the door would now be open.\nNow reset the CPU and type "solve" to run on the real lock, without the debugger.\n\nThe CPU completed in ' + t + " cycles."),
    $("#nextlevelbutton").click(function() {
        $("#youwin_outer").hide(),
        cpu._reset(),
        $("#gray_bg").hide()
    }),
    $("#nextlevelbutton").val("Back to the debugger.")),
    $("#youwin_outer").show(),
    $("#textentry").prop("disabled", !0)
}
function nowin() {
    $("#gray_bg").show(),
    $("#nowin_outer").show()
}
function endnowin() {
    $("#gray_bg").hide(),
    $("#nowin_outer").hide(),
    $("#textentry").prop("disabled", !1),
    $("#io_wait").hide(),
    changemode()
}
function show_debug_hi_msg() {
    write("Welcome to the lock debugger."),
    write("You are connected to a lock you managed to procure. You have"),
    write("  enabled the JTAG headers. This is not the real door lock."),
    write("  Use this mode to figure out what the lock is doing, and"),
    write("  then leave the debugger (upper left button) and enter"),
    write("  your input on the actual lock."),
    write("If you're not  sure what to do with this  interface, typing"),
    write('  "help" would be a good start.'),
    write('If you just want to see things work, type "continue".'),
    write(""),
    write("Connecting to remote lock ...")
}
function show_normal_hi_msg() {}
function changemode(reset=true) {
    cpu.debugmode = !cpu.debugmode,
    $("#responses").text(""),
    show_debug_hi_msg(),
    $("#whichmode pre").text("Leave Debug Mode"),
    $("#registers").show(),
    $(".replresponsesouter").show(),
    $(".textentrywrap").show(),
    $("#memorywatch").show(),
    $("#startandrestart").hide(),
    $("#io_wait").show();
    if (reset){
        write("Resetting CPU state.");
        cpu._reset();
    }

}
function decodehex(e) {
    for (var t = "", n = 0; n < e.length; n += 2)
        t += String.fromCharCode(parseInt(e.substr(n, 2), 16));
    return t
}
function hideheaders() {
    isheaders ? ($(".h2hide").hide(),
    $("#header").hide()) : ($(".h2hide").show(),
    $("#header").show()),
    isheaders = !isheaders
}
let manShown = false;
function focusTextEntry() {
    if (!manShown){
        $("#textentry").focus();
    }
}
function showmanual() {
    cpu.get("/get_manual", function(e) {
        "[insert story here]" != e.manual && ($("#info").text(e.manual),
        $("#gray_bg").show(),
        $("#info_outer").show());
        manShown = true;
        document.onkeypress = manualKeyHandler;
        $("#textentry").blur();
    });
}
function donemanual() {
    $("#gray_bg").hide(),
    $("#info_outer").hide();
    manShown = false;
    document.onkeypress = null;
    focusTextEntry();
}
function manualKeyHandler(e) {
    if (e.keyCode === 13) {
        donemanual();
    }
}
function togglebreakpoint(e) {
    var t = e.substr(4, 4);
    /170/.test($("#" + e).css("background-color").toString()) ? cpu._unbreak([null, t]) : cpu._break([null, t])
}
var prod = 1;
$(document).ready(function() {
    const te = $("#textentry");
    cpu.send("/cpu/is_alive", {}, function(e) {
        var t = "You already have another debugger window open. Starting the debugger will invalidate any existing debugger windows.";
        return prod && JSON.parse(e) && !confirm(t) ? (window.onbeforeunload = window.onunload = function() {}
        ,
        void (location.href = "/")) : ($("#memorybox").append("<div id='memory10000' style='display: none' class='topofregion'><pre>sdfsdfdfs</pre></div>"),
        show_debug_hi_msg(),
        prod && showmanual(),
        te.keydown(function(e) {
            if(13 === e.which){
                parse(te.val());
                te.val("");
                e.preventDefault();
            }
            38 == e.which && (e.preventDefault(),
            history_prev()),
            40 == e.which && (e.preventDefault(),
            history_next())
        }),
        $("#io_input_box").keypress(function(e) {
            13 == e.which && (cpu.io_response(),
            e.preventDefault())
        }),
        cpu.load(),
        void setTimeout(function() {
            var e = document.getElementById("asmbox").children;
            for (var t in e) {
                var n = e[t].id;
                if (n)
                    for (var i = parseInt(n.substr(4, 16), 16), o = 0; 6 > o; o++)
                        cpu.div_insns[i + o] = n
            }
        }, 10))
    })
});
var chistory = []
  , functions = {}
  , the_thing_width = null
  , cpu = {
    expirey1: null,
    expirey2: null,
    first_um: !0,
    is_over: !1,
    prev_instr: null,
    prev_cmd: "help",
    prev_cmd_time: 0,
    update_stopper: null,
    level: null,
    debugmode: !0,
    registers: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    memory: {},
    gaps: [[0, 1048576]],
    div_insns: {},
    win_input: [],
    tracking: [0, 1],
    reset_expirey: function() {
        clearTimeout(cpu.expirey1),
        clearTimeout(cpu.expirey2),
        cpu.expirey1 = setTimeout(function() {
            window.onbeforeunload = function() {}
            ,
            alert("Your session has expired."),
            window.location = "/"
        }, 15e5),
        cpu.expirey2 = setTimeout(function() {
            write("   +-------------------------------------------------+"),
            write("  /                                                 /|"),
            write(" /                                                 / |"),
            write("+-------------------------------------------------+  |"),
            write("|                     WARNING                     |  |"),
            write("|                                                 |  |"),
            write("|  Your session is going to reset in 10 minutes.  |  |"),
            write("|                                                 |  +"),
            write("|  You must make an action to reset the timeout.  | /"),
            write("|                                                 |/"),
            write("+-------------------------------------------------+")
        }, 9e5)
    },
    _help: function() {
        write(""),
        write("Valid commands:"),
        write("  Help - show this message"),
        write("  Solve - solve the level on the real lock"),
        write("  Reset - reset the state of the debugger"),
        write("  (C)ontinue - run until next breakpoint"),
        write("  (S)tep [count] - step [count] instructions"),
        write("  step Over / (N)ext - step until out or pc is next instruction"),
        write("  step Out / (F)inish - step until the function returns"),
        write("  (B)reak [expr] - set a breakpoint at address"),
        write("  (U)nbreak [expr] - remove a breakpoint"),
        write("  (R)ead [expr] [c] - read [c] bytes starting at [expr]"),
        write("  track [reg] - track the given register in memory"),
        write("  untrack [reg] - removes the tracking of the given register"),
        write("  (L)et [reg]/[addr] = [expr] - write to register or memory"),
        write("  Breakpoints - show a list of breakpoints"),
        // write("  Insncount - count number of CPU cycles executed"),
        write("  Manual - show the manual for this page"),
        write(""),
        write("Scripting commands:"),
        write('  #define name [commands] - alias "name" to run [commands].'),
        write("  command;command - run first command, then second comamnd."),
        write(""),
        write("List of types:"),
        write("  [reg] := 'r' followed by a number 0-15"),
        write("  [addr] := base-16 integer or label name (e.g., 'main')"),
        write("  [expr] := [reg] or [addr] or"),
        write("            [expr]+[expr] or [expr]-[expr]"),
        write("")
    },
    send: function(e, t, n, i) {
        $("#textentry").prop("disabled", !0),
        $.ajax({
            url: e,
            type: "POST",
            dataType: "json",
            contentType: "application/json",
            data: JSON.stringify(i ? t : {
                body: t
            })
        }).fail(function() {
            $("#textentry").prop("disabled", !1),focusTextEntry(),
            cpu.debugmode && write("Error; connection to lock has dropped.")
        }).done(function(e) {
            $("#textentry").prop("disabled", !1),focusTextEntry(),
            e.data && (1 == e.data.success ? writen(randmsg()) : 0 == e.data.success && write("   " + e.data.reason)),
            n && n(e)
        })
    },
    get: function(e, t) {
        $.ajax({
            url: e,
            type: "get",
            dataType: "json"
        }).fail(function() {
            cpu.debugmode && write("Error; connection to lock has dropped.")
        }).done(function(e) {
            t && t(e)
        })
    },
    load: function() {
        cpu.send("/cpu/load", {}, function() {
            cpu.send("/cpu/reset/" + (cpu.debugmode ? "debug" : "nodebug"), {}, function() {
                write("Connected. Have fun!"),
                write(""),
                write(""),
                cpu.update(),
                cpu.get_breakpoints()
            })
        })
    },
    update_registers: function(e) {
        var t = ""
          , n = cpu.registers;
        cpu.registers = e;
        for (var i = 0; 4 > i; i++) {
            for (var o = "", r = 0; 4 > r; r++) {
                var s = i + r == 0 || n[4 * i + r] == e[4 * i + r] ? "<span id='reg" + (4 * i + r) + "' class='unchangedregister'>" : "<span id='reg" + (4 * i + r) + "'class='changedregister'>"
                  , a = "r" + pad("" + (4 * i + r), 2);
                "r00" == a && (a = "pc "),
                "r01" == a && (a = "sp "),
                "r02" == a && (a = "sr "),
                "r03" == a && (a = "cg "),
                o += a + " " + s + pad(e[4 * i + r].toString(16), 4) + "</span>" + (3 != r ? "  " : "")
            }
            t += "<pre>" + o + "</pre>"
        }
        $("#registers").html(t),
        $(".tipsy").remove(),
        $(".pointedat").attr("class", "");
        var u = "";
        1 & e[2] && (u += "C"),
        2 & e[2] && (u += "Z"),
        4 & e[2] && (u += "N"),
        256 & e[2] && (u += "V"),
        16 & e[2] && (u = "CPUOFF"),
        32768 & e[2] && (u = "INT " + ((32512 & e[2]) >> 8)),
        $("#reg2").tipsy({
            fade: !1,
            gravity: "n",
            fallback: u
        });
        for (var r = 4; 16 > r; r++)
            $("#reg" + r).tipsy({
                fade: !1,
                gravity: "n",
                fallback: "" + e[r]
            });
        for (var l, r = 0; 16 > r; r++)
            -1 == cpu.tracking.indexOf(r) && ($("#r" + pad(r, 2) + "line").hide(),
            $("#r" + pad(r, 2) + "name").hide());
        var c = {};
        for (var p in cpu.tracking) {
            p = cpu.tracking[p];
            var d = $("#memorylocation" + pad(e[p].toString(16), 4))
              , f = d.offset();
            if (f) {
                var h = $("#memorybox").offset()
                  , g = $("#memorybox").scrollTop()
                  , m = $("#memorybox").width()
                  , y = d.height()
                  , v = d.height()
                  , b = Math.floor(e[p] / 8);
                b in c ? c[b]++ : c[b] = 0,
                $("#r" + pad(p.toString(), 2) + "line").css({
                    position: "absolute",
                    top: f.top - h.top + y + g,
                    left: f.left - h.left + v,
                    width: h.left + m - f.left - v - 50 + "px",
                    height: "1px",
                    display: ""
                }),
                f.top == l && (f.top += y),
                l = f.top;
                var w = 25;
                $("#r" + pad(p.toString(), 2) + "name").css({
                    position: "absolute",
                    top: f.top - h.top + g,
                    left: m - 50 - w * Math.floor(c[b] / 2) + "px",
                    display: ""
                }),
                d.attr("class", "pointedat")
            } else
                $("#r" + pad(p.toString(), 2) + "line").css({
                    display: "none"
                }),
                $("#r" + pad(p.toString(), 2) + "name").css({
                    display: "none"
                })
        }
    },
    show_running_instr: function(e) {
        cpu.prev_instr && ($("#insn" + pad(cpu.prev_instr.toString(16), 4)).css("color", "#fff"),
        $("#insn" + pad(cpu.prev_instr.toString(16), 4)).css("font-weight", "")),
        scrollToElement("#insn" + pad(e.toString(16), 4)),
        cpu.prev_instr = e,
        $("#insn" + pad(e.toString(16), 4)).css("color", "red"),
        $("#insn" + pad(e.toString(16), 4)).css("font-weight", "bold")
    },
    a: 0,
    b: 0,
    doit: {},
    write_memory_line: function(e, t) {
        for (var n in cpu.gaps) {
            var i = cpu.gaps[n];
            if (i[0] <= e && e < i[1]) {
                e + t < i[1] && (cpu.gaps.push([e, i[1]]),
                65536 > e + t && (cpu.doit[e + t] = function() {
                    var n = cpu.addIfNeeded(e + t, t);
                    n.text(pad((e + t).toString(16), 4) + ":   *")
                }
                )),
                i[0] + t == e ? cpu.gaps.splice(n, 1) : i[1] = e;
                break
            }
        }
        var o = [];
        o.push(pad(e.toString(16), 4) + ":  ");
        for (var r = "   ", n = e; e + t > n; n++) {
            n % 2 == 0 && o.push(" ");
            var s = cpu.memory[n] || 0
              , a = document.createElement("span");
            a.id = "memorylocation" + pad(n.toString(16), 4),
            a.textContent = pad(s.toString(16), 2),
            o.push(a),
            r += s >= 32 && 127 >= s ? "&#x" + s.toString(16) + ";" : "."
        }
        o.push(r + "\n"),
        65536 != e && (cpu.doit[e] = function() {
            var n = cpu.addIfNeeded(e, t);
            n.html(o)
        }
        )
    },
    addIfNeeded: function(e, t) {
        var n = $("#memory" + pad(e.toString(16), 4) + " pre");
        if (0 == n.length) {
            var i = pad(e.toString(16), 4);
            n = $("<div id='memory" + i + "' class='topofregion usedmemory'></div>");
            var o = $("#memory" + pad((e - t).toString(16), 4));
            if (o.length)
                n.removeClass("topofregion"),
                o.after(n);
            else {
                var r = $("#memorybox div.topofregion");
                for (var s in r) {
                    var a = $(r[s])
                      , u = parseInt(a.attr("id").substr(6), 16);
                    if (u > e) {
                        u - t == e && a.removeClass("topofregion"),
                        a.before(n);
                        break
                    }
                }
            }
            var l = $("<pre/>");
            n.append(l),
            n = l
        }
        return n
    },
    updatememory: function(e) {
        for (var t = 0; t < e.length; t += 36) {
            for (var n = e.substr(t, 4), i = e.substr(t + 4, 32), o = parseInt(n, 16), r = 0; 32 > r; r += 2)
                if (newval = parseInt(i.substr(r, 2), 16),
                cpu.memory[o + r / 2] != newval) {
                    if (cpu.div_insns[o + r / 2] && 0 == cpu.first_um && o + r / 2 > 48) {
                        var s = "#" + cpu.div_insns[o + r / 2];
                        $(s + " pre").hide(),
                        $(s).append("<pre class='removeme'>    [overwritten]</pre>")
                    }
                    cpu.memory[o + r / 2] = newval
                }
            null === the_thing_width && (the_thing_width = $("#memorybox").width()),
            the_thing_width > 600 ? cpu.write_memory_line(65520 & parseInt(n, 16), 16) : (cpu.write_memory_line(65528 & parseInt(n, 16), 8),
            cpu.write_memory_line(8 + parseInt(n, 16) & 65528, 8))
        }
        for (var a in cpu.doit)
            cpu.doit[a]();
        $(".usedmemory").css("font-family", "monospace"),
        cpu.doit = {},
        cpu.first_um = !1
    },
    do_update: function(e) {
        if ("" + e.isdebug != "" + cpu.debugmode)
            return void changemode();
        if (e.new_output && write_io(decodehex(e.new_output)),
        e.updatememory && cpu.updatememory(e.updatememory),
        e.regs && (cpu.update_registers(e.regs),
        cpu.show_running_instr(e.regs[0]),
        2 != e.state || cpu.debugmode || e.advanced || nowin()),
        e.reason && (write(e.reason),
        (cpu.update_stopper != null && cpu.update_stopper.stop())),
        e.alert && alert(e.alert),
        e.insn) {
            var hexInsn = e.insn.toString(16).padStart(4, '0');
            $("#insnbytes").text(`${hexInsn}:  ${e.insn_bytes.match(/.{4}/g).join(' ')}`);
            $("#insndecoded").text(e.disasm);
        }
        return 1 != e.state && (cpu.update_stopper != null && cpu.update_stopper.stop(),
        cpu.update_stopper = null),
        "4" == e.state && ($("#textentry").prop("disabled", !0),
        cpu.debugmode && (write("   [    console awaiting input    ]"),
        write("   [ automatically set breakpoint ]"),
        write("   [     press c to continue.     ]")),
        $("#gray_bg").show(),
        $("#io_outer").show(),
        $("#io_output_box pre").text($("#ioresponses").text()),
        $("#io_input_box").focus()),
        e.advanced ? youwin("win" == e.advanced, e.advanced_steps) : void 0
    },
    update: function(e, doneCallback=null) {
        cpu.get("/cpu/snapshot?x=" + (new Date).getTime(), function(t) {
            e && e(t),
            cpu.do_update(t),
            focusTextEntry();
            if(doneCallback){
                doneCallback();
            }
        })
    },
    io_response: function() {
        var e = $("#io_input_box").val();
        if ($("#io_check_box").is(":checked")) {
            var t = /^([0-9a-fA-F ]+)$/
              , n = e.match(t);
            if (!n)
                return void alert("Invalid characters in hex input");
            if (e = e.replace(/[^0-9a-fA-F]/g, ""),
            e.length % 2 != 0)
                return void alert("Hex input must have an even number of characters")
        } else {
            for (var i = "", o = 0; o < e.length; o++)
                i += e.charCodeAt(o).toString(16);
            e = i
        }
        cpu.win_input.push(e),
        cpu.send("/cpu/send_input", {
            body: e
        }, function(e) {
            return null === e.success ? void alert("Something went wrong sending input to the debugger. Please try again.") : (cpu.updateInterval(300),
            focusTextEntry(),
            $("#textentry").prop("disabled", !1))
        }, 1),
        $("#io_outer").hide(),
        $("#gray_bg").hide(),
        $("#io_input_box").val("")
    },
    io_wait: function() {
        $("#gray_bg").hide(),
        $("#io_outer").hide(),
        write("Console expects input. Press c to provide it."),
        $("#textentry").prop("disabled", !1),
        focusTextEntry()
    },
    make_breakpoint: function(e) {
        $("#insn" + e).css("background", "#00a"),
        $("#insn" + e).css("font-weight", "bold")
    },
    get_breakpoints: function() {
        cpu.get("/cpu/dbg/events?x=" + (new Date).getTime(), function(e) {
            for (var t in e.data.events)
                0 == e.data.events[t] && (cpu.debugmode ? cpu.make_breakpoint(t) : ($("#insn" + cpu.to_addr(t)).css("font-weight", ""),
                $("#insn" + cpu.to_addr(t)).css("background", "")))
        })
    },
    instr_after: function(e) {
        e = cpu.to_addr(e),
        e = parseInt(e, 16) + 1;
        for (var t = 0; 80 > t; t++)
            if ($("#insn" + cpu.to_addr(e + t)).length)
                return cpu.to_addr(e + t)
    },
    to_addr: function(e) {
        if ("number" == typeof e)
            return pad(e.toString(16), 4);
        if (-1 != e.indexOf("+")) {
            var t = e.split("+");
            return pad((parseInt(cpu.to_addr(t.shift().trim()), 16) + parseInt(cpu.to_addr(t.join("+")), 16)).toString(16), 4)
        }
        if (-1 != e.indexOf("-")) {
            var t = e.split("-");
            return pad((parseInt(cpu.to_addr(t.shift().trim()), 16) - parseInt(cpu.to_addr(t.join("-")), 16)).toString(16), 4)
        }
        if (/^(0x)?[0-9a-fA-F]+$/.test(e))
            return /^0x/.test(e) && (e = e.substr(2),
            write("  You don't need to specify 0x; all numbers are entered in base 16 already.")),
            pad(e, 4);
        if ("r" == e.charAt(0) && e.length <= 3)
            return pad(cpu.registers[parseInt(e.substr(1))].toString(16), 4);
        if ("pc" == e)
            return pad(cpu.registers[0].toString(16), 4);
        if ("sp" == e)
            return pad(cpu.registers[1].toString(16), 4);
        if ("sr" == e)
            return pad(cpu.registers[2].toString(16), 4);
        if ("cg" == e)
            return pad(cpu.registers[3].toString(16), 4);
        var n = {};
        return $(".insnlabel").map(function() {
            var e = this.textContent;
            if ("...\n" != e && !/^\s*\./.test(e) && /</.test(e)) {
                var t = /<.*>/.exec(e)[0]
                  , i = e.trim().substr(0, 4);
                n[t] = parseInt(i, 16)
            }
        }),
        n["<" + e + ">"] ? pad(n["<" + e + ">"].toString(16), 4) : (write("   could not find label '" + e + "'; using 0000."),
        "0000")
    },
    _reset: function(e) {
        cpu.win_input = [],
        document.getElementById("ioresponses").textContent = "",
        $(".usedmemory").remove(),
        cpu.first_um = !0,
        cpu.gaps = [[0, 1048576]],
        cpu.memory = {};
        var t = {};
        for (var n in cpu.div_insns) {
            var i = cpu.div_insns[n];
            t[i] || (t[i] = 1,
            $("#" + i + " pre").show(),
            $(".removeme").remove())
        }
        $("#memory10000").addClass("topofregion"),
        cpu.send("/cpu/reset/" + (cpu.debugmode ? "debug" : "nodebug"), {}, function() {
            cpu.get_breakpoints(),
            cpu.update(),
            "function" == typeof e && e()
        })
    },
    updateInterval: function(delay=null) {
        if (typeof delay !== 'number') {
            delay = 500;
        }
        const stopper = {stop: ()=>{stopper.shouldStop = true}, shouldStop: false};
        function interval(e, stopper) {
            cpu.update(e, ()=>{if(!stopper.shouldStop){setTimeout(e => interval(e, stopper), 1e3);}});
        }
        null == cpu.update_stopper && (cpu.update_stopper = stopper,
        setTimeout(e => interval(e, stopper), delay))
    },
    step: function(e) {
        e ? "out" == e ? cpu.send("/cpu/dbg/step_out", {}, cpu.updateInterval
        ) : "over" == e ? cpu.send("/cpu/dbg/step_over", {}, cpu.updateInterval
        ) : cpu.send("/cpu/dbg/stepn/" + e, {}, cpu.updateInterval
        ) : cpu.send("/cpu/step", {}, function(e) {
            cpu.do_update(e)
        })
    },
    _breakpoints: function() {
        cpu.get("/cpu/dbg/events?x=" + (new Date).getTime(), function(e) {
            if (write("   ok"),
            write(""),
            e.data.events) {
                write("List of breakpoints currently set:");
                for (var t in e.data.events)
                    0 == e.data.events[t] && write("    " + t)
            } else
                write("No breakpoints currently set.")
        })
    },
    _finish: function() {
        cpu.step("out")
    },
    // _insncount: function() {
    //     cpu.get("/cpu/dbg/stepcount", function(e) {
    //         write("  The CPU has executed " + e.data.count + " cycles.")
    //     })
    // },
    _manual: function() {
        showmanual()
    },
    _next: function() {
        cpu.step("over")
    },
    _step: function(e) {
        cpu.step("in" == e[1] ? e[2] : "over" == e[1] ? "over" : "out" == e[1] ? "out" : e[1])
    },
    _in: function(e) {
        cpu.step(e[1])
    },
    _over: function() {
        cpu.step("over")
    },
    _out: function() {
        cpu.step("out")
    },
    _continue: function() {
        cpu.send("/cpu/dbg/continue", {}, cpu.updateInterval)
    },
    _break: function(e, t) {
        if (!e[1])
            return void write("   Please give an expression to break at.");
        return t || "once" == e[2] || "o" == e[2] ? void cpu.one_time_breakpoint(x[1]) : void cpu.send("/cpu/dbg/event", {
            data: {
                addr: cpu.to_addr(e[1]),
                event: 0
            }
        }, function(t) {
            t.data.success && cpu.make_breakpoint(cpu.to_addr(e[1]))
        })
    },
    _unbreak: function(e) {
        return e[1] ? void cpu.send("/cpu/dbg/event", {
            data: {
                addr: cpu.to_addr(e[1]),
                event: -1
            }
        }, function() {
            $("#insn" + cpu.to_addr(e[1])).css("font-weight", ""),
            $("#insn" + cpu.to_addr(e[1])).css("background", "")
        }) : void write("   Please give an expression to unbreak.")
    },
    _read: function(e) {
        if (!e[1])
            return void write("   Please give an expression to read the memory at.");
        var t = cpu.to_addr(e[1]);
        cpu.get("/cpu/dbg/memory/" + t + "?len=" + (parseInt(e[2], 16) + (15 - parseInt(e[2], 16) & 15) || 32), function(e) {
            for (var n = atob(e.raw), i = "", o = "  ", r = "  ", s = 0; s < n.length; s++)
                s % 2 == 0 && (o += " "),
                o += pad(n.charCodeAt(s).toString(16), 2),
                r += 32 <= n.charCodeAt(s) && n.charCodeAt(s) <= 127 ? String.fromCharCode(n.charCodeAt(s)) : ".",
                s % 8 == 7 && (i += "   " + pad((-7 + s + parseInt(t, 16)).toString(16), 4) + ":" + o + r + "\n",
                o = "  ",
                r = "  ");
            write(i)
        })
    },
    _track: function(e) {
        var t = ["pc", "sp", "sr", "cg"]
          , n = e[1];
        if ("r" == n.charAt(0) || -1 != t.indexOf(n)) {
            var n;
            n = parseInt(-1 != t.indexOf(n) ? t.indexOf(n) : n.substr(1))
        }
        -1 == cpu.tracking.indexOf(n) && (cpu.tracking.push(n),
        cpu.update_registers(cpu.registers))
    },
    _untrack: function(e) {
        var t = ["pc", "sp", "sr", "cg"]
          , n = e[1];
        if ("r" == n.charAt(0) || -1 != t.indexOf(n)) {
            var n;
            n = parseInt(-1 != t.indexOf(n) ? t.indexOf(n) : n.substr(1))
        }
        var i = cpu.tracking.indexOf(n);
        -1 != i && cpu.tracking.splice(i, 1),
        cpu.update_registers(cpu.registers)
    },
    _let: function(e) {
        if (("let" == e[0] || "l" == e[0]) && e.shift(),
        !e[1])
            return void write("   Please give a register or memory address, and expression to set it to.");
        e = e.filter(function(e) {
            return e
        });
        var t = e.shift();
        e.shift();
        var n = ["pc", "sp", "sr", "cg"];
        if ("r" == t.charAt(0) || -1 != n.indexOf(t)) {
            var i;
            i = parseInt(-1 != n.indexOf(t) ? n.indexOf(t) : t.substr(1));
            var o = cpu.to_addr(e.join(" "));
            cpu.send("/cpu/regs", {
                reg: i,
                val: parseInt(o, 16)
            }, function(e) {
                cpu.update_registers(e.data.regs),
                cpu.update()
            }, 1)
        } else {
            var i = cpu.to_addr(t)
              , o = cpu.to_addr(e.join(" "));
            cpu.send("/cpu/updatememory", {
                addr: parseInt(i, 16),
                val: parseInt(o, 16)
            }, function(e) {
                cpu.updatememory(e.updatememory),
                cpu.update()
            }, 1)
        }
    },
    _view: function() {
        cpu.get("/cpu/output", function(e) {
            write(("\n" + e.output).replace(/\n/g, "\n  | ") + "EOF\n\n")
        })
    }
};
cpu._r = cpu._read,
cpu._s = cpu._in,
cpu._i = cpu._in,
cpu._n = cpu._next,
cpu._f = cpu._finish,
cpu._o = cpu._out,
cpu._b = cpu._break,
cpu._u = cpu._unbreak,
cpu._c = cpu._continue,
cpu._l = cpu._let,
cpu._h = cpu._help;
var isreal_glob, isheaders = 1;
window.onbeforeunload = function() {
    return prod ? "Are you sure you want to leave? Your state will be lost." : void 0
}
,
window.onunload = function() {
    $.ajax({
        url: "/cpu/dbg/kill",
        async: !1,
        type: "POST",
        contentType: "application/json",
        data: JSON.stringify({
            body: {}
        })
    })
}
,
cpu.reset_expirey();
