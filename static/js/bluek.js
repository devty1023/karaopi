/*
 * bluek.js
 *
 * version 0.1
 * @devty1023
 * 11.02.2014 
 */
/*
 * usage:
 * 
 * <audio src="..." id="audio"></audio>
 * <div class="bluek"
 *      data-audio="audio"
 *      data-src="08008.json">
 * </div> 
 */

function BluekEngine(timings) {
    this.timings = timings;
}

BluekEngine.prototype.update = function(curTime) {
    curTime = ~~(curTime * 1000);
    for(var i = 0; i < this.timings.length; ++i) {
        if(this.timings[i].start < curTime &&
            this.timings[i].end > curTime)
        {
            this.CURRENT_LINE = i;
            return i;
        }
    }
    this.CURRENT_LINE = -1;
    return -1;
}

BluekEngine.prototype.getCurrentLineNum = function() {
    return this.CURRENT_LINE;
}

BluekEngine.prototype.getCurrentLine = function() {
    if(this.CURRENT_LINE < 0) {
        return "Bluek Karaoke Machine";
    }
    return this.timings[this.CURRENT_LINE].line;
}


BluekEngine.prototype.getFollowingLine = function() {
    if(this.CURRENT_LINE < 0 ||
        this.CURRENT_LINE+1 > this.timings.length) {
        return "";
    }
    return this.timings[this.CURRENT_LINE+1].line;
}

function SimpleDisplay(engine, element) {
    this.engine = engine;
    this.element = element;

    var currentLine = document.createElement("div");
    $(currentLine).attr("class", "bluek current");
    $(currentLine).attr("id", "bluek-current");

    var followingLine = document.createElement("div");
    $(followingLine).attr("class", "bluek following");
    $(followingLine).attr("id", "bluek-following");

    $(this.element).append(currentLine);
    $(this.element).append(followingLine);
}

SimpleDisplay.prototype.render = function() {
    var current = $('#bluek-current');
    var following = $('#bluek-following');
    current.html('<h1 class="bluek current">'+this.engine.getCurrentLine()+"</h1>");
    following.html('<h1 class="bluek following">'+this.engine.getFollowingLine()+"</h1>");

    var currentN = this.engine.getCurrentLineNum();
    if (currentN != 0 && 
          currentN != this.CURRENT_LINE)
    {
        this.flip = this.flip ? false : true; // flip
        this.CURRENT_LINE = currentN;
    }

    if(this.flip)
    {
        $(current).before($(following));
    }
    else
    {
        $(following).before($(current));
    }
}

SimpleDisplay.prototype.CURRENT_LINE = -1;

SimpleDisplay.prototype.flip = false;


$(document).ready(function() {
    function playKaraoke(element, data) {
        var audioId = element.attr('data-audio')
        var kengine = new BluekEngine(data)
        var display = new SimpleDisplay(kengine, element)
        setInterval(function() {
            var curTime = document.getElementById(audioId).currentTime;
            kengine.update(curTime);
            display.render();
        }, 80);
    }
    $('.bluek').each(function() {
        var element = $(this);
        var audioId = element.attr('data-audio')
        var audioSrc = element.attr('data-src')

        if(audioId && audioSrc)
        {
            console.log(audioSrc)
            $.getJSON(audioSrc, function(data) {
                playKaraoke(element, data);
            });

        }
    });
});
