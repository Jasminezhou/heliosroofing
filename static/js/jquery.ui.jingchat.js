(function($){
    $.widget("ui.chatbox", {
        options: {
            id: null, //id for the DOM element
            title: null, // title of the chatbox
            user: null, // can be anything associated with this chatbox
            hidden: false,
            offset: 0, // relative to right edge of the browser window
            width: 300, // width of the chatbox
            introPhoto: "http://placehold.it/50/55C1E7/fff&amp;text=J",
            introName: "Support person name here...",
            introDescription: "Chat Descriptions here...",
            messageSent: function(id, user, msg) {
                // override this
                this.boxManager.addMsg(user.first_name, msg);
            },
            boxClosed: function(id) {
            }, // called when the close icon is clicked
            boxManager: {
                // thanks to the widget factory facility
                // similar to http://alexsexton.com/?p=51
                init: function(elem) {
                    this.elem = elem;
                },
                addMsg: function(peer, msg) {
                    var self = this;
                    var box = self.elem.uiChatboxLog;
                    var e = document.createElement('div');
                    box.append(e);
                    $(e).hide();

                    var systemMessage = false;

                    if (peer) {
                        var peerName = document.createElement("b");
                        $(peerName).text(peer + ": ");
                        e.appendChild(peerName);
                    } else {
                        systemMessage = true;
                    }

                    var msgElement = document.createElement(
                        systemMessage ? "i" : "span");
                    $(msgElement).text(msg);
                    e.appendChild(msgElement);
                    $(e).addClass("ui-chatbox-msg");
                    $(e).css("maxWidth", $(box).width());
                    $(e).fadeIn();
                    self._scrollToBottom();

                    if (!self.elem.uiChatboxTitlebar.hasClass("ui-state-focus")
                        && !self.highlightLock) {
                        self.highlightLock = true;
                        self.highlightBox();
                    }
                },
                highlightBox: function() {
                    var self = this;
                    self.elem.uiChatboxTitlebar.effect("highlight", {}, 300);
                    self.elem.uiChatbox.effect("bounce", {times: 3}, 300, function() {
                        self.highlightLock = false;
                        self._scrollToBottom();
                    });
                },
                toggleBox: function() {
                    this.elem.uiChatbox.toggle();
                },
                _scrollToBottom: function() {
                    var box = this.elem.uiChatboxLog;
                    box.scrollTop(box.get(0).scrollHeight);
                }
            }
        },
        toggleContent: function(event) {
            this.uiChatboxContent.toggle();
            this.uiChatboxIntro.toggle();
            this.uiChatboxFooter.toggle();
            if (this.uiChatboxContent.is(":visible")) {
                this.uiChatboxTitlebarOpen.hide();
                this.uiChatboxTitlebarClose.show();
                this.uiChatboxInputBox.focus();
            } else {
                this.uiChatboxTitlebarOpen.show();
                this.uiChatboxTitlebarClose.hide();
            }
        },
        widget: function() {
            return this.uiChatbox
        },
        _create: function() {
            var self = this,
            options = self.options,
            title = options.title || "Jing Chatbox",
            // chatbox
            uiChatbox = (self.uiChatbox = self.element)
                .addClass('panel ' +
                          'panel-primary '
                         )
                .attr('outline', 0)
                .focusin(function() {
                    // ui-state-highlight is not really helpful here
                    //self.uiChatbox.removeClass('ui-state-highlight');
                    self.uiChatboxTitlebar.addClass('ui-state-focus');
                })
                .focusout(function() {
                    self.uiChatboxTitlebar.removeClass('ui-state-focus');
                }),
            // titlebar
            uiChatboxTitlebar = (self.uiChatboxTitlebar = $('<div></div>'))
                .addClass('panel-heading '
                         )
                .click(function(event) {
                    self.toggleContent(event);
                })
                .appendTo(uiChatbox),
            uiChatboxTitle = (self.uiChatboxTitle = $('<span><span class="glyphicon glyphicon-comment"></span></span>'))
                .html(title)
                .appendTo(uiChatboxTitlebar),
            uiChatboxTitlebarClose = (self.uiChatboxTitlebarClose = $('<span class="close glyphicon glyphicon-remove pull-right"></span>'))
                .hover(function() { uiChatboxTitlebarClose.addClass('ui-state-hover'); },
                       function() { uiChatboxTitlebarClose.removeClass('ui-state-hover'); })
                .click(function(event) {
                    self.toggleContent(event);
                    return false;
                })
                .appendTo(uiChatboxTitlebar),
            uiChatboxTitlebarOpen = (self.uiChatboxTitlebarOpen = $('<span class="open pull-right glyphicon glyphicon-minus"></span>'))
                .hover(function() { uiChatboxTitlebarOpen.addClass('ui-state-hover'); },
                       function() { uiChatboxTitlebarOpen.removeClass('ui-state-hover'); })
                .click(function(event) {
                    self.toggleContent(event);
                    return false;
                })
                .appendTo(uiChatboxTitlebar),
            // intro
            uiChatboxIntro = (self.uiChatboxIntro = $('<div></div>'))
                .addClass('row ' +
                          'expert'
                    )
                .appendTo(uiChatbox),
            uiChatboxIntroPhoto = (self.uiChatboxIntroPhoto = $('<img class="col-xs-5" alt="our expert">'))
                .attr('src', options.introPhoto)
                .appendTo(uiChatboxIntro),
            uiChatboxIntroDetail = (self.uiChatboxIntroDetail = $('<div class="col-xs-7"></div>'
)).
                appendTo(uiChatboxIntro),
            uiChatboxIntroName = (self.uiChatboxIntroName = $('<h3></h3>'))
                .html(options.introName)
                .appendTo(uiChatboxIntroDetail),
            uiChatboxIntroDescription = (self.uiChatboxIntroDescription = $('<p></p>'))
                .html(options.introDescription)
                .appendTo(uiChatboxIntroDetail),
            // content
            uiChatboxContent = (self.uiChatboxContent = $('<div></div>'))
                .addClass('panel-body'
                         )
                .appendTo(uiChatbox),
            uiChatboxLog = (self.uiChatboxLog = $('<ul>'))
                .addClass('chat')
                .appendTo(uiChatboxContent),
            // footer
            uiChatboxFooter = (self.uiChatboxFooter = $('<div></div>'))
                .addClass('panel-footer')
                .appendTo(uiChatbox),
            uiChatboxInput = (self.uiChatboxInput = $('<div></div>'))
                .addClass('input-group')
                .appendTo(uiChatboxFooter),
            uiChatboxInputBox = (self.uiChatboxInputBox = $('<input>'))
                .addClass('form-control ' +
                          'input-sm'
                         )
                .attr('placeholder', 'Type your message here')
                .appendTo(uiChatboxInput)
                .keydown(function(event) {
                    if (event.keyCode && event.keyCode == $.ui.keyCode.ENTER) {
                        msg = $.trim($(this).val());
                        if (msg.length > 0) {
                            self.options.messageSent(self.options.id, self.options.user, msg);
                        }
                        $(this).val('');
                        return false;
                    }
                })
                .focusin(function() {
                    uiChatboxInputBox.addClass('ui-chatbox-input-focus');
                    var box = self.uiChatboxLog;
                    box.scrollTop(box.get(0).scrollHeight);
                })
                .focusout(function() {
                    uiChatboxInputBox.removeClass('ui-chatbox-input-focus');
                }),
            uiChatboxInputButton = (self.uiChatboxInputButton = $('<span class="input-group-btn"><button class="btn btn-warning btn-sm" id="btn-chat">Send</button></span>'))
                .appendTo(uiChatboxInput);

            // disable selection
            uiChatboxTitlebar.find('*').add(uiChatboxTitlebar).disableSelection();

            // hide close button
            uiChatboxTitlebarClose.hide();
            self.toggleContent();
            // switch focus to input box when whatever clicked
            uiChatboxContent.children().click(function() {
                // click on any children, set focus on input box
                self.uiChatboxInputBox.focus();
            });

            self._setWidth(self.options.width);
            self._position(self.options.offset);

            self.options.boxManager.init(self);

            if (!self.options.hidden) {
                uiChatbox.show();
            }
        },
        _setOption: function(option, value) {
            if (value != null) {
                switch (option) {
                case "hidden":
                    if (value)
                        this.uiChatbox.hide();
                    else
                        this.uiChatbox.show();
                    break;
                case "offset":
                    this._position(value);
                    break;
                case "width":
                    this._setWidth(value);
                    break;
                }
            }
            $.Widget.prototype._setOption.apply(this, arguments);
        },
        _setWidth: function(width) {
            this.uiChatboxTitlebar.width(width + "px");
            this.uiChatboxLog.width(width + "px");
            this.uiChatboxInput.css("maxWidth", width + "px");
            // padding:2, boarder:2, margin:5
            // this.uiChatboxInputBox.css("width", (width - 18) + "px");
        },
        _position: function(offset) {
            this.uiChatbox.css("right", offset);
        }
    });
}(jQuery));
