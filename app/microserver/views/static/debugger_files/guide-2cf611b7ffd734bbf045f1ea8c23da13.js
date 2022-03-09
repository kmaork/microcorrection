var guide=new Guideline.Guide("welcome");$(document).ready(function(){function e(t,n,i,o){var r=null,a=!1;return function(){return null===r&&(n&&$("#MYFORM").hide(),i&&$("#whichmode").click(changemode),o&&$("#insn4438").click(function(){togglebreakpoint(this.id),$("#insn4438").off("click")}),r=1,$("#textentry").off("keydown").keydown(function(n){13==n.which&&(t.test($("#textentry").val())?(parse($("#textentry").val()),$("#textentry").val(""),n.preventDefault(),a=1,e(/^YOU SHALL NOT PASS$/)()):($("#textentry").val(""),$(".wrongcmd").remove(),$("div.content h2").append("<span class='wrongcmd' style='color: red'>&nbsp;&nbsp;Wrong command</span>")))})),a}}function t(){var e=!1;return function(){return 0!=$("#io_outer").position().top&&setTimeout(function(){e=!0},300),e}}function n(e,t){var n,i=0,o=!1;return function(){return $("#io_wait").prop("disabled",!0),$("#io_check_box").prop("disabled",!0),i||(t&&$("#MYFORM").show(),n=cpu.io_response,cpu.io_response=function(){var t=$("#io_input_box").val();t!=e?($("#io_input_box").val(""),$(".wrongcmd").remove(),$("div.content h2").append("<span class='wrongcmd' style='color: red'>&nbsp;&nbsp;Wrong input</span>")):(cpu.io_response=n,n(),o=!0,$(".gl-bubble").remove())},i=1),o}}guide.on("start",function(){console.log("start"),window.in_tutorial=!0}),guide.on("complete",function(){}),guide.on("skip",function(){window.in_tutorial=!1,$("#textentry").off("keydown").keydown(function(e){13==e.which&&(parse($("#textentry").val()),$("#textentry").val(""),e.preventDefault()),38==e.which&&(e.preventDefault(),history_prev()),40==e.which&&(e.preventDefault(),history_next())})}),guide.on("realstart",function(){e(/^YOU SHALL NOT PASS$/)(),$(".insn").prop("onclick",""),$("#whichmode").prop("onclick","")});var i=guide.addPage("/cpu/debugger");i.addStep({type:"overlay",showContinue:!1,content:"<div style=''><h1>Welcome to the CPUCTF Debugger Tutorial</h1><p>This tutorial will step you through our debugger and explain how everything works by showing you how to beat this level. It is strongly recomended you go through it (it'll take less than 15 minutes, we promise), but is not required. You can always return to this tutorial if you choose not to by reloading the page. </p><button class='btn btn-large btn-primary btn-alpha-blue hide-button'><i class='icon-circle-arrow-right'></i> Show me the tutorial!</button><br/><a href='#' class='gl-skip'>I know what I'm doing -- just let me go!</a></div>"}),i.addStep({type:"overlay",showContinue:!0,continueAfter:3e3,content:"<div style=''><h1>Welcome!</h1><p style='font-size: 14px'>Scattered throughout the world in locked warehouses are briefcases filled with Cy Yombinator bearer bonds that could be worth billions comma billions of dollars. You will help steal the briefcases.</p><p>Cy Yombinator has cleverly protected the warehouses with Lockitall electronic lock devices. Lockitall locks are unlockable with an app. We've positioned operatives near each warehouse; each is waiting for you to successfully unlock the warehouse by tricking out the locks.</p><p>The Lockitall devices work by accepting Bluetooth connections from the Lockitall LockIT Pro app. We've done the hard work for you: we spent $15,000 on a development kit that includes remote controlled locks for you to practice on, and reverse engineered enough of it to build a primitive debugger.</p><p>Using the debugger, you'll be able to single step the lock code, set breakpoints, and examine memory on your own test instance of the lock. You'll use the debugger to find an input that unlocks the test lock, and then replay it to a real lock.</p></div>"}),i.addStep({title:"This is the disassembled object file.",content:"It has all of the instructions that the LockIT Pro will execute. Scroll around to view the instructions.",showAt:".asmbox",align:"right middle",continueWhen:"scroll .asmbox"}),i.addStep({title:"This is the memory viewer.",content:"It contains the contents of memory. Scroll through it too.",showAt:".memorybox",align:"right middle",continueWhen:"scroll .memorybox"}),i.addStep({title:"This is the debugger input.",content:"Enter commands here. Start by typing 'help'",showAt:".textentrywrap",align:"center top",continueWhen:e(/^(h|help)$/)}),i.addStep({title:"This is the debugger console.",content:"It contains the output to the commands you enter. Scroll back and read through the help.",showAt:".replresponsesouter",align:"left middle",continueWhen:"scroll .replresponsesouter"}),i.addStep({title:"Run the program.",content:'Type either "continue" or "c" to start.',showAt:".textentrywrap",align:"left middle",continueWhen:e(/^(c|continue)$/)}),i.addStep({title:"This is the IO console.",content:"Here we see the output of the lock. In this case, it wants us to enter the password.",showAt:"#io_output_box",align:"center bottom",continueAfter:3e3,waitToShow:t()}),i.addStep({title:"This is the IO console.",content:'You can enter input to the console here, which the lock will be able to read. Start by entering "test" and clicking "send".',showAt:"#io_input_box",align:"center bottom",continueWhen:n("test")}),i.addStep({title:"Continue the CPU",content:'Press "c" to continue.',showAt:".textentrywrap",align:"center top",continueWhen:e(/^(c|continue)$/)}),i.addStep({title:"CPU output goes here too.",content:"Notice that the output of the CPU is shown here as well.  In this case, the password you entered was not correct",showAt:".ioresponsesouter",align:"left middle",continueAfter:3e3}),i.addStep({title:"Notice the CPU is off.",content:"This means the program finished executing.",showAt:".replresponsesouter",align:"left middle",continueAfter:3e3}),i.addStep({title:"Reset the CPU",content:"Let's try again, but this time step through the CPU to see what's going on. Type \"reset\" to reset the CPU state.",showAt:".textentrywrap",align:"left middle",continueWhen:e(/^reset$/)}),i.addStep({title:"Set a Breakpoint",content:'In order to see what\'s going on, we are going to set a breakpoint. This stops CPU execution when a specific location is reached. In this case, type "break main" to break at the function called "main".',showAt:".textentrywrap",align:"left middle",continueWhen:e(/^(b|break) main$/)}),i.addStep({title:"Resume the CPU",content:'Now that the breakpoint is set, type "c" to continue.',showAt:".textentrywrap",align:"left middle",continueWhen:function(){return e(/^(c|continue)$/,0,0,1)}()}),i.addStep({title:"The CPU is paused.",content:"You can see a breakpoint was set by the blue background. Remove the breakpoint by clicking the instruction, so the next time you run the program, the CPU won't stop here. You can add any breakpoint by clicking on an instruction (but not during this tutorial).",showAt:".asmbox",align:"right middle",continueWhen:"click #insn4438"}),i.addStep({title:"These are the registers.",content:"They show the state of the CPU at the time of the breakpoint.",showAt:"#registers",align:"center bottom",continueAfter:3e3}),i.addStep({title:"This is the program counter.",content:"It shows the address of the currently running instruction. Notice that it is shown in base 16. All numbers in the debugger are base 16.",showAt:"#reg0",align:"center bottom",continueAfter:3e3}),i.addStep({title:"This is the current instruction.",content:"The instruction at the program counter is shown here. You can also see it in the instruction listing on the left.",showAt:"#insndecoded",align:"center bottom",continueAfter:3e3}),i.addStep({title:"Step the CPU.",content:'Let\'s run the program one step. Type "step" or "s".',showAt:".textentrywrap",align:"left middle",continueWhen:e(/^(s|step)$/)}),i.addStep({title:"We ran one instruction",content:"The instruction we're on (the red one) is one after where the breakpoint was set. We moved one step.",showAt:".asmbox",align:"right middle",continueAfter:3e3}),i.addStep({title:"Step Many.",content:'Stepping one instruction at a time can be very slow. Type "step 5a" to step a bunch of instructions. Remember: this number is base 16 -- we\'re actually going to step 94 instructions.',showAt:".textentrywrap",align:"left middle",continueWhen:e(/^(s|step) 5a$/)}),i.addStep({title:"This is the INT function",content:"This is how the lock interacts with the user. By issuing interrupts, the lock can put characters, request input, or do just about anything else.",showAt:".asmbox",align:"right middle",continueAfter:3e3}),i.addStep({title:"Partial output",content:"The partial output of the program is shown here.",showAt:".ioresponsesouter",align:"left middle",continueAfter:3e3}),i.addStep({title:"Continue again.",content:'Type "continue" to run until you are asked for the password.',showAt:".textentrywrap",align:"left middle",continueWhen:e(/^(c|continue)$/)}),i.addStep({title:"You still don't know the password.",content:"But let's enter a password to see what's going on. Put \"test\" again.",showAt:"#io_input_box",align:"center bottom",waitToShow:t(),continueWhen:n("test")}),i.addStep({title:"Stepping out.",content:'You can step out of the current function by typing "out".  This runs until it encounters the next "ret" (return) instruction. All functions end with "ret" instructions to return them to the caller.',showAt:".textentrywrap",align:"left middle",continueWhen:e(/^out$/)}),i.addStep({title:"Stepping out.",content:'You\'re not yet at the main level, step out can be abbreviated "f" for "finish": use that instead.',showAt:".textentrywrap",align:"left middle",continueWhen:e(/^(f|finish)$/)}),i.addStep({title:"Stepping out.",content:"Do it one more time.",showAt:".textentrywrap",align:"left middle",continueWhen:e(/^(out|f|finish)$/)}),i.addStep({title:"The check_password function looks interesting.",content:"",showAt:".asmbox",align:"right middle",continueAfter:3e3}),i.addStep({title:"Let's break there",content:'Set a breakpoint there by typing "break check_password"',showAt:".textentrywrap",align:"left middle",continueWhen:e(/^(b|break) check_password$/)}),i.addStep({title:"Run to the breakpoint",content:'Type "c" or "continue"',showAt:".textentrywrap",align:"left middle",continueWhen:e(/^(c|continue)$/)}),i.addStep({title:"This looks promising.",content:"It looks like this is what checks your password to see if it's correct.",showAt:".asmbox",align:"right middle",continueAfter:3e3}),i.addStep({title:"Parsing an instruction.",content:'The next instruction to execute is <pre>mov.b @r15, r14</pre>  This means "move whatever is at memory  addressed by r15 in to r14". Look at the value of r15.',showAt:"#registers",align:"center bottom",continueAfter:3e3}),i.addStep({title:"Find 439c in memory.",content:"Find the value of r15 (remember, it's 0x439c) in memory. Notice how the password you entered is there?",showAt:".memorybox",align:"right middle",continueAfter:3e3}),i.addStep({title:"Try it.",content:"Take a step (type 's') to watch the CPU move that value in to R14.",showAt:".textentrywrap",align:"left middle",continueWhen:e(/^(s|step)$/)}),i.addStep({title:"Register changed.",content:"Notice that register 14 has changed. 0x74 is the hex value of the character 't'.",showAt:"#registers",align:"center bottom",continueAfter:3e3}),i.addStep({title:"Another step.",content:"Now take another step (type 's') to watch the next instruction. This one is going to add one to r15.",showAt:".textentrywrap",align:"left middle",continueWhen:e(/^(s|step)$/)}),i.addStep({title:"Register to change.",content:"Notice r15 has incremented.",showAt:"#registers",align:"center bottom",continueAfter:3e3}),i.addStep({title:"Another step.",content:"The next instruction is going to add one to r12. Take a step (type 's') to watch it do that.",showAt:".textentrywrap",align:"left middle",continueWhen:e(/^(s|step)$/)}),i.addStep({title:"Register change.",content:"Notice the value of r12 has increased to 1.",showAt:"#registers",align:"center bottom",continueAfter:3e3}),i.addStep({title:"The tst instruction (test if not zero).",content:"The test function will compare the value in r14 with the constant 0.  It will then set flags in the status register accordingly.",showAt:"#memorywatch",align:"center bottom",continueAfter:3e3}),i.addStep({title:"Another step.",content:"Take a step (type 's') to watch the comparison.",showAt:".textentrywrap",align:"left middle",continueWhen:e(/^(s|step)$/)}),i.addStep({title:"The jnz instruction (jump if not zero).",content:'The jump-if-not-zero instruction is a conditional jump, which will move the program counter when the zero "flag" is not set. This one jumps backward by 8 bytes.',showAt:"#memorywatch",align:"center bottom",continueAfter:3e3}),i.addStep({title:"This is the status register.",content:'Mouse over it to look at the flags that are set.  The "C" means that the "Carry" flag is set. If the result of the last instruction was 0, the "Zero" flag would be set. It\'s not, though.',showAt:"#reg2",align:"left middle",continueAfter:3e3}),i.addStep({title:"Another step.",content:'Let\'s see it jump. Type "s".',showAt:".textentrywrap",align:"left middle",continueWhen:e(/^(s|step)$/)}),i.addStep({title:"We're back where we started.",content:"But remember, we processed one byte of input, and incremented r12 along the way.",showAt:".asmbox",align:"right middle",continueAfter:3e3}),i.addStep({title:"Eventually the loop will end.",content:'When it happens that r14 is 0, the jump  won\'t occur, and we will end at address 0x448e.  Set a breakpoint there with "break 448e". Notice that this is a base-16 address. All numbers you enter in the debugger are base-16.',showAt:".textentrywrap",align:"left middle",continueWhen:e(/^(b|break) 448e$/)}),i.addStep({title:"Unset the other breakpoint",content:'You also need to unset your other breakpoint. Type "unbreak check_password".',showAt:".textentrywrap",align:"left middle",continueWhen:e(/^unbreak check_password$/)}),i.addStep({title:"Now continue to that location",content:'Type "c"',showAt:".textentrywrap",align:"left middle",continueWhen:e(/^(c|continue)$/)}),i.addStep({title:"Unbreak it now.",content:'We don\'t want this breakpoint any more, type "unbreak 448e"',showAt:".textentrywrap",align:"left middle",continueWhen:e(/^(unbreak) 448e$/)}),i.addStep({title:"The cmp instruction (compare two values).",content:"The compare instruction will compare the value in r12 with the constant 9.  Notice that r12 is 5 right now. This is because  we entered a 4 character password, with one additional character for the null byte.",showAt:"#memorywatch",align:"center bottom",continueAfter:3e3}),i.addStep({title:"Step to watch it do that",content:'Type "s"',showAt:".textentrywrap",align:"left middle",continueWhen:e(/^(s|step)$/)}),i.addStep({title:"The jeq/jz instruction (jump if equal/jump if zero)",content:'This function will skip forward by 4 bytes if the comparison was true (if r12 was 9). The jump-if-equal and jump-if-zero instructions are actually equivalent: this is because "cmp" sets the zero flag when the values are equal. ',showAt:"#memorywatch",align:"center bottom",continueAfter:3e3}),i.addStep({title:"The zero flag isn't set, so we don't expect the jump to happen.",content:'Type "s"',showAt:".textentrywrap",align:"left middle",continueWhen:e(/^(s|step)$/)}),i.addStep({title:"What if we did jump?.",content:"See what would have happened if we did jump",showAt:".asmbox",align:"right middle",continueAfter:3e3}),i.addStep({title:"We would have ended up here.",content:"At address 4498.",showAt:"#insn4498",align:"center bottom",continueAfter:3e3}),i.addStep({title:"Change the program counter.",content:'Type "let pc=4498" to change where the program counter points to',showAt:".textentrywrap",align:"left middle",continueWhen:e(/^(let |)pc ?= ?4498$/)}),i.addStep({title:"Out",content:'Step out (type "out" or "f") to see what\'s going to happen next',showAt:".textentrywrap",align:"left middle",continueWhen:e(/^(out|f|finish)$/)}),i.addStep({title:"Testing r15",content:'We\'re running a "test" instruction again.  It checks if r15 is non-zero, and sets the status flag accordingly.',showAt:".asmbox",align:"right middle",continueAfter:3e3}),i.addStep({title:"Step",content:'Watch the instruction run; type "step"',showAt:".textentrywrap",align:"left middle",continueWhen:e(/^(s|step)$/)}),i.addStep({title:"Step again.",content:'We know that r15 was 1, and the jump happens when the value isn\'t 0. Step again; type "s".',showAt:".textentrywrap",align:"left middle",continueWhen:e(/^(s|step)$/)}),i.addStep({title:"Done!",content:"We're moving the access granted string, and then calling puts, and then calling unlock_door. This means we're done.",showAt:".asmbox",align:"right middle",continueAfter:3e3}),i.addStep({title:"Continue",content:'Continue the CPU executing with "c"',showAt:".textentrywrap",align:"left middle",continueWhen:function(){return e(/^(c|continue)$/,1)}()}),i.addStep({title:"Yay!",content:"But remember, we cheated by moving the program counter to the instruction we wanted. Let's do it again, but with the correct password this time",showAt:"#nextlevelbutton",align:"center bottom",continueWhen:"click #nextlevelbutton"}),i.addStep({title:"Again.",content:'Reset the state of the CPU (type "reset") and start again.',showAt:".textentrywrap",align:"left middle",continueWhen:e(/^(reset)$/)}),i.addStep({title:"Continue",content:'Start up the CPU to get the input prompt. Type "c".',showAt:".textentrywrap",align:"left middle",continueWhen:e(/^(c|continue)$/)}),i.addStep({title:"The interrupt request also has additional options.",content:'This check box lets you enter hex-encoded values, for when you need to enter special characters. For example, you would type "74657374" instead of "test", after checking this box.',showAt:"#io_check_box",align:"center bottom",waitToShow:t(),continueAfter:3e3}),i.addStep({title:"The interrupt request also has additional options.",content:'This button lets you dismiss the popup and go back to the debugger to investigate more. You can resume the CPU with "continue" which will bring back this popup.',showAt:"#io_wait",align:"center bottom",continueAfter:3e3}),i.addStep({title:"Now let's solve it. We know how to make the password correct!",content:'Remember that r12 needed to be 9?  And it incremented once for every character we typed, plus one for the ending null byte?  So we just need to enter an 8 character password.  Try "password" as the input.',showAt:"#io_input_box",align:"center bottom",continueWhen:n("password")}),i.addStep({title:"Notice the CPU set a breakpoint",content:"After you send input from the debugger, the CPU automatically breaks. This makes it easier to debug what's going on. (This has happened every time previously, too.)",showAt:"#asmbox",align:"right middle",continueAfter:3e3}),i.addStep({title:"Continue",content:"Continue, to watch everything work",showAt:".textentrywrap",align:"left middle",continueWhen:function(){return e(/^(c|continue)$/,0,1)}()}),i.addStep({title:"Yay!",content:"Just remember that this was on the debugger lock.  Let's now do the same thing on the real lock, and let our operatives in the first warehouse.",showAt:"#nextlevelbutton",align:"center bottom",continueWhen:"click #nextlevelbutton"}),i.addStep({title:"To the lock!",content:"Now we're going to execute it on the real lock. Type \"solve\" to do that. You won't be able to run any debug commands, just enter the final solution.",showAt:".textentrywrap",align:"left middle",continueWhen:function(){return e(/^(solve)$/,0,1)}()}),i.addStep({title:"We know the password now!",content:"Just enter 'password'",showAt:"#io_input_box",align:"center bottom",waitToShow:t(),continueWhen:n("password",1)}),i.addStep({title:"That's it!",content:"You now know enough to break more locks.",showAt:"#ss-submit",align:"center bottom",continueWhen:"click #ss-submit"}),cpu.get("/whoami",function(e){"Tutorial"==e.level&&(guide.register(),Guideline.setCurrentPage("/cpu/debugger"),Guideline.getGuide("welcome").start(function(){}))})});