function doneassemble(){cpu.send("/assemble",{asm:$("#assemble").val()},function(e){console.log(e);var t="";if(e.error)t="ERROR: "+e.error;else for(var n=0;n<e.opcodes.length;n+=40)t+=e.opcodes.substr(n,40)+"\n";$("#thing").after($("<tr>").append($("<td>").text($("#assemble").val())).append($("<td>").attr("class","oorange").text(t)))},1)}function donedisassemble(){var e=$("#assemble").val().split("\n"),t="";for(var n in e){var i=e[n];/^[0-9a-f]+:([ ]+[0-9a-f]+)+ +.{8,17}$/.test(i)&&(i=i.replace(/^[0-9a-f]+:(([ ]+[0-9a-f]+)+) +.{8,17}$/g,"$1")),t+=i.replace(/ /g,"")}cpu.get("/cpu/dbg/disasm?obj="+t,function(e){var t="";t=e.error?"ERROR: "+e.error:e.data.insns.join("\n"),$("#thing").after($("<tr>").append($("<td>").attr("class","oorange").text(t)).append($("<td>").text($("#assemble").val())))},1)}var cpu={send:function(e,t,n){$.ajax({url:e,type:"POST",dataType:"json",contentType:"application/json",data:JSON.stringify(t)}).fail(function(){}).done(function(e){n&&n(e)})},get:function(e,t){$.ajax({url:e,type:"get",dataType:"json"}).fail(function(){console.log("Connection to server failed; GET could not be sent.")}).done(function(e){t&&t(e)})}};