


$.fn.update_mylabelstatus = function(updatetime) {
    if (typeof updatetime == "undefined") updatetime = 0;
    var $icon = $(this);
    var badges =[
        [0,    "The Newb","#999999"],
        [9,    "The Unpaid Intern","#00cc32"],
        [27,   "The Intern", "#90ff00"],
        [81,   "The Undergraduate Student","#f8ff00"],
        [162,  "The Grad Student","#ff884b"],
        [324,  "The Postdoc Researcher","#ff3317"],
        [648,  "The Assistant Scientist","#ff001a"],
        [1296, "The Scientist","#ff00e7"],
        [2592, "Nemo","#7600ff"],
        [5184, "Aquaman/Aquagirl","#6f72ff"],
        [10368,"Poseidon","#00daff"]
    ];

    var badgestr = "";
    for (var i in badges) badgestr += "<i class='icon-star' style='color:"+badges[i][2]+"'>"+badges[i][1]+" (>"+badges[i][0]+")</i><br>";

    $icon.data("badge",badges[0])
        .css("color",badges[0][2])
        .popover({
            placement:"bottom",
            title:"YOUR STATUS RANKING:",
            html:true,
            content:function(){
                return "<small>You have labelled "+$(this).data("mylabelcount")+" points so far. That is as many as <b style='color:"+$(this).data("badge")[2]+"'>"+$(this).data("badge")[1]+"!</b> "
                    +" &nbsp;Keep labelling to progress through the ranks:<hr style='margin:5px 0'>"
                    +badgestr+"</small>";
            },
            trigger:"hover"});
    updateMyLabelStatus(updatetime, $icon, badges);
    return this;
}


function updateMyLabelStatus(updatetime, $icon, badges) {
    $.ajax({
        dataType: "json",
        async: true,
        url: "get_annotation_info",
        success: function (data) {
            for (var i=badges.length-1 ; i>=0 ; i--) {
                if (parseInt(badges[i][0]) <= parseInt(data.mylabelcount)) {
                    $icon.data("badge",badges[i]);
                    $icon.data("mylabelcount",data.mylabelcount);
                    break;
                }
            }
            $icon.css("color",$icon.data("badge")[2]).html('<i class="icon-star">'+$icon.data("mylabelcount")+'</i>'+$icon.data("badge")[1]);
        },
        error: function(XMLHttpRequest, textStatus, errorThrown) {
            console.log(XMLHttpRequest);
        }
    });
    if (updatetime > 0) setTimeout(function(){updateMyLabelStatus(updatetime, $icon, badges)},updatetime);
}
