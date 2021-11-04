//
// ChemDoodle Web Components 9.2.0
//
// https://web.chemdoodle.com
//
// Copyright 2009-2021 iChemLabs, LLC.  All rights reserved.
//
// The ChemDoodle Web Components library is licensed under version 3
// of the GNU GENERAL PUBLIC LICENSE.
//
// You may redistribute it and/or modify it under the terms of the
// GNU General Public License as published by the Free Software Foundation,
// either version 3 of the License, or (at your option) any later version.
//
// As an exception to the GPL, you may distribute this packed form of
// the code without the copy of the GPL license normally required,
// provided you include this license notice and a URL through which
// recipients can access the corresponding unpacked source code. 
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// ChemDoodle Web Components employs 3rd party libraries under the MIT
// license. For a full list with links to the original source, go to:
// https://web.chemdoodle.com/installation/download/#libraries
//
// Please contact iChemLabs <https://www.ichemlabs.com/contact-us> for
// alternate licensing options.
//

/*
The following changes have been made:
1. made the code pretty using https://beautifier.io/
2. remove the save button

- Tony Schaefer, August 2021
*/

'use strict';
(function(g) {
    (function(a) {
        "function" === typeof define && define.amd ? define(["jquery"], a) : a(g)
    })(function(a) {
        function g(b, c) {
            var k = b.nodeName.toLowerCase();
            if ("area" === k) {
                c = b.parentNode;
                k = c.name;
                if (!b.href || !k || "map" !== c.nodeName.toLowerCase()) return !1;
                b = a("img[usemap\x3d'#" + k + "']")[0];
                return !!b && f(b)
            }
            return (/^(input|select|textarea|button|object)$/.test(k) ? !b.disabled : "a" === k ? b.href || c : c) && f(b)
        }

        function f(b) {
            return a.expr.filters.visible(b) && !a(b).parents().addBack().filter(function() {
                return "hidden" ===
                    a.css(this, "visibility")
            }).length
        }

        function m(b) {
            for (var c; b.length && b[0] !== document;) {
                c = b.css("position");
                if ("absolute" === c || "relative" === c || "fixed" === c)
                    if (c = parseInt(b.css("zIndex"), 10), !isNaN(c) && 0 !== c) return c;
                b = b.parent()
            }
            return 0
        }

        function h() {
            this._curInst = null;
            this._keyEvent = !1;
            this._disabledInputs = [];
            this._inDialog = this._datepickerShowing = !1;
            this._mainDivId = "ui-datepicker-div";
            this._inlineClass = "ui-datepicker-inline";
            this._appendClass = "ui-datepicker-append";
            this._triggerClass = "ui-datepicker-trigger";
            this._dialogClass = "ui-datepicker-dialog";
            this._disableClass = "ui-datepicker-disabled";
            this._unselectableClass = "ui-datepicker-unselectable";
            this._currentClass = "ui-datepicker-current-day";
            this._dayOverClass = "ui-datepicker-days-cell-over";
            this.regional = [];
            this.regional[""] = {
                closeText: "Done",
                prevText: "Prev",
                nextText: "Next",
                currentText: "Today",
                monthNames: "January February March April May June July August September October November December".split(" "),
                monthNamesShort: "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split(" "),
                dayNames: "Sunday Monday Tuesday Wednesday Thursday Friday Saturday".split(" "),
                dayNamesShort: "Sun Mon Tue Wed Thu Fri Sat".split(" "),
                dayNamesMin: "Su Mo Tu We Th Fr Sa".split(" "),
                weekHeader: "Wk",
                dateFormat: "mm/dd/yy",
                firstDay: 0,
                isRTL: !1,
                showMonthAfterYear: !1,
                yearSuffix: ""
            };
            this._defaults = {
                showOn: "focus",
                showAnim: "fadeIn",
                showOptions: {},
                defaultDate: null,
                appendText: "",
                buttonText: "...",
                buttonImage: "",
                buttonImageOnly: !1,
                hideIfNoPrevNext: !1,
                navigationAsDateFormat: !1,
                gotoCurrent: !1,
                changeMonth: !1,
                changeYear: !1,
                yearRange: "c-10:c+10",
                showOtherMonths: !1,
                selectOtherMonths: !1,
                showWeek: !1,
                calculateWeek: this.iso8601Week,
                shortYearCutoff: "+10",
                minDate: null,
                maxDate: null,
                duration: "fast",
                beforeShowDay: null,
                beforeShow: null,
                onSelect: null,
                onChangeMonthYear: null,
                onClose: null,
                numberOfMonths: 1,
                showCurrentAtPos: 0,
                stepMonths: 1,
                stepBigMonths: 12,
                altField: "",
                altFormat: "",
                constrainInput: !0,
                showButtonPanel: !1,
                autoSize: !1,
                disabled: !1
            };
            a.extend(this._defaults, this.regional[""]);
            this.regional.en = a.extend(!0, {}, this.regional[""]);
            this.regional["en-US"] = a.extend(!0, {}, this.regional.en);
            this.dpDiv = d(a("\x3cdiv id\x3d'" + this._mainDivId + "' class\x3d'ui-datepicker ui-widget ui-widget-content ui-helper-clearfix ui-corner-all'\x3e\x3c/div\x3e"))
        }

        function d(b) {
            return b.delegate("button, .ui-datepicker-prev, .ui-datepicker-next, .ui-datepicker-calendar td a", "mouseout", function() {
                a(this).removeClass("ui-state-hover"); - 1 !== this.className.indexOf("ui-datepicker-prev") && a(this).removeClass("ui-datepicker-prev-hover"); - 1 !== this.className.indexOf("ui-datepicker-next") &&
                    a(this).removeClass("ui-datepicker-next-hover")
            }).delegate("button, .ui-datepicker-prev, .ui-datepicker-next, .ui-datepicker-calendar td a", "mouseover", l)
        }

        function l() {
            a.datepicker._isDisabledDatepicker(w.inline ? w.dpDiv.parent()[0] : w.input[0]) || (a(this).parents(".ui-datepicker-calendar").find("a").removeClass("ui-state-hover"), a(this).addClass("ui-state-hover"), -1 !== this.className.indexOf("ui-datepicker-prev") && a(this).addClass("ui-datepicker-prev-hover"), -1 !== this.className.indexOf("ui-datepicker-next") &&
                a(this).addClass("ui-datepicker-next-hover"))
        }

        function t(b, c) {
            a.extend(b, c);
            for (var k in c) null == c[k] && (b[k] = c[k]);
            return b
        }

        function q(b) {
            return function() {
                var c = this.element.val();
                b.apply(this, arguments);
                this._refresh();
                c !== this.element.val() && this._trigger("change")
            }
        }
        a.ui = a.ui || {};
        a.extend(a.ui, {
            version: "1.11.4",
            keyCode: {
                BACKSPACE: 8,
                COMMA: 188,
                DELETE: 46,
                DOWN: 40,
                END: 35,
                ENTER: 13,
                ESCAPE: 27,
                HOME: 36,
                LEFT: 37,
                PAGE_DOWN: 34,
                PAGE_UP: 33,
                PERIOD: 190,
                RIGHT: 39,
                SPACE: 32,
                TAB: 9,
                UP: 38
            }
        });
        a.fn.extend({
            scrollParent: function(b) {
                var c =
                    this.css("position"),
                    k = "absolute" === c,
                    e = b ? /(auto|scroll|hidden)/ : /(auto|scroll)/;
                b = this.parents().filter(function() {
                    var b = a(this);
                    return k && "static" === b.css("position") ? !1 : e.test(b.css("overflow") + b.css("overflow-y") + b.css("overflow-x"))
                }).eq(0);
                return "fixed" !== c && b.length ? b : a(this[0].ownerDocument || document)
            },
            uniqueId: function() {
                var b = 0;
                return function() {
                    return this.each(function() {
                        this.id || (this.id = "ui-id-" + ++b)
                    })
                }
            }(),
            removeUniqueId: function() {
                return this.each(function() {
                    /^ui-id-\d+$/.test(this.id) &&
                        a(this).removeAttr("id")
                })
            }
        });
        a.extend(a.expr[":"], {
            data: a.expr.createPseudo ? a.expr.createPseudo(function(b) {
                return function(c) {
                    return !!a.data(c, b)
                }
            }) : function(b, c, k) {
                return !!a.data(b, k[3])
            },
            focusable: function(b) {
                return g(b, !isNaN(a.attr(b, "tabindex")))
            },
            tabbable: function(b) {
                var c = a.attr(b, "tabindex"),
                    k = isNaN(c);
                return (k || 0 <= c) && g(b, !k)
            }
        });
        a("\x3ca\x3e").outerWidth(1).jquery || a.each(["Width", "Height"], function(b, c) {
            function k(b, c, k, u) {
                a.each(e, function() {
                    c -= parseFloat(a.css(b, "padding" + this)) || 0;
                    k && (c -= parseFloat(a.css(b, "border" + this + "Width")) || 0);
                    u && (c -= parseFloat(a.css(b, "margin" + this)) || 0)
                });
                return c
            }
            var e = "Width" === c ? ["Left", "Right"] : ["Top", "Bottom"],
                d = c.toLowerCase(),
                f = {
                    innerWidth: a.fn.innerWidth,
                    innerHeight: a.fn.innerHeight,
                    outerWidth: a.fn.outerWidth,
                    outerHeight: a.fn.outerHeight
                };
            a.fn["inner" + c] = function(b) {
                return void 0 === b ? f["inner" + c].call(this) : this.each(function() {
                    a(this).css(d, k(this, b) + "px")
                })
            };
            a.fn["outer" + c] = function(b, e) {
                return "number" !== typeof b ? f["outer" + c].call(this, b) :
                    this.each(function() {
                        a(this).css(d, k(this, b, !0, e) + "px")
                    })
            }
        });
        a.fn.addBack || (a.fn.addBack = function(b) {
            return this.add(null == b ? this.prevObject : this.prevObject.filter(b))
        });
        a("\x3ca\x3e").data("a-b", "a").removeData("a-b").data("a-b") && (a.fn.removeData = function(b) {
            return function(c) {
                return arguments.length ? b.call(this, a.camelCase(c)) : b.call(this)
            }
        }(a.fn.removeData));
        a.ui.ie = !!/msie [\w.]+/.exec(navigator.userAgent.toLowerCase());
        a.fn.extend({
            focus: function(b) {
                return function(c, k) {
                    return "number" === typeof c ?
                        this.each(function() {
                            var b = this;
                            setTimeout(function() {
                                a(b).focus();
                                k && k.call(b)
                            }, c)
                        }) : b.apply(this, arguments)
                }
            }(a.fn.focus),
            disableSelection: function() {
                var b = "onselectstart" in document.createElement("div") ? "selectstart" : "mousedown";
                return function() {
                    return this.bind(b + ".ui-disableSelection", function(b) {
                        b.preventDefault()
                    })
                }
            }(),
            enableSelection: function() {
                return this.unbind(".ui-disableSelection")
            },
            zIndex: function(b) {
                if (void 0 !== b) return this.css("zIndex", b);
                if (this.length) {
                    b = a(this[0]);
                    for (var c; b.length &&
                        b[0] !== document;) {
                        c = b.css("position");
                        if ("absolute" === c || "relative" === c || "fixed" === c)
                            if (c = parseInt(b.css("zIndex"), 10), !isNaN(c) && 0 !== c) return c;
                        b = b.parent()
                    }
                }
                return 0
            }
        });
        a.ui.plugin = {
            add: function(b, c, k) {
                var e;
                b = a.ui[b].prototype;
                for (e in k) b.plugins[e] = b.plugins[e] || [], b.plugins[e].push([c, k[e]])
            },
            call: function(b, c, a, e) {
                if ((c = b.plugins[c]) && (e || b.element[0].parentNode && 11 !== b.element[0].parentNode.nodeType))
                    for (e = 0; e < c.length; e++) b.options[c[e][0]] && c[e][1].apply(b.element, a)
            }
        };
        var r = 0,
            n = Array.prototype.slice;
        a.cleanData = function(b) {
            return function(c) {
                var k, e, d;
                for (d = 0; null != (e = c[d]); d++) try {
                    (k = a._data(e, "events")) && k.remove && a(e).triggerHandler("remove")
                } catch (G) {}
                b(c)
            }
        }(a.cleanData);
        a.widget = function(b, c, k) {
            var e = {},
                d = b.split(".")[0];
            b = b.split(".")[1];
            var f = d + "-" + b;
            k || (k = c, c = a.Widget);
            a.expr[":"][f.toLowerCase()] = function(b) {
                return !!a.data(b, f)
            };
            a[d] = a[d] || {};
            var h = a[d][b];
            var n = a[d][b] = function(b, c) {
                if (!this._createWidget) return new n(b, c);
                arguments.length && this._createWidget(b, c)
            };
            a.extend(n, h, {
                version: k.version,
                _proto: a.extend({}, k),
                _childConstructors: []
            });
            var l = new c;
            l.options = a.widget.extend({}, l.options);
            a.each(k, function(b, k) {
                a.isFunction(k) ? e[b] = function() {
                    var a = function() {
                            return c.prototype[b].apply(this, arguments)
                        },
                        e = function(a) {
                            return c.prototype[b].apply(this, a)
                        };
                    return function() {
                        var b = this._super,
                            c = this._superApply;
                        this._super = a;
                        this._superApply = e;
                        var u = k.apply(this, arguments);
                        this._super = b;
                        this._superApply = c;
                        return u
                    }
                }() : e[b] = k
            });
            n.prototype = a.widget.extend(l, {
                widgetEventPrefix: h ? l.widgetEventPrefix ||
                    b : b
            }, e, {
                constructor: n,
                namespace: d,
                widgetName: b,
                widgetFullName: f
            });
            h ? (a.each(h._childConstructors, function(b, c) {
                b = c.prototype;
                a.widget(b.namespace + "." + b.widgetName, n, c._proto)
            }), delete h._childConstructors) : c._childConstructors.push(n);
            a.widget.bridge(b, n);
            return n
        };
        a.widget.extend = function(b) {
            for (var c = n.call(arguments, 1), k = 0, e = c.length, d, f; k < e; k++)
                for (d in c[k]) f = c[k][d], c[k].hasOwnProperty(d) && void 0 !== f && (a.isPlainObject(f) ? b[d] = a.isPlainObject(b[d]) ? a.widget.extend({}, b[d], f) : a.widget.extend({},
                    f) : b[d] = f);
            return b
        };
        a.widget.bridge = function(b, c) {
            var k = c.prototype.widgetFullName || b;
            a.fn[b] = function(e) {
                var u = "string" === typeof e,
                    d = n.call(arguments, 1),
                    f = this;
                u ? this.each(function() {
                    var c = a.data(this, k);
                    if ("instance" === e) return f = c, !1;
                    if (!c) return a.error("cannot call methods on " + b + " prior to initialization; attempted to call method '" + e + "'");
                    if (!a.isFunction(c[e]) || "_" === e.charAt(0)) return a.error("no such method '" + e + "' for " + b + " widget instance");
                    var u = c[e].apply(c, d);
                    if (u !== c && void 0 !== u) return f =
                        u && u.jquery ? f.pushStack(u.get()) : u, !1
                }) : (d.length && (e = a.widget.extend.apply(null, [e].concat(d))), this.each(function() {
                    var b = a.data(this, k);
                    b ? (b.option(e || {}), b._init && b._init()) : a.data(this, k, new c(e, this))
                }));
                return f
            }
        };
        a.Widget = function() {};
        a.Widget._childConstructors = [];
        a.Widget.prototype = {
            widgetName: "widget",
            widgetEventPrefix: "",
            defaultElement: "\x3cdiv\x3e",
            options: {
                disabled: !1,
                create: null
            },
            _createWidget: function(b, c) {
                c = a(c || this.defaultElement || this)[0];
                this.element = a(c);
                this.uuid = r++;
                this.eventNamespace =
                    "." + this.widgetName + this.uuid;
                this.bindings = a();
                this.hoverable = a();
                this.focusable = a();
                c !== this && (a.data(c, this.widgetFullName, this), this._on(!0, this.element, {
                    remove: function(b) {
                        b.target === c && this.destroy()
                    }
                }), this.document = a(c.style ? c.ownerDocument : c.document || c), this.window = a(this.document[0].defaultView || this.document[0].parentWindow));
                this.options = a.widget.extend({}, this.options, this._getCreateOptions(), b);
                this._create();
                this._trigger("create", null, this._getCreateEventData());
                this._init()
            },
            _getCreateOptions: a.noop,
            _getCreateEventData: a.noop,
            _create: a.noop,
            _init: a.noop,
            destroy: function() {
                this._destroy();
                this.element.unbind(this.eventNamespace).removeData(this.widgetFullName).removeData(a.camelCase(this.widgetFullName));
                this.widget().unbind(this.eventNamespace).removeAttr("aria-disabled").removeClass(this.widgetFullName + "-disabled ui-state-disabled");
                this.bindings.unbind(this.eventNamespace);
                this.hoverable.removeClass("ui-state-hover");
                this.focusable.removeClass("ui-state-focus")
            },
            _destroy: a.noop,
            widget: function() {
                return this.element
            },
            option: function(b, c) {
                var k = b,
                    e;
                if (0 === arguments.length) return a.widget.extend({}, this.options);
                if ("string" === typeof b) {
                    k = {};
                    var d = b.split(".");
                    b = d.shift();
                    if (d.length) {
                        var f = k[b] = a.widget.extend({}, this.options[b]);
                        for (e = 0; e < d.length - 1; e++) f[d[e]] = f[d[e]] || {}, f = f[d[e]];
                        b = d.pop();
                        if (1 === arguments.length) return void 0 === f[b] ? null : f[b];
                        f[b] = c
                    } else {
                        if (1 === arguments.length) return void 0 === this.options[b] ? null : this.options[b];
                        k[b] = c
                    }
                }
                this._setOptions(k);
                return this
            },
            _setOptions: function(b) {
                for (var c in b) this._setOption(c,
                    b[c]);
                return this
            },
            _setOption: function(b, c) {
                this.options[b] = c;
                "disabled" === b && (this.widget().toggleClass(this.widgetFullName + "-disabled", !!c), c && (this.hoverable.removeClass("ui-state-hover"), this.focusable.removeClass("ui-state-focus")));
                return this
            },
            enable: function() {
                return this._setOptions({
                    disabled: !1
                })
            },
            disable: function() {
                return this._setOptions({
                    disabled: !0
                })
            },
            _on: function(b, c, k) {
                var e, d = this;
                "boolean" !== typeof b && (k = c, c = b, b = !1);
                k ? (c = e = a(c), this.bindings = this.bindings.add(c)) : (k = c, c = this.element,
                    e = this.widget());
                a.each(k, function(k, u) {
                    function f() {
                        if (b || !0 !== d.options.disabled && !a(this).hasClass("ui-state-disabled")) return ("string" === typeof u ? d[u] : u).apply(d, arguments)
                    }
                    "string" !== typeof u && (f.guid = u.guid = u.guid || f.guid || a.guid++);
                    var h = k.match(/^([\w:-]*)\s*(.*)$/);
                    k = h[1] + d.eventNamespace;
                    (h = h[2]) ? e.delegate(h, k, f): c.bind(k, f)
                })
            },
            _off: function(b, c) {
                c = (c || "").split(" ").join(this.eventNamespace + " ") + this.eventNamespace;
                b.unbind(c).undelegate(c);
                this.bindings = a(this.bindings.not(b).get());
                this.focusable = a(this.focusable.not(b).get());
                this.hoverable = a(this.hoverable.not(b).get())
            },
            _delay: function(b, c) {
                var a = this;
                return setTimeout(function() {
                    return ("string" === typeof b ? a[b] : b).apply(a, arguments)
                }, c || 0)
            },
            _hoverable: function(b) {
                this.hoverable = this.hoverable.add(b);
                this._on(b, {
                    mouseenter: function(b) {
                        a(b.currentTarget).addClass("ui-state-hover")
                    },
                    mouseleave: function(b) {
                        a(b.currentTarget).removeClass("ui-state-hover")
                    }
                })
            },
            _focusable: function(b) {
                this.focusable = this.focusable.add(b);
                this._on(b, {
                    focusin: function(b) {
                        a(b.currentTarget).addClass("ui-state-focus")
                    },
                    focusout: function(b) {
                        a(b.currentTarget).removeClass("ui-state-focus")
                    }
                })
            },
            _trigger: function(b, c, k) {
                var e, d = this.options[b];
                k = k || {};
                c = a.Event(c);
                c.type = (b === this.widgetEventPrefix ? b : this.widgetEventPrefix + b).toLowerCase();
                c.target = this.element[0];
                if (b = c.originalEvent)
                    for (e in b) e in c || (c[e] = b[e]);
                this.element.trigger(c, k);
                return !(a.isFunction(d) && !1 === d.apply(this.element[0], [c].concat(k)) || c.isDefaultPrevented())
            }
        };
        a.each({
            show: "fadeIn",
            hide: "fadeOut"
        }, function(b, c) {
            a.Widget.prototype["_" + b] = function(k, e, d) {
                "string" === typeof e && (e = {
                    effect: e
                });
                var u = e ? !0 === e || "number" === typeof e ? c : e.effect || c : b;
                e = e || {};
                "number" === typeof e && (e = {
                    duration: e
                });
                var f = !a.isEmptyObject(e);
                e.complete = d;
                e.delay && k.delay(e.delay);
                if (f && a.effects && a.effects.effect[u]) k[b](e);
                else if (u !== b && k[u]) k[u](e.duration, e.easing, d);
                else k.queue(function(c) {
                    a(this)[b]();
                    d && d.call(k[0]);
                    c()
                })
            }
        });
        var v = !1;
        a(document).mouseup(function() {
            v = !1
        });
        a.widget("ui.mouse", {
            version: "1.11.4",
            options: {
                cancel: "input,textarea,button,select,option",
                distance: 1,
                delay: 0
            },
            _mouseInit: function() {
                var b = this;
                this.element.bind("mousedown." + this.widgetName, function(c) {
                    return b._mouseDown(c)
                }).bind("click." + this.widgetName, function(c) {
                    if (!0 === a.data(c.target, b.widgetName + ".preventClickEvent")) return a.removeData(c.target, b.widgetName + ".preventClickEvent"), c.stopImmediatePropagation(), !1
                });
                this.started = !1
            },
            _mouseDestroy: function() {
                this.element.unbind("." + this.widgetName);
                this._mouseMoveDelegate && this.document.unbind("mousemove." +
                    this.widgetName, this._mouseMoveDelegate).unbind("mouseup." + this.widgetName, this._mouseUpDelegate)
            },
            _mouseDown: function(b) {
                if (!v) {
                    this._mouseMoved = !1;
                    this._mouseStarted && this._mouseUp(b);
                    this._mouseDownEvent = b;
                    var c = this,
                        k = 1 === b.which,
                        e = "string" === typeof this.options.cancel && b.target.nodeName ? a(b.target).closest(this.options.cancel).length : !1;
                    if (!k || e || !this._mouseCapture(b)) return !0;
                    this.mouseDelayMet = !this.options.delay;
                    this.mouseDelayMet || (this._mouseDelayTimer = setTimeout(function() {
                        c.mouseDelayMet = !0
                    }, this.options.delay));
                    if (this._mouseDistanceMet(b) && this._mouseDelayMet(b) && (this._mouseStarted = !1 !== this._mouseStart(b), !this._mouseStarted)) return b.preventDefault(), !0;
                    !0 === a.data(b.target, this.widgetName + ".preventClickEvent") && a.removeData(b.target, this.widgetName + ".preventClickEvent");
                    this._mouseMoveDelegate = function(b) {
                        return c._mouseMove(b)
                    };
                    this._mouseUpDelegate = function(b) {
                        return c._mouseUp(b)
                    };
                    this.document.bind("mousemove." + this.widgetName, this._mouseMoveDelegate).bind("mouseup." + this.widgetName,
                        this._mouseUpDelegate);
                    b.preventDefault();
                    return v = !0
                }
            },
            _mouseMove: function(b) {
                if (this._mouseMoved && (a.ui.ie && (!document.documentMode || 9 > document.documentMode) && !b.button || !b.which)) return this._mouseUp(b);
                if (b.which || b.button) this._mouseMoved = !0;
                if (this._mouseStarted) return this._mouseDrag(b), b.preventDefault();
                this._mouseDistanceMet(b) && this._mouseDelayMet(b) && ((this._mouseStarted = !1 !== this._mouseStart(this._mouseDownEvent, b)) ? this._mouseDrag(b) : this._mouseUp(b));
                return !this._mouseStarted
            },
            _mouseUp: function(b) {
                this.document.unbind("mousemove." +
                    this.widgetName, this._mouseMoveDelegate).unbind("mouseup." + this.widgetName, this._mouseUpDelegate);
                this._mouseStarted && (this._mouseStarted = !1, b.target === this._mouseDownEvent.target && a.data(b.target, this.widgetName + ".preventClickEvent", !0), this._mouseStop(b));
                return v = !1
            },
            _mouseDistanceMet: function(b) {
                return Math.max(Math.abs(this._mouseDownEvent.pageX - b.pageX), Math.abs(this._mouseDownEvent.pageY - b.pageY)) >= this.options.distance
            },
            _mouseDelayMet: function() {
                return this.mouseDelayMet
            },
            _mouseStart: function() {},
            _mouseDrag: function() {},
            _mouseStop: function() {},
            _mouseCapture: function() {
                return !0
            }
        });
        (function() {
            function b(b, c, a) {
                return [parseFloat(b[0]) * (q.test(b[0]) ? c / 100 : 1), parseFloat(b[1]) * (q.test(b[1]) ? a / 100 : 1)]
            }

            function c(b) {
                var c = b[0];
                return 9 === c.nodeType ? {
                    width: b.width(),
                    height: b.height(),
                    offset: {
                        top: 0,
                        left: 0
                    }
                } : a.isWindow(c) ? {
                    width: b.width(),
                    height: b.height(),
                    offset: {
                        top: b.scrollTop(),
                        left: b.scrollLeft()
                    }
                } : c.preventDefault ? {
                    width: 0,
                    height: 0,
                    offset: {
                        top: c.pageY,
                        left: c.pageX
                    }
                } : {
                    width: b.outerWidth(),
                    height: b.outerHeight(),
                    offset: b.offset()
                }
            }
            a.ui = a.ui || {};
            var k, e, d = Math.max,
                f = Math.abs,
                h = Math.round,
                n = /left|center|right/,
                l = /top|center|bottom/,
                g = /[\+\-]\d+(\.[\d]+)?%?/,
                m = /^\w+/,
                q = /%$/,
                r = a.fn.position;
            a.position = {
                scrollbarWidth: function() {
                    if (void 0 !== k) return k;
                    var b = a("\x3cdiv style\x3d'display:block;position:absolute;width:50px;height:50px;overflow:hidden;'\x3e\x3cdiv style\x3d'height:100px;width:auto;'\x3e\x3c/div\x3e\x3c/div\x3e");
                    var c = b.children()[0];
                    a("body").append(b);
                    var e = c.offsetWidth;
                    b.css("overflow", "scroll");
                    c = c.offsetWidth;
                    e === c && (c = b[0].clientWidth);
                    b.remove();
                    return k = e - c
                },
                getScrollInfo: function(b) {
                    var c = b.isWindow || b.isDocument ? "" : b.element.css("overflow-x"),
                        k = b.isWindow || b.isDocument ? "" : b.element.css("overflow-y");
                    c = "scroll" === c || "auto" === c && b.width < b.element[0].scrollWidth;
                    return {
                        width: "scroll" === k || "auto" === k && b.height < b.element[0].scrollHeight ? a.position.scrollbarWidth() : 0,
                        height: c ? a.position.scrollbarWidth() : 0
                    }
                },
                getWithinInfo: function(b) {
                    b = a(b || window);
                    var c = a.isWindow(b[0]),
                        k = !!b[0] && 9 === b[0].nodeType;
                    return {
                        element: b,
                        isWindow: c,
                        isDocument: k,
                        offset: b.offset() || {
                            left: 0,
                            top: 0
                        },
                        scrollLeft: b.scrollLeft(),
                        scrollTop: b.scrollTop(),
                        width: c || k ? b.width() : b.outerWidth(),
                        height: c || k ? b.height() : b.outerHeight()
                    }
                }
            };
            a.fn.position = function(k) {
                if (!k || !k.of) return r.apply(this, arguments);
                k = a.extend({}, k);
                var u = a(k.of),
                    F = a.position.getWithinInfo(k.within),
                    q = a.position.getScrollInfo(F),
                    v = (k.collision || "flip").split(" "),
                    y = {};
                var p = c(u);
                u[0].preventDefault && (k.at = "left top");
                var t = p.width;
                var G = p.height;
                var x = p.offset;
                var w = a.extend({}, x);
                a.each(["my", "at"], function() {
                    var b = (k[this] || "").split(" ");
                    1 === b.length && (b = n.test(b[0]) ? b.concat(["center"]) : l.test(b[0]) ? ["center"].concat(b) : ["center", "center"]);
                    b[0] = n.test(b[0]) ? b[0] : "center";
                    b[1] = l.test(b[1]) ? b[1] : "center";
                    var c = g.exec(b[0]);
                    var a = g.exec(b[1]);
                    y[this] = [c ? c[0] : 0, a ? a[0] : 0];
                    k[this] = [m.exec(b[0])[0], m.exec(b[1])[0]]
                });
                1 === v.length && (v[1] = v[0]);
                "right" === k.at[0] ? w.left += t : "center" === k.at[0] && (w.left += t / 2);
                "bottom" === k.at[1] ? w.top += G : "center" === k.at[1] && (w.top +=
                    G / 2);
                var H = b(y.at, t, G);
                w.left += H[0];
                w.top += H[1];
                return this.each(function() {
                    var c, n = a(this),
                        l = n.outerWidth(),
                        g = n.outerHeight(),
                        m = parseInt(a.css(this, "marginLeft"), 10) || 0,
                        r = parseInt(a.css(this, "marginTop"), 10) || 0,
                        p = l + m + (parseInt(a.css(this, "marginRight"), 10) || 0) + q.width,
                        S = g + r + (parseInt(a.css(this, "marginBottom"), 10) || 0) + q.height,
                        z = a.extend({}, w),
                        I = b(y.my, n.outerWidth(), n.outerHeight());
                    "right" === k.my[0] ? z.left -= l : "center" === k.my[0] && (z.left -= l / 2);
                    "bottom" === k.my[1] ? z.top -= g : "center" === k.my[1] && (z.top -=
                        g / 2);
                    z.left += I[0];
                    z.top += I[1];
                    e || (z.left = h(z.left), z.top = h(z.top));
                    var T = {
                        marginLeft: m,
                        marginTop: r
                    };
                    a.each(["left", "top"], function(b, c) {
                        if (a.ui.position[v[b]]) a.ui.position[v[b]][c](z, {
                            targetWidth: t,
                            targetHeight: G,
                            elemWidth: l,
                            elemHeight: g,
                            collisionPosition: T,
                            collisionWidth: p,
                            collisionHeight: S,
                            offset: [H[0] + I[0], H[1] + I[1]],
                            my: k.my,
                            at: k.at,
                            within: F,
                            elem: n
                        })
                    });
                    k.using && (c = function(b) {
                        var c = x.left - z.left,
                            a = c + t - l,
                            e = x.top - z.top,
                            h = e + G - g,
                            F = {
                                target: {
                                    element: u,
                                    left: x.left,
                                    top: x.top,
                                    width: t,
                                    height: G
                                },
                                element: {
                                    element: n,
                                    left: z.left,
                                    top: z.top,
                                    width: l,
                                    height: g
                                },
                                horizontal: 0 > a ? "left" : 0 < c ? "right" : "center",
                                vertical: 0 > h ? "top" : 0 < e ? "bottom" : "middle"
                            };
                        t < l && f(c + a) < t && (F.horizontal = "center");
                        G < g && f(e + h) < G && (F.vertical = "middle");
                        d(f(c), f(a)) > d(f(e), f(h)) ? F.important = "horizontal" : F.important = "vertical";
                        k.using.call(this, b, F)
                    });
                    n.offset(a.extend(z, {
                        using: c
                    }))
                })
            };
            a.ui.position = {
                fit: {
                    left: function(b, c) {
                        var a = c.within,
                            k = a.isWindow ? a.scrollLeft : a.offset.left,
                            e = a.width,
                            u = b.left - c.collisionPosition.marginLeft;
                        a = k - u;
                        var f = u + c.collisionWidth -
                            e - k;
                        c.collisionWidth > e ? 0 < a && 0 >= f ? (c = b.left + a + c.collisionWidth - e - k, b.left += a - c) : b.left = 0 < f && 0 >= a ? k : a > f ? k + e - c.collisionWidth : k : b.left = 0 < a ? b.left + a : 0 < f ? b.left - f : d(b.left - u, b.left)
                    },
                    top: function(b, c) {
                        var a = c.within,
                            k = a.isWindow ? a.scrollTop : a.offset.top,
                            e = c.within.height,
                            u = b.top - c.collisionPosition.marginTop;
                        a = k - u;
                        var f = u + c.collisionHeight - e - k;
                        c.collisionHeight > e ? 0 < a && 0 >= f ? (c = b.top + a + c.collisionHeight - e - k, b.top += a - c) : b.top = 0 < f && 0 >= a ? k : a > f ? k + e - c.collisionHeight : k : b.top = 0 < a ? b.top + a : 0 < f ? b.top - f : d(b.top - u,
                            b.top)
                    }
                },
                flip: {
                    left: function(b, c) {
                        var a = c.within,
                            k = a.offset.left + a.scrollLeft,
                            e = a.width,
                            d = a.isWindow ? a.scrollLeft : a.offset.left,
                            u = b.left - c.collisionPosition.marginLeft;
                        a = u - d;
                        var h = u + c.collisionWidth - e - d;
                        u = "left" === c.my[0] ? -c.elemWidth : "right" === c.my[0] ? c.elemWidth : 0;
                        var n = "left" === c.at[0] ? c.targetWidth : "right" === c.at[0] ? -c.targetWidth : 0,
                            l = -2 * c.offset[0];
                        if (0 > a) {
                            if (c = b.left + u + n + l + c.collisionWidth - e - k, 0 > c || c < f(a)) b.left += u + n + l
                        } else 0 < h && (c = b.left - c.collisionPosition.marginLeft + u + n + l - d, 0 < c || f(c) < h) &&
                            (b.left += u + n + l)
                    },
                    top: function(b, c) {
                        var a = c.within,
                            k = a.offset.top + a.scrollTop,
                            e = a.height,
                            d = a.isWindow ? a.scrollTop : a.offset.top,
                            u = b.top - c.collisionPosition.marginTop;
                        a = u - d;
                        var h = u + c.collisionHeight - e - d;
                        u = "top" === c.my[1] ? -c.elemHeight : "bottom" === c.my[1] ? c.elemHeight : 0;
                        var n = "top" === c.at[1] ? c.targetHeight : "bottom" === c.at[1] ? -c.targetHeight : 0,
                            l = -2 * c.offset[1];
                        if (0 > a) {
                            if (c = b.top + u + n + l + c.collisionHeight - e - k, 0 > c || c < f(a)) b.top += u + n + l
                        } else 0 < h && (c = b.top - c.collisionPosition.marginTop + u + n + l - d, 0 < c || f(c) < h) && (b.top +=
                            u + n + l)
                    }
                },
                flipfit: {
                    left: function() {
                        a.ui.position.flip.left.apply(this, arguments);
                        a.ui.position.fit.left.apply(this, arguments)
                    },
                    top: function() {
                        a.ui.position.flip.top.apply(this, arguments);
                        a.ui.position.fit.top.apply(this, arguments)
                    }
                }
            };
            (function() {
                var b, c = document.getElementsByTagName("body")[0];
                var k = document.createElement("div");
                var d = document.createElement(c ? "div" : "body");
                var u = {
                    visibility: "hidden",
                    width: 0,
                    height: 0,
                    border: 0,
                    margin: 0,
                    background: "none"
                };
                c && a.extend(u, {
                    position: "absolute",
                    left: "-1000px",
                    top: "-1000px"
                });
                for (b in u) d.style[b] = u[b];
                d.appendChild(k);
                u = c || document.documentElement;
                u.insertBefore(d, u.firstChild);
                k.style.cssText = "position: absolute; left: 10.7432222px;";
                k = a(k).offset().left;
                e = 10 < k && 11 > k;
                d.innerHTML = "";
                u.removeChild(d)
            })()
        })();
        a.widget("ui.draggable", a.ui.mouse, {
            version: "1.11.4",
            widgetEventPrefix: "drag",
            options: {
                addClasses: !0,
                appendTo: "parent",
                axis: !1,
                connectToSortable: !1,
                containment: !1,
                cursor: "auto",
                cursorAt: !1,
                grid: !1,
                handle: !1,
                helper: "original",
                iframeFix: !1,
                opacity: !1,
                refreshPositions: !1,
                revert: !1,
                revertDuration: 500,
                scope: "default",
                scroll: !0,
                scrollSensitivity: 20,
                scrollSpeed: 20,
                snap: !1,
                snapMode: "both",
                snapTolerance: 20,
                stack: !1,
                zIndex: !1,
                drag: null,
                start: null,
                stop: null
            },
            _create: function() {
                "original" === this.options.helper && this._setPositionRelative();
                this.options.addClasses && this.element.addClass("ui-draggable");
                this.options.disabled && this.element.addClass("ui-draggable-disabled");
                this._setHandleClassName();
                this._mouseInit()
            },
            _setOption: function(b, c) {
                this._super(b,
                    c);
                "handle" === b && (this._removeHandleClassName(), this._setHandleClassName())
            },
            _destroy: function() {
                (this.helper || this.element).is(".ui-draggable-dragging") ? this.destroyOnClear = !0 : (this.element.removeClass("ui-draggable ui-draggable-dragging ui-draggable-disabled"), this._removeHandleClassName(), this._mouseDestroy())
            },
            _mouseCapture: function(b) {
                var c = this.options;
                this._blurActiveElement(b);
                if (this.helper || c.disabled || 0 < a(b.target).closest(".ui-resizable-handle").length) return !1;
                this.handle = this._getHandle(b);
                if (!this.handle) return !1;
                this._blockFrames(!0 === c.iframeFix ? "iframe" : c.iframeFix);
                return !0
            },
            _blockFrames: function(b) {
                this.iframeBlocks = this.document.find(b).map(function() {
                    var b = a(this);
                    return a("\x3cdiv\x3e").css("position", "absolute").appendTo(b.parent()).outerWidth(b.outerWidth()).outerHeight(b.outerHeight()).offset(b.offset())[0]
                })
            },
            _unblockFrames: function() {
                this.iframeBlocks && (this.iframeBlocks.remove(), delete this.iframeBlocks)
            },
            _blurActiveElement: function(b) {
                var c = this.document[0];
                if (this.handleElement.is(b.target)) try {
                    c.activeElement &&
                        "body" !== c.activeElement.nodeName.toLowerCase() && a(c.activeElement).blur()
                } catch (k) {}
            },
            _mouseStart: function(b) {
                var c = this.options;
                this.helper = this._createHelper(b);
                this.helper.addClass("ui-draggable-dragging");
                this._cacheHelperProportions();
                a.ui.ddmanager && (a.ui.ddmanager.current = this);
                this._cacheMargins();
                this.cssPosition = this.helper.css("position");
                this.scrollParent = this.helper.scrollParent(!0);
                this.offsetParent = this.helper.offsetParent();
                this.hasFixedAncestor = 0 < this.helper.parents().filter(function() {
                    return "fixed" ===
                        a(this).css("position")
                }).length;
                this.positionAbs = this.element.offset();
                this._refreshOffsets(b);
                this.originalPosition = this.position = this._generatePosition(b, !1);
                this.originalPageX = b.pageX;
                this.originalPageY = b.pageY;
                c.cursorAt && this._adjustOffsetFromHelper(c.cursorAt);
                this._setContainment();
                if (!1 === this._trigger("start", b)) return this._clear(), !1;
                this._cacheHelperProportions();
                a.ui.ddmanager && !c.dropBehaviour && a.ui.ddmanager.prepareOffsets(this, b);
                this._normalizeRightBottom();
                this._mouseDrag(b, !0);
                a.ui.ddmanager && a.ui.ddmanager.dragStart(this, b);
                return !0
            },
            _refreshOffsets: function(b) {
                this.offset = {
                    top: this.positionAbs.top - this.margins.top,
                    left: this.positionAbs.left - this.margins.left,
                    scroll: !1,
                    parent: this._getParentOffset(),
                    relative: this._getRelativeOffset()
                };
                this.offset.click = {
                    left: b.pageX - this.offset.left,
                    top: b.pageY - this.offset.top
                }
            },
            _mouseDrag: function(b, c) {
                this.hasFixedAncestor && (this.offset.parent = this._getParentOffset());
                this.position = this._generatePosition(b, !0);
                this.positionAbs = this._convertPositionTo("absolute");
                if (!c) {
                    c = this._uiHash();
                    if (!1 === this._trigger("drag", b, c)) return this._mouseUp({}), !1;
                    this.position = c.position
                }
                this.helper[0].style.left = this.position.left + "px";
                this.helper[0].style.top = this.position.top + "px";
                a.ui.ddmanager && a.ui.ddmanager.drag(this, b);
                return !1
            },
            _mouseStop: function(b) {
                var c = this,
                    k = !1;
                a.ui.ddmanager && !this.options.dropBehaviour && (k = a.ui.ddmanager.drop(this, b));
                this.dropped && (k = this.dropped, this.dropped = !1);
                "invalid" === this.options.revert && !k || "valid" === this.options.revert && k || !0 ===
                    this.options.revert || a.isFunction(this.options.revert) && this.options.revert.call(this.element, k) ? a(this.helper).animate(this.originalPosition, parseInt(this.options.revertDuration, 10), function() {
                        !1 !== c._trigger("stop", b) && c._clear()
                    }) : !1 !== this._trigger("stop", b) && this._clear();
                return !1
            },
            _mouseUp: function(b) {
                this._unblockFrames();
                a.ui.ddmanager && a.ui.ddmanager.dragStop(this, b);
                this.handleElement.is(b.target) && this.element.focus();
                return a.ui.mouse.prototype._mouseUp.call(this, b)
            },
            cancel: function() {
                this.helper.is(".ui-draggable-dragging") ?
                    this._mouseUp({}) : this._clear();
                return this
            },
            _getHandle: function(b) {
                return this.options.handle ? !!a(b.target).closest(this.element.find(this.options.handle)).length : !0
            },
            _setHandleClassName: function() {
                this.handleElement = this.options.handle ? this.element.find(this.options.handle) : this.element;
                this.handleElement.addClass("ui-draggable-handle")
            },
            _removeHandleClassName: function() {
                this.handleElement.removeClass("ui-draggable-handle")
            },
            _createHelper: function(b) {
                var c = this.options,
                    k = a.isFunction(c.helper);
                b = k ? a(c.helper.apply(this.element[0], [b])) : "clone" === c.helper ? this.element.clone().removeAttr("id") : this.element;
                b.parents("body").length || b.appendTo("parent" === c.appendTo ? this.element[0].parentNode : c.appendTo);
                k && b[0] === this.element[0] && this._setPositionRelative();
                b[0] === this.element[0] || /(fixed|absolute)/.test(b.css("position")) || b.css("position", "absolute");
                return b
            },
            _setPositionRelative: function() {
                /^(?:r|a|f)/.test(this.element.css("position")) || (this.element[0].style.position = "relative")
            },
            _adjustOffsetFromHelper: function(b) {
                "string" ===
                typeof b && (b = b.split(" "));
                a.isArray(b) && (b = {
                    left: +b[0],
                    top: +b[1] || 0
                });
                "left" in b && (this.offset.click.left = b.left + this.margins.left);
                "right" in b && (this.offset.click.left = this.helperProportions.width - b.right + this.margins.left);
                "top" in b && (this.offset.click.top = b.top + this.margins.top);
                "bottom" in b && (this.offset.click.top = this.helperProportions.height - b.bottom + this.margins.top)
            },
            _isRootNode: function(b) {
                return /(html|body)/i.test(b.tagName) || b === this.document[0]
            },
            _getParentOffset: function() {
                var b = this.offsetParent.offset(),
                    c = this.document[0];
                "absolute" === this.cssPosition && this.scrollParent[0] !== c && a.contains(this.scrollParent[0], this.offsetParent[0]) && (b.left += this.scrollParent.scrollLeft(), b.top += this.scrollParent.scrollTop());
                this._isRootNode(this.offsetParent[0]) && (b = {
                    top: 0,
                    left: 0
                });
                return {
                    top: b.top + (parseInt(this.offsetParent.css("borderTopWidth"), 10) || 0),
                    left: b.left + (parseInt(this.offsetParent.css("borderLeftWidth"), 10) || 0)
                }
            },
            _getRelativeOffset: function() {
                if ("relative" !== this.cssPosition) return {
                    top: 0,
                    left: 0
                };
                var b =
                    this.element.position(),
                    c = this._isRootNode(this.scrollParent[0]);
                return {
                    top: b.top - (parseInt(this.helper.css("top"), 10) || 0) + (c ? 0 : this.scrollParent.scrollTop()),
                    left: b.left - (parseInt(this.helper.css("left"), 10) || 0) + (c ? 0 : this.scrollParent.scrollLeft())
                }
            },
            _cacheMargins: function() {
                this.margins = {
                    left: parseInt(this.element.css("marginLeft"), 10) || 0,
                    top: parseInt(this.element.css("marginTop"), 10) || 0,
                    right: parseInt(this.element.css("marginRight"), 10) || 0,
                    bottom: parseInt(this.element.css("marginBottom"), 10) ||
                        0
                }
            },
            _cacheHelperProportions: function() {
                this.helperProportions = {
                    width: this.helper.outerWidth(),
                    height: this.helper.outerHeight()
                }
            },
            _setContainment: function() {
                var b;
                var c = this.options;
                var k = this.document[0];
                this.relativeContainer = null;
                if (c.containment)
                    if ("window" === c.containment) this.containment = [a(window).scrollLeft() - this.offset.relative.left - this.offset.parent.left, a(window).scrollTop() - this.offset.relative.top - this.offset.parent.top, a(window).scrollLeft() + a(window).width() - this.helperProportions.width -
                        this.margins.left, a(window).scrollTop() + (a(window).height() || k.body.parentNode.scrollHeight) - this.helperProportions.height - this.margins.top
                    ];
                    else if ("document" === c.containment) this.containment = [0, 0, a(k).width() - this.helperProportions.width - this.margins.left, (a(k).height() || k.body.parentNode.scrollHeight) - this.helperProportions.height - this.margins.top];
                else if (c.containment.constructor === Array) this.containment = c.containment;
                else {
                    if ("parent" === c.containment && (c.containment = this.helper[0].parentNode),
                        k = a(c.containment), b = k[0]) c = /(scroll|auto)/.test(k.css("overflow")), this.containment = [(parseInt(k.css("borderLeftWidth"), 10) || 0) + (parseInt(k.css("paddingLeft"), 10) || 0), (parseInt(k.css("borderTopWidth"), 10) || 0) + (parseInt(k.css("paddingTop"), 10) || 0), (c ? Math.max(b.scrollWidth, b.offsetWidth) : b.offsetWidth) - (parseInt(k.css("borderRightWidth"), 10) || 0) - (parseInt(k.css("paddingRight"), 10) || 0) - this.helperProportions.width - this.margins.left - this.margins.right, (c ? Math.max(b.scrollHeight, b.offsetHeight) : b.offsetHeight) -
                        (parseInt(k.css("borderBottomWidth"), 10) || 0) - (parseInt(k.css("paddingBottom"), 10) || 0) - this.helperProportions.height - this.margins.top - this.margins.bottom
                    ], this.relativeContainer = k
                } else this.containment = null
            },
            _convertPositionTo: function(b, c) {
                c || (c = this.position);
                b = "absolute" === b ? 1 : -1;
                var a = this._isRootNode(this.scrollParent[0]);
                return {
                    top: c.top + this.offset.relative.top * b + this.offset.parent.top * b - ("fixed" === this.cssPosition ? -this.offset.scroll.top : a ? 0 : this.offset.scroll.top) * b,
                    left: c.left + this.offset.relative.left *
                        b + this.offset.parent.left * b - ("fixed" === this.cssPosition ? -this.offset.scroll.left : a ? 0 : this.offset.scroll.left) * b
                }
            },
            _generatePosition: function(b, c) {
                var a = this.options,
                    e = this._isRootNode(this.scrollParent[0]);
                var d = b.pageX;
                var f = b.pageY;
                e && this.offset.scroll || (this.offset.scroll = {
                    top: this.scrollParent.scrollTop(),
                    left: this.scrollParent.scrollLeft()
                });
                if (c) {
                    if (this.containment) {
                        if (this.relativeContainer) {
                            var h = this.relativeContainer.offset();
                            h = [this.containment[0] + h.left, this.containment[1] + h.top, this.containment[2] +
                                h.left, this.containment[3] + h.top
                            ]
                        } else h = this.containment;
                        b.pageX - this.offset.click.left < h[0] && (d = h[0] + this.offset.click.left);
                        b.pageY - this.offset.click.top < h[1] && (f = h[1] + this.offset.click.top);
                        b.pageX - this.offset.click.left > h[2] && (d = h[2] + this.offset.click.left);
                        b.pageY - this.offset.click.top > h[3] && (f = h[3] + this.offset.click.top)
                    }
                    a.grid && (f = a.grid[1] ? this.originalPageY + Math.round((f - this.originalPageY) / a.grid[1]) * a.grid[1] : this.originalPageY, f = h ? f - this.offset.click.top >= h[1] || f - this.offset.click.top >
                        h[3] ? f : f - this.offset.click.top >= h[1] ? f - a.grid[1] : f + a.grid[1] : f, d = a.grid[0] ? this.originalPageX + Math.round((d - this.originalPageX) / a.grid[0]) * a.grid[0] : this.originalPageX, d = h ? d - this.offset.click.left >= h[0] || d - this.offset.click.left > h[2] ? d : d - this.offset.click.left >= h[0] ? d - a.grid[0] : d + a.grid[0] : d);
                    "y" === a.axis && (d = this.originalPageX);
                    "x" === a.axis && (f = this.originalPageY)
                }
                return {
                    top: f - this.offset.click.top - this.offset.relative.top - this.offset.parent.top + ("fixed" === this.cssPosition ? -this.offset.scroll.top :
                        e ? 0 : this.offset.scroll.top),
                    left: d - this.offset.click.left - this.offset.relative.left - this.offset.parent.left + ("fixed" === this.cssPosition ? -this.offset.scroll.left : e ? 0 : this.offset.scroll.left)
                }
            },
            _clear: function() {
                this.helper.removeClass("ui-draggable-dragging");
                this.helper[0] === this.element[0] || this.cancelHelperRemoval || this.helper.remove();
                this.helper = null;
                this.cancelHelperRemoval = !1;
                this.destroyOnClear && this.destroy()
            },
            _normalizeRightBottom: function() {
                "y" !== this.options.axis && "auto" !== this.helper.css("right") &&
                    (this.helper.width(this.helper.width()), this.helper.css("right", "auto"));
                "x" !== this.options.axis && "auto" !== this.helper.css("bottom") && (this.helper.height(this.helper.height()), this.helper.css("bottom", "auto"))
            },
            _trigger: function(b, c, k) {
                k = k || this._uiHash();
                a.ui.plugin.call(this, b, [c, k, this], !0);
                /^(drag|start|stop)/.test(b) && (this.positionAbs = this._convertPositionTo("absolute"), k.offset = this.positionAbs);
                return a.Widget.prototype._trigger.call(this, b, c, k)
            },
            plugins: {},
            _uiHash: function() {
                return {
                    helper: this.helper,
                    position: this.position,
                    originalPosition: this.originalPosition,
                    offset: this.positionAbs
                }
            }
        });
        a.ui.plugin.add("draggable", "connectToSortable", {
            start: function(b, c, k) {
                var e = a.extend({}, c, {
                    item: k.element
                });
                k.sortables = [];
                a(k.options.connectToSortable).each(function() {
                    var c = a(this).sortable("instance");
                    c && !c.options.disabled && (k.sortables.push(c), c.refreshPositions(), c._trigger("activate", b, e))
                })
            },
            stop: function(b, c, k) {
                var e = a.extend({}, c, {
                    item: k.element
                });
                k.cancelHelperRemoval = !1;
                a.each(k.sortables, function() {
                    this.isOver ?
                        (this.isOver = 0, k.cancelHelperRemoval = !0, this.cancelHelperRemoval = !1, this._storedCSS = {
                            position: this.placeholder.css("position"),
                            top: this.placeholder.css("top"),
                            left: this.placeholder.css("left")
                        }, this._mouseStop(b), this.options.helper = this.options._helper) : (this.cancelHelperRemoval = !0, this._trigger("deactivate", b, e))
                })
            },
            drag: function(b, c, k) {
                a.each(k.sortables, function() {
                    var e = !1,
                        d = this;
                    d.positionAbs = k.positionAbs;
                    d.helperProportions = k.helperProportions;
                    d.offset.click = k.offset.click;
                    d._intersectsWith(d.containerCache) &&
                        (e = !0, a.each(k.sortables, function() {
                            this.positionAbs = k.positionAbs;
                            this.helperProportions = k.helperProportions;
                            this.offset.click = k.offset.click;
                            this !== d && this._intersectsWith(this.containerCache) && a.contains(d.element[0], this.element[0]) && (e = !1);
                            return e
                        }));
                    e ? (d.isOver || (d.isOver = 1, k._parent = c.helper.parent(), d.currentItem = c.helper.appendTo(d.element).data("ui-sortable-item", !0), d.options._helper = d.options.helper, d.options.helper = function() {
                        return c.helper[0]
                    }, b.target = d.currentItem[0], d._mouseCapture(b,
                        !0), d._mouseStart(b, !0, !0), d.offset.click.top = k.offset.click.top, d.offset.click.left = k.offset.click.left, d.offset.parent.left -= k.offset.parent.left - d.offset.parent.left, d.offset.parent.top -= k.offset.parent.top - d.offset.parent.top, k._trigger("toSortable", b), k.dropped = d.element, a.each(k.sortables, function() {
                        this.refreshPositions()
                    }), k.currentItem = k.element, d.fromOutside = k), d.currentItem && (d._mouseDrag(b), c.position = d.position)) : d.isOver && (d.isOver = 0, d.cancelHelperRemoval = !0, d.options._revert = d.options.revert,
                        d.options.revert = !1, d._trigger("out", b, d._uiHash(d)), d._mouseStop(b, !0), d.options.revert = d.options._revert, d.options.helper = d.options._helper, d.placeholder && d.placeholder.remove(), c.helper.appendTo(k._parent), k._refreshOffsets(b), c.position = k._generatePosition(b, !0), k._trigger("fromSortable", b), k.dropped = !1, a.each(k.sortables, function() {
                            this.refreshPositions()
                        }))
                })
            }
        });
        a.ui.plugin.add("draggable", "cursor", {
            start: function(b, c, k) {
                b = a("body");
                k = k.options;
                b.css("cursor") && (k._cursor = b.css("cursor"));
                b.css("cursor",
                    k.cursor)
            },
            stop: function(b, c, k) {
                b = k.options;
                b._cursor && a("body").css("cursor", b._cursor)
            }
        });
        a.ui.plugin.add("draggable", "opacity", {
            start: function(b, c, k) {
                b = a(c.helper);
                k = k.options;
                b.css("opacity") && (k._opacity = b.css("opacity"));
                b.css("opacity", k.opacity)
            },
            stop: function(b, c, k) {
                b = k.options;
                b._opacity && a(c.helper).css("opacity", b._opacity)
            }
        });
        a.ui.plugin.add("draggable", "scroll", {
            start: function(b, c, a) {
                a.scrollParentNotHidden || (a.scrollParentNotHidden = a.helper.scrollParent(!1));
                a.scrollParentNotHidden[0] !==
                    a.document[0] && "HTML" !== a.scrollParentNotHidden[0].tagName && (a.overflowOffset = a.scrollParentNotHidden.offset())
            },
            drag: function(b, c, k) {
                c = k.options;
                var e = !1,
                    d = k.scrollParentNotHidden[0],
                    f = k.document[0];
                d !== f && "HTML" !== d.tagName ? (c.axis && "x" === c.axis || (k.overflowOffset.top + d.offsetHeight - b.pageY < c.scrollSensitivity ? d.scrollTop = e = d.scrollTop + c.scrollSpeed : b.pageY - k.overflowOffset.top < c.scrollSensitivity && (d.scrollTop = e = d.scrollTop - c.scrollSpeed)), c.axis && "y" === c.axis || (k.overflowOffset.left + d.offsetWidth -
                    b.pageX < c.scrollSensitivity ? d.scrollLeft = e = d.scrollLeft + c.scrollSpeed : b.pageX - k.overflowOffset.left < c.scrollSensitivity && (d.scrollLeft = e = d.scrollLeft - c.scrollSpeed))) : (c.axis && "x" === c.axis || (b.pageY - a(f).scrollTop() < c.scrollSensitivity ? e = a(f).scrollTop(a(f).scrollTop() - c.scrollSpeed) : a(window).height() - (b.pageY - a(f).scrollTop()) < c.scrollSensitivity && (e = a(f).scrollTop(a(f).scrollTop() + c.scrollSpeed))), c.axis && "y" === c.axis || (b.pageX - a(f).scrollLeft() < c.scrollSensitivity ? e = a(f).scrollLeft(a(f).scrollLeft() -
                    c.scrollSpeed) : a(window).width() - (b.pageX - a(f).scrollLeft()) < c.scrollSensitivity && (e = a(f).scrollLeft(a(f).scrollLeft() + c.scrollSpeed))));
                !1 !== e && a.ui.ddmanager && !c.dropBehaviour && a.ui.ddmanager.prepareOffsets(k, b)
            }
        });
        a.ui.plugin.add("draggable", "snap", {
            start: function(b, c, k) {
                b = k.options;
                k.snapElements = [];
                a(b.snap.constructor !== String ? b.snap.items || ":data(ui-draggable)" : b.snap).each(function() {
                    var b = a(this),
                        c = b.offset();
                    this !== k.element[0] && k.snapElements.push({
                        item: this,
                        width: b.outerWidth(),
                        height: b.outerHeight(),
                        top: c.top,
                        left: c.left
                    })
                })
            },
            drag: function(b, c, k) {
                var e, d = k.options,
                    f = d.snapTolerance,
                    h = c.offset.left,
                    n = h + k.helperProportions.width,
                    l = c.offset.top,
                    g = l + k.helperProportions.height;
                for (e = k.snapElements.length - 1; 0 <= e; e--) {
                    var m = k.snapElements[e].left - k.margins.left;
                    var q = m + k.snapElements[e].width;
                    var r = k.snapElements[e].top - k.margins.top;
                    var v = r + k.snapElements[e].height;
                    if (n < m - f || h > q + f || g < r - f || l > v + f || !a.contains(k.snapElements[e].item.ownerDocument, k.snapElements[e].item)) k.snapElements[e].snapping && k.options.snap.release &&
                        k.options.snap.release.call(k.element, b, a.extend(k._uiHash(), {
                            snapItem: k.snapElements[e].item
                        })), k.snapElements[e].snapping = !1;
                    else {
                        if ("inner" !== d.snapMode) {
                            var y = Math.abs(r - g) <= f;
                            var p = Math.abs(v - l) <= f;
                            var t = Math.abs(m - n) <= f;
                            var x = Math.abs(q - h) <= f;
                            y && (c.position.top = k._convertPositionTo("relative", {
                                top: r - k.helperProportions.height,
                                left: 0
                            }).top);
                            p && (c.position.top = k._convertPositionTo("relative", {
                                top: v,
                                left: 0
                            }).top);
                            t && (c.position.left = k._convertPositionTo("relative", {
                                top: 0,
                                left: m - k.helperProportions.width
                            }).left);
                            x && (c.position.left = k._convertPositionTo("relative", {
                                top: 0,
                                left: q
                            }).left)
                        }
                        var w = y || p || t || x;
                        "outer" !== d.snapMode && (y = Math.abs(r - l) <= f, p = Math.abs(v - g) <= f, t = Math.abs(m - h) <= f, x = Math.abs(q - n) <= f, y && (c.position.top = k._convertPositionTo("relative", {
                            top: r,
                            left: 0
                        }).top), p && (c.position.top = k._convertPositionTo("relative", {
                            top: v - k.helperProportions.height,
                            left: 0
                        }).top), t && (c.position.left = k._convertPositionTo("relative", {
                            top: 0,
                            left: m
                        }).left), x && (c.position.left = k._convertPositionTo("relative", {
                            top: 0,
                            left: q -
                                k.helperProportions.width
                        }).left));
                        !k.snapElements[e].snapping && (y || p || t || x || w) && k.options.snap.snap && k.options.snap.snap.call(k.element, b, a.extend(k._uiHash(), {
                            snapItem: k.snapElements[e].item
                        }));
                        k.snapElements[e].snapping = y || p || t || x || w
                    }
                }
            }
        });
        a.ui.plugin.add("draggable", "stack", {
            start: function(b, c, k) {
                b = a.makeArray(a(k.options.stack)).sort(function(b, c) {
                    return (parseInt(a(b).css("zIndex"), 10) || 0) - (parseInt(a(c).css("zIndex"), 10) || 0)
                });
                if (b.length) {
                    var e = parseInt(a(b[0]).css("zIndex"), 10) || 0;
                    a(b).each(function(b) {
                        a(this).css("zIndex",
                            e + b)
                    });
                    this.css("zIndex", e + b.length)
                }
            }
        });
        a.ui.plugin.add("draggable", "zIndex", {
            start: function(b, c, k) {
                b = a(c.helper);
                k = k.options;
                b.css("zIndex") && (k._zIndex = b.css("zIndex"));
                b.css("zIndex", k.zIndex)
            },
            stop: function(b, c, k) {
                b = k.options;
                b._zIndex && a(c.helper).css("zIndex", b._zIndex)
            }
        });
        a.widget("ui.droppable", {
            version: "1.11.4",
            widgetEventPrefix: "drop",
            options: {
                accept: "*",
                activeClass: !1,
                addClasses: !0,
                greedy: !1,
                hoverClass: !1,
                scope: "default",
                tolerance: "intersect",
                activate: null,
                deactivate: null,
                drop: null,
                out: null,
                over: null
            },
            _create: function() {
                var b, c = this.options,
                    k = c.accept;
                this.isover = !1;
                this.isout = !0;
                this.accept = a.isFunction(k) ? k : function(b) {
                    return b.is(k)
                };
                this.proportions = function() {
                    if (arguments.length) b = arguments[0];
                    else return b ? b : b = {
                        width: this.element[0].offsetWidth,
                        height: this.element[0].offsetHeight
                    }
                };
                this._addToManager(c.scope);
                c.addClasses && this.element.addClass("ui-droppable")
            },
            _addToManager: function(b) {
                a.ui.ddmanager.droppables[b] = a.ui.ddmanager.droppables[b] || [];
                a.ui.ddmanager.droppables[b].push(this)
            },
            _splice: function(b) {
                for (var c = 0; c < b.length; c++) b[c] === this && b.splice(c, 1)
            },
            _destroy: function() {
                this._splice(a.ui.ddmanager.droppables[this.options.scope]);
                this.element.removeClass("ui-droppable ui-droppable-disabled")
            },
            _setOption: function(b, c) {
                "accept" === b ? this.accept = a.isFunction(c) ? c : function(b) {
                    return b.is(c)
                } : "scope" === b && (this._splice(a.ui.ddmanager.droppables[this.options.scope]), this._addToManager(c));
                this._super(b, c)
            },
            _activate: function(b) {
                var c = a.ui.ddmanager.current;
                this.options.activeClass &&
                    this.element.addClass(this.options.activeClass);
                c && this._trigger("activate", b, this.ui(c))
            },
            _deactivate: function(b) {
                var c = a.ui.ddmanager.current;
                this.options.activeClass && this.element.removeClass(this.options.activeClass);
                c && this._trigger("deactivate", b, this.ui(c))
            },
            _over: function(b) {
                var c = a.ui.ddmanager.current;
                c && (c.currentItem || c.element)[0] !== this.element[0] && this.accept.call(this.element[0], c.currentItem || c.element) && (this.options.hoverClass && this.element.addClass(this.options.hoverClass), this._trigger("over",
                    b, this.ui(c)))
            },
            _out: function(b) {
                var c = a.ui.ddmanager.current;
                c && (c.currentItem || c.element)[0] !== this.element[0] && this.accept.call(this.element[0], c.currentItem || c.element) && (this.options.hoverClass && this.element.removeClass(this.options.hoverClass), this._trigger("out", b, this.ui(c)))
            },
            _drop: function(b, c) {
                var k = c || a.ui.ddmanager.current,
                    e = !1;
                if (!k || (k.currentItem || k.element)[0] === this.element[0]) return !1;
                this.element.find(":data(ui-droppable)").not(".ui-draggable-dragging").each(function() {
                    var c = a(this).droppable("instance");
                    if (c.options.greedy && !c.options.disabled && c.options.scope === k.options.scope && c.accept.call(c.element[0], k.currentItem || k.element) && a.ui.intersect(k, a.extend(c, {
                            offset: c.element.offset()
                        }), c.options.tolerance, b)) return e = !0, !1
                });
                return e ? !1 : this.accept.call(this.element[0], k.currentItem || k.element) ? (this.options.activeClass && this.element.removeClass(this.options.activeClass), this.options.hoverClass && this.element.removeClass(this.options.hoverClass), this._trigger("drop", b, this.ui(k)), this.element) :
                    !1
            },
            ui: function(b) {
                return {
                    draggable: b.currentItem || b.element,
                    helper: b.helper,
                    position: b.position,
                    offset: b.positionAbs
                }
            }
        });
        a.ui.intersect = function() {
            return function(b, c, a, e) {
                if (!c.offset) return !1;
                var k = (b.positionAbs || b.position.absolute).left + b.margins.left,
                    d = (b.positionAbs || b.position.absolute).top + b.margins.top,
                    f = k + b.helperProportions.width,
                    u = d + b.helperProportions.height,
                    h = c.offset.left,
                    n = c.offset.top,
                    l = h + c.proportions().width,
                    g = n + c.proportions().height;
                switch (a) {
                    case "fit":
                        return h <= k && f <= l && n <=
                            d && u <= g;
                    case "intersect":
                        return h < k + b.helperProportions.width / 2 && f - b.helperProportions.width / 2 < l && n < d + b.helperProportions.height / 2 && u - b.helperProportions.height / 2 < g;
                    case "pointer":
                        b = e.pageY;
                        a = c.proportions().height;
                        if (n = b >= n && b < n + a) e = e.pageX, c = c.proportions().width, n = e >= h && e < h + c;
                        return n;
                    case "touch":
                        return (d >= n && d <= g || u >= n && u <= g || d < n && u > g) && (k >= h && k <= l || f >= h && f <= l || k < h && f > l);
                    default:
                        return !1
                }
            }
        }();
        a.ui.ddmanager = {
            current: null,
            droppables: {
                "default": []
            },
            prepareOffsets: function(b, c) {
                var k, e = a.ui.ddmanager.droppables[b.options.scope] || [],
                    d = c ? c.type : null,
                    f = (b.currentItem || b.element).find(":data(ui-droppable)").addBack();
                var h = 0;
                a: for (; h < e.length; h++)
                    if (!(e[h].options.disabled || b && !e[h].accept.call(e[h].element[0], b.currentItem || b.element))) {
                        for (k = 0; k < f.length; k++)
                            if (f[k] === e[h].element[0]) {
                                e[h].proportions().height = 0;
                                continue a
                            } e[h].visible = "none" !== e[h].element.css("display");
                        e[h].visible && ("mousedown" === d && e[h]._activate.call(e[h], c), e[h].offset = e[h].element.offset(), e[h].proportions({
                            width: e[h].element[0].offsetWidth,
                            height: e[h].element[0].offsetHeight
                        }))
                    }
            },
            drop: function(b, c) {
                var k = !1;
                a.each((a.ui.ddmanager.droppables[b.options.scope] || []).slice(), function() {
                    this.options && (!this.options.disabled && this.visible && a.ui.intersect(b, this, this.options.tolerance, c) && (k = this._drop.call(this, c) || k), !this.options.disabled && this.visible && this.accept.call(this.element[0], b.currentItem || b.element) && (this.isout = !0, this.isover = !1, this._deactivate.call(this, c)))
                });
                return k
            },
            dragStart: function(b, c) {
                b.element.parentsUntil("body").bind("scroll.droppable", function() {
                    b.options.refreshPositions ||
                        a.ui.ddmanager.prepareOffsets(b, c)
                })
            },
            drag: function(b, c) {
                b.options.refreshPositions && a.ui.ddmanager.prepareOffsets(b, c);
                a.each(a.ui.ddmanager.droppables[b.options.scope] || [], function() {
                    if (!this.options.disabled && !this.greedyChild && this.visible) {
                        var k = a.ui.intersect(b, this, this.options.tolerance, c);
                        var e = !k && this.isover ? "isout" : k && !this.isover ? "isover" : null;
                        if (e) {
                            if (this.options.greedy) {
                                var d = this.options.scope;
                                k = this.element.parents(":data(ui-droppable)").filter(function() {
                                    return a(this).droppable("instance").options.scope ===
                                        d
                                });
                                if (k.length) {
                                    var f = a(k[0]).droppable("instance");
                                    f.greedyChild = "isover" === e
                                }
                            }
                            f && "isover" === e && (f.isover = !1, f.isout = !0, f._out.call(f, c));
                            this[e] = !0;
                            this["isout" === e ? "isover" : "isout"] = !1;
                            this["isover" === e ? "_over" : "_out"].call(this, c);
                            f && "isout" === e && (f.isout = !1, f.isover = !0, f._over.call(f, c))
                        }
                    }
                })
            },
            dragStop: function(b, c) {
                b.element.parentsUntil("body").unbind("scroll.droppable");
                b.options.refreshPositions || a.ui.ddmanager.prepareOffsets(b, c)
            }
        };
        a.widget("ui.resizable", a.ui.mouse, {
            version: "1.11.4",
            widgetEventPrefix: "resize",
            options: {
                alsoResize: !1,
                animate: !1,
                animateDuration: "slow",
                animateEasing: "swing",
                aspectRatio: !1,
                autoHide: !1,
                containment: !1,
                ghost: !1,
                grid: !1,
                handles: "e,s,se",
                helper: !1,
                maxHeight: null,
                maxWidth: null,
                minHeight: 10,
                minWidth: 10,
                zIndex: 90,
                resize: null,
                start: null,
                stop: null
            },
            _num: function(b) {
                return parseInt(b, 10) || 0
            },
            _isNumber: function(b) {
                return !isNaN(parseInt(b, 10))
            },
            _hasScroll: function(b, c) {
                if ("hidden" === a(b).css("overflow")) return !1;
                c = c && "left" === c ? "scrollLeft" : "scrollTop";
                if (0 < b[c]) return !0;
                b[c] = 1;
                var k = 0 <
                    b[c];
                b[c] = 0;
                return k
            },
            _create: function() {
                var b, c = this,
                    k = this.options;
                this.element.addClass("ui-resizable");
                a.extend(this, {
                    _aspectRatio: !!k.aspectRatio,
                    aspectRatio: k.aspectRatio,
                    originalElement: this.element,
                    _proportionallyResizeElements: [],
                    _helper: k.helper || k.ghost || k.animate ? k.helper || "ui-resizable-helper" : null
                });
                this.element[0].nodeName.match(/^(canvas|textarea|input|select|button|img)$/i) && (this.element.wrap(a("\x3cdiv class\x3d'ui-wrapper' style\x3d'overflow: hidden;'\x3e\x3c/div\x3e").css({
                    position: this.element.css("position"),
                    width: this.element.outerWidth(),
                    height: this.element.outerHeight(),
                    top: this.element.css("top"),
                    left: this.element.css("left")
                })), this.element = this.element.parent().data("ui-resizable", this.element.resizable("instance")), this.elementIsWrapper = !0, this.element.css({
                    marginLeft: this.originalElement.css("marginLeft"),
                    marginTop: this.originalElement.css("marginTop"),
                    marginRight: this.originalElement.css("marginRight"),
                    marginBottom: this.originalElement.css("marginBottom")
                }), this.originalElement.css({
                    marginLeft: 0,
                    marginTop: 0,
                    marginRight: 0,
                    marginBottom: 0
                }), this.originalResizeStyle = this.originalElement.css("resize"), this.originalElement.css("resize", "none"), this._proportionallyResizeElements.push(this.originalElement.css({
                    position: "static",
                    zoom: 1,
                    display: "block"
                })), this.originalElement.css({
                    margin: this.originalElement.css("margin")
                }), this._proportionallyResize());
                this.handles = k.handles || (a(".ui-resizable-handle", this.element).length ? {
                    n: ".ui-resizable-n",
                    e: ".ui-resizable-e",
                    s: ".ui-resizable-s",
                    w: ".ui-resizable-w",
                    se: ".ui-resizable-se",
                    sw: ".ui-resizable-sw",
                    ne: ".ui-resizable-ne",
                    nw: ".ui-resizable-nw"
                } : "e,s,se");
                this._handles = a();
                if (this.handles.constructor === String) {
                    "all" === this.handles && (this.handles = "n,e,s,w,se,sw,ne,nw");
                    var e = this.handles.split(",");
                    this.handles = {};
                    for (b = 0; b < e.length; b++) {
                        var d = a.trim(e[b]);
                        var f = "ui-resizable-" + d;
                        var h = a("\x3cdiv class\x3d'ui-resizable-handle " + f + "'\x3e\x3c/div\x3e");
                        h.css({
                            zIndex: k.zIndex
                        });
                        "se" === d && h.addClass("ui-icon ui-icon-gripsmall-diagonal-se");
                        this.handles[d] =
                            ".ui-resizable-" + d;
                        this.element.append(h)
                    }
                }
                this._renderAxis = function(b) {
                    var k;
                    b = b || this.element;
                    for (k in this.handles) {
                        if (this.handles[k].constructor === String) this.handles[k] = this.element.children(this.handles[k]).first().show();
                        else if (this.handles[k].jquery || this.handles[k].nodeType) this.handles[k] = a(this.handles[k]), this._on(this.handles[k], {
                            mousedown: c._mouseDown
                        });
                        if (this.elementIsWrapper && this.originalElement[0].nodeName.match(/^(textarea|input|select|button)$/i)) {
                            var e = a(this.handles[k], this.element);
                            var d = /sw|ne|nw|se|n|s/.test(k) ? e.outerHeight() : e.outerWidth();
                            e = ["padding", /ne|nw|n/.test(k) ? "Top" : /se|sw|s/.test(k) ? "Bottom" : /^e$/.test(k) ? "Right" : "Left"].join("");
                            b.css(e, d);
                            this._proportionallyResize()
                        }
                        this._handles = this._handles.add(this.handles[k])
                    }
                };
                this._renderAxis(this.element);
                this._handles = this._handles.add(this.element.find(".ui-resizable-handle"));
                this._handles.disableSelection();
                this._handles.mouseover(function() {
                    c.resizing || (this.className && (h = this.className.match(/ui-resizable-(se|sw|ne|nw|n|e|s|w)/i)),
                        c.axis = h && h[1] ? h[1] : "se")
                });
                k.autoHide && (this._handles.hide(), a(this.element).addClass("ui-resizable-autohide").mouseenter(function() {
                    k.disabled || (a(this).removeClass("ui-resizable-autohide"), c._handles.show())
                }).mouseleave(function() {
                    k.disabled || c.resizing || (a(this).addClass("ui-resizable-autohide"), c._handles.hide())
                }));
                this._mouseInit()
            },
            _destroy: function() {
                this._mouseDestroy();
                var b = function(b) {
                    a(b).removeClass("ui-resizable ui-resizable-disabled ui-resizable-resizing").removeData("resizable").removeData("ui-resizable").unbind(".resizable").find(".ui-resizable-handle").remove()
                };
                if (this.elementIsWrapper) {
                    b(this.element);
                    var c = this.element;
                    this.originalElement.css({
                        position: c.css("position"),
                        width: c.outerWidth(),
                        height: c.outerHeight(),
                        top: c.css("top"),
                        left: c.css("left")
                    }).insertAfter(c);
                    c.remove()
                }
                this.originalElement.css("resize", this.originalResizeStyle);
                b(this.originalElement);
                return this
            },
            _mouseCapture: function(b) {
                var c, k = !1;
                for (c in this.handles) {
                    var e = a(this.handles[c])[0];
                    if (e === b.target || a.contains(e, b.target)) k = !0
                }
                return !this.options.disabled && k
            },
            _mouseStart: function(b) {
                var c =
                    this.options,
                    k = this.element;
                this.resizing = !0;
                this._renderProxy();
                var e = this._num(this.helper.css("left"));
                var d = this._num(this.helper.css("top"));
                c.containment && (e += a(c.containment).scrollLeft() || 0, d += a(c.containment).scrollTop() || 0);
                this.offset = this.helper.offset();
                this.position = {
                    left: e,
                    top: d
                };
                this.size = this._helper ? {
                    width: this.helper.width(),
                    height: this.helper.height()
                } : {
                    width: k.width(),
                    height: k.height()
                };
                this.originalSize = this._helper ? {
                    width: k.outerWidth(),
                    height: k.outerHeight()
                } : {
                    width: k.width(),
                    height: k.height()
                };
                this.sizeDiff = {
                    width: k.outerWidth() - k.width(),
                    height: k.outerHeight() - k.height()
                };
                this.originalPosition = {
                    left: e,
                    top: d
                };
                this.originalMousePosition = {
                    left: b.pageX,
                    top: b.pageY
                };
                this.aspectRatio = "number" === typeof c.aspectRatio ? c.aspectRatio : this.originalSize.width / this.originalSize.height || 1;
                e = a(".ui-resizable-" + this.axis).css("cursor");
                a("body").css("cursor", "auto" === e ? this.axis + "-resize" : e);
                k.addClass("ui-resizable-resizing");
                this._propagate("start", b);
                return !0
            },
            _mouseDrag: function(b) {
                var c =
                    this.originalMousePosition;
                var k = b.pageX - c.left || 0;
                c = b.pageY - c.top || 0;
                var e = this._change[this.axis];
                this._updatePrevProperties();
                if (!e) return !1;
                k = e.apply(this, [b, k, c]);
                this._updateVirtualBoundaries(b.shiftKey);
                if (this._aspectRatio || b.shiftKey) k = this._updateRatio(k, b);
                k = this._respectSize(k, b);
                this._updateCache(k);
                this._propagate("resize", b);
                k = this._applyChanges();
                !this._helper && this._proportionallyResizeElements.length && this._proportionallyResize();
                a.isEmptyObject(k) || (this._updatePrevProperties(),
                    this._trigger("resize", b, this.ui()), this._applyChanges());
                return !1
            },
            _mouseStop: function(b) {
                this.resizing = !1;
                var c, k = this.options;
                if (this._helper) {
                    var e = this._proportionallyResizeElements;
                    e = (c = e.length && /textarea/i.test(e[0].nodeName)) && this._hasScroll(e[0], "left") ? 0 : this.sizeDiff.height;
                    c = c ? 0 : this.sizeDiff.width;
                    c = {
                        width: this.helper.width() - c,
                        height: this.helper.height() - e
                    };
                    e = parseInt(this.element.css("left"), 10) + (this.position.left - this.originalPosition.left) || null;
                    var d = parseInt(this.element.css("top"),
                        10) + (this.position.top - this.originalPosition.top) || null;
                    k.animate || this.element.css(a.extend(c, {
                        top: d,
                        left: e
                    }));
                    this.helper.height(this.size.height);
                    this.helper.width(this.size.width);
                    this._helper && !k.animate && this._proportionallyResize()
                }
                a("body").css("cursor", "auto");
                this.element.removeClass("ui-resizable-resizing");
                this._propagate("stop", b);
                this._helper && this.helper.remove();
                return !1
            },
            _updatePrevProperties: function() {
                this.prevPosition = {
                    top: this.position.top,
                    left: this.position.left
                };
                this.prevSize = {
                    width: this.size.width,
                    height: this.size.height
                }
            },
            _applyChanges: function() {
                var b = {};
                this.position.top !== this.prevPosition.top && (b.top = this.position.top + "px");
                this.position.left !== this.prevPosition.left && (b.left = this.position.left + "px");
                this.size.width !== this.prevSize.width && (b.width = this.size.width + "px");
                this.size.height !== this.prevSize.height && (b.height = this.size.height + "px");
                this.helper.css(b);
                return b
            },
            _updateVirtualBoundaries: function(b) {
                var c = this.options;
                c = {
                    minWidth: this._isNumber(c.minWidth) ?
                        c.minWidth : 0,
                    maxWidth: this._isNumber(c.maxWidth) ? c.maxWidth : Infinity,
                    minHeight: this._isNumber(c.minHeight) ? c.minHeight : 0,
                    maxHeight: this._isNumber(c.maxHeight) ? c.maxHeight : Infinity
                };
                if (this._aspectRatio || b) {
                    b = c.minHeight * this.aspectRatio;
                    var a = c.minWidth / this.aspectRatio;
                    var e = c.maxHeight * this.aspectRatio;
                    var d = c.maxWidth / this.aspectRatio;
                    b > c.minWidth && (c.minWidth = b);
                    a > c.minHeight && (c.minHeight = a);
                    e < c.maxWidth && (c.maxWidth = e);
                    d < c.maxHeight && (c.maxHeight = d)
                }
                this._vBoundaries = c
            },
            _updateCache: function(b) {
                this.offset =
                    this.helper.offset();
                this._isNumber(b.left) && (this.position.left = b.left);
                this._isNumber(b.top) && (this.position.top = b.top);
                this._isNumber(b.height) && (this.size.height = b.height);
                this._isNumber(b.width) && (this.size.width = b.width)
            },
            _updateRatio: function(b) {
                var c = this.position,
                    a = this.size,
                    e = this.axis;
                this._isNumber(b.height) ? b.width = b.height * this.aspectRatio : this._isNumber(b.width) && (b.height = b.width / this.aspectRatio);
                "sw" === e && (b.left = c.left + (a.width - b.width), b.top = null);
                "nw" === e && (b.top = c.top + (a.height -
                    b.height), b.left = c.left + (a.width - b.width));
                return b
            },
            _respectSize: function(b) {
                var c = this._vBoundaries,
                    a = this.axis,
                    e = this._isNumber(b.width) && c.maxWidth && c.maxWidth < b.width,
                    d = this._isNumber(b.height) && c.maxHeight && c.maxHeight < b.height,
                    f = this._isNumber(b.width) && c.minWidth && c.minWidth > b.width,
                    h = this._isNumber(b.height) && c.minHeight && c.minHeight > b.height,
                    n = this.originalPosition.left + this.originalSize.width,
                    l = this.position.top + this.size.height,
                    g = /sw|nw|w/.test(a);
                a = /nw|ne|n/.test(a);
                f && (b.width = c.minWidth);
                h && (b.height = c.minHeight);
                e && (b.width = c.maxWidth);
                d && (b.height = c.maxHeight);
                f && g && (b.left = n - c.minWidth);
                e && g && (b.left = n - c.maxWidth);
                h && a && (b.top = l - c.minHeight);
                d && a && (b.top = l - c.maxHeight);
                b.width || b.height || b.left || !b.top ? b.width || b.height || b.top || !b.left || (b.left = null) : b.top = null;
                return b
            },
            _getPaddingPlusBorderDimensions: function(b) {
                var c = 0,
                    a = [],
                    e = [b.css("borderTopWidth"), b.css("borderRightWidth"), b.css("borderBottomWidth"), b.css("borderLeftWidth")];
                for (b = [b.css("paddingTop"), b.css("paddingRight"),
                        b.css("paddingBottom"), b.css("paddingLeft")
                    ]; 4 > c; c++) a[c] = parseInt(e[c], 10) || 0, a[c] += parseInt(b[c], 10) || 0;
                return {
                    height: a[0] + a[2],
                    width: a[1] + a[3]
                }
            },
            _proportionallyResize: function() {
                if (this._proportionallyResizeElements.length)
                    for (var b, c = 0, a = this.helper || this.element; c < this._proportionallyResizeElements.length; c++) b = this._proportionallyResizeElements[c], this.outerDimensions || (this.outerDimensions = this._getPaddingPlusBorderDimensions(b)), b.css({
                        height: a.height() - this.outerDimensions.height || 0,
                        width: a.width() -
                            this.outerDimensions.width || 0
                    })
            },
            _renderProxy: function() {
                var b = this.options;
                this.elementOffset = this.element.offset();
                this._helper ? (this.helper = this.helper || a("\x3cdiv style\x3d'overflow:hidden;'\x3e\x3c/div\x3e"), this.helper.addClass(this._helper).css({
                    width: this.element.outerWidth() - 1,
                    height: this.element.outerHeight() - 1,
                    position: "absolute",
                    left: this.elementOffset.left + "px",
                    top: this.elementOffset.top + "px",
                    zIndex: ++b.zIndex
                }), this.helper.appendTo("body").disableSelection()) : this.helper = this.element
            },
            _change: {
                e: function(b, c) {
                    return {
                        width: this.originalSize.width + c
                    }
                },
                w: function(b, c) {
                    return {
                        left: this.originalPosition.left + c,
                        width: this.originalSize.width - c
                    }
                },
                n: function(b, c, a) {
                    return {
                        top: this.originalPosition.top + a,
                        height: this.originalSize.height - a
                    }
                },
                s: function(b, c, a) {
                    return {
                        height: this.originalSize.height + a
                    }
                },
                se: function(b, c, k) {
                    return a.extend(this._change.s.apply(this, arguments), this._change.e.apply(this, [b, c, k]))
                },
                sw: function(b, c, k) {
                    return a.extend(this._change.s.apply(this, arguments), this._change.w.apply(this,
                        [b, c, k]))
                },
                ne: function(b, c, k) {
                    return a.extend(this._change.n.apply(this, arguments), this._change.e.apply(this, [b, c, k]))
                },
                nw: function(b, c, k) {
                    return a.extend(this._change.n.apply(this, arguments), this._change.w.apply(this, [b, c, k]))
                }
            },
            _propagate: function(b, c) {
                a.ui.plugin.call(this, b, [c, this.ui()]);
                "resize" !== b && this._trigger(b, c, this.ui())
            },
            plugins: {},
            ui: function() {
                return {
                    originalElement: this.originalElement,
                    element: this.element,
                    helper: this.helper,
                    position: this.position,
                    size: this.size,
                    originalSize: this.originalSize,
                    originalPosition: this.originalPosition
                }
            }
        });
        a.ui.plugin.add("resizable", "animate", {
            stop: function(b) {
                var c = a(this).resizable("instance"),
                    k = c.options,
                    e = c._proportionallyResizeElements,
                    d = e.length && /textarea/i.test(e[0].nodeName),
                    f = d && c._hasScroll(e[0], "left") ? 0 : c.sizeDiff.height;
                d = {
                    width: c.size.width - (d ? 0 : c.sizeDiff.width),
                    height: c.size.height - f
                };
                f = parseInt(c.element.css("left"), 10) + (c.position.left - c.originalPosition.left) || null;
                var h = parseInt(c.element.css("top"), 10) + (c.position.top - c.originalPosition.top) ||
                    null;
                c.element.animate(a.extend(d, h && f ? {
                    top: h,
                    left: f
                } : {}), {
                    duration: k.animateDuration,
                    easing: k.animateEasing,
                    step: function() {
                        var k = {
                            width: parseInt(c.element.css("width"), 10),
                            height: parseInt(c.element.css("height"), 10),
                            top: parseInt(c.element.css("top"), 10),
                            left: parseInt(c.element.css("left"), 10)
                        };
                        e && e.length && a(e[0]).css({
                            width: k.width,
                            height: k.height
                        });
                        c._updateCache(k);
                        c._propagate("resize", b)
                    }
                })
            }
        });
        a.ui.plugin.add("resizable", "containment", {
            start: function() {
                var b = a(this).resizable("instance"),
                    c =
                    b.element;
                var k = b.options.containment;
                if (c = k instanceof a ? k.get(0) : /parent/.test(k) ? c.parent().get(0) : k)
                    if (b.containerElement = a(c), /document/.test(k) || k === document) b.containerOffset = {
                        left: 0,
                        top: 0
                    }, b.containerPosition = {
                        left: 0,
                        top: 0
                    }, b.parentData = {
                        element: a(document),
                        left: 0,
                        top: 0,
                        width: a(document).width(),
                        height: a(document).height() || document.body.parentNode.scrollHeight
                    };
                    else {
                        var e = a(c);
                        var d = [];
                        a(["Top", "Right", "Left", "Bottom"]).each(function(c, a) {
                            d[c] = b._num(e.css("padding" + a))
                        });
                        b.containerOffset =
                            e.offset();
                        b.containerPosition = e.position();
                        b.containerSize = {
                            height: e.innerHeight() - d[3],
                            width: e.innerWidth() - d[1]
                        };
                        k = b.containerOffset;
                        var f = b.containerSize.height;
                        var h = b.containerSize.width;
                        h = b._hasScroll(c, "left") ? c.scrollWidth : h;
                        f = b._hasScroll(c) ? c.scrollHeight : f;
                        b.parentData = {
                            element: c,
                            left: k.left,
                            top: k.top,
                            width: h,
                            height: f
                        }
                    }
            },
            resize: function(b) {
                var c = a(this).resizable("instance");
                var k = c.options;
                var e = c.containerOffset;
                var d = c.position;
                b = c._aspectRatio || b.shiftKey;
                var f = {
                        top: 0,
                        left: 0
                    },
                    h = c.containerElement,
                    n = !0;
                h[0] !== document && /static/.test(h.css("position")) && (f = e);
                d.left < (c._helper ? e.left : 0) && (c.size.width += c._helper ? c.position.left - e.left : c.position.left - f.left, b && (c.size.height = c.size.width / c.aspectRatio, n = !1), c.position.left = k.helper ? e.left : 0);
                d.top < (c._helper ? e.top : 0) && (c.size.height += c._helper ? c.position.top - e.top : c.position.top, b && (c.size.width = c.size.height * c.aspectRatio, n = !1), c.position.top = c._helper ? e.top : 0);
                k = c.containerElement.get(0) === c.element.parent().get(0);
                d = /relative|absolute/.test(c.containerElement.css("position"));
                k && d ? (c.offset.left = c.parentData.left + c.position.left, c.offset.top = c.parentData.top + c.position.top) : (c.offset.left = c.element.offset().left, c.offset.top = c.element.offset().top);
                k = Math.abs(c.sizeDiff.width + (c._helper ? c.offset.left - f.left : c.offset.left - e.left));
                e = Math.abs(c.sizeDiff.height + (c._helper ? c.offset.top - f.top : c.offset.top - e.top));
                k + c.size.width >= c.parentData.width && (c.size.width = c.parentData.width - k, b && (c.size.height = c.size.width / c.aspectRatio, n = !1));
                e + c.size.height >= c.parentData.height && (c.size.height =
                    c.parentData.height - e, b && (c.size.width = c.size.height * c.aspectRatio, n = !1));
                n || (c.position.left = c.prevPosition.left, c.position.top = c.prevPosition.top, c.size.width = c.prevSize.width, c.size.height = c.prevSize.height)
            },
            stop: function() {
                var b = a(this).resizable("instance"),
                    c = b.options,
                    k = b.containerOffset,
                    e = b.containerPosition,
                    d = b.containerElement,
                    f = a(b.helper),
                    h = f.offset(),
                    n = f.outerWidth() - b.sizeDiff.width;
                f = f.outerHeight() - b.sizeDiff.height;
                b._helper && !c.animate && /relative/.test(d.css("position")) && a(this).css({
                    left: h.left -
                        e.left - k.left,
                    width: n,
                    height: f
                });
                b._helper && !c.animate && /static/.test(d.css("position")) && a(this).css({
                    left: h.left - e.left - k.left,
                    width: n,
                    height: f
                })
            }
        });
        a.ui.plugin.add("resizable", "alsoResize", {
            start: function() {
                var b = a(this).resizable("instance").options;
                a(b.alsoResize).each(function() {
                    var b = a(this);
                    b.data("ui-resizable-alsoresize", {
                        width: parseInt(b.width(), 10),
                        height: parseInt(b.height(), 10),
                        left: parseInt(b.css("left"), 10),
                        top: parseInt(b.css("top"), 10)
                    })
                })
            },
            resize: function(b, c) {
                b = a(this).resizable("instance");
                var k = b.originalSize,
                    e = b.originalPosition,
                    d = {
                        height: b.size.height - k.height || 0,
                        width: b.size.width - k.width || 0,
                        top: b.position.top - e.top || 0,
                        left: b.position.left - e.left || 0
                    };
                a(b.options.alsoResize).each(function() {
                    var b = a(this),
                        k = a(this).data("ui-resizable-alsoresize"),
                        e = {},
                        f = b.parents(c.originalElement[0]).length ? ["width", "height"] : ["width", "height", "top", "left"];
                    a.each(f, function(b, c) {
                        (b = (k[c] || 0) + (d[c] || 0)) && 0 <= b && (e[c] = b || null)
                    });
                    b.css(e)
                })
            },
            stop: function() {
                a(this).removeData("resizable-alsoresize")
            }
        });
        a.ui.plugin.add("resizable", "ghost", {
            start: function() {
                var b = a(this).resizable("instance"),
                    c = b.options,
                    k = b.size;
                b.ghost = b.originalElement.clone();
                b.ghost.css({
                    opacity: .25,
                    display: "block",
                    position: "relative",
                    height: k.height,
                    width: k.width,
                    margin: 0,
                    left: 0,
                    top: 0
                }).addClass("ui-resizable-ghost").addClass("string" === typeof c.ghost ? c.ghost : "");
                b.ghost.appendTo(b.helper)
            },
            resize: function() {
                var b = a(this).resizable("instance");
                b.ghost && b.ghost.css({
                    position: "relative",
                    height: b.size.height,
                    width: b.size.width
                })
            },
            stop: function() {
                var b = a(this).resizable("instance");
                b.ghost && b.helper && b.helper.get(0).removeChild(b.ghost.get(0))
            }
        });
        a.ui.plugin.add("resizable", "grid", {
            resize: function() {
                var b = a(this).resizable("instance"),
                    c = b.options,
                    k = b.size,
                    e = b.originalSize,
                    d = b.originalPosition,
                    f = b.axis,
                    h = "number" === typeof c.grid ? [c.grid, c.grid] : c.grid,
                    n = h[0] || 1,
                    l = h[1] || 1,
                    g = Math.round((k.width - e.width) / n) * n;
                k = Math.round((k.height - e.height) / l) * l;
                var m = e.width + g,
                    q = e.height + k,
                    r = c.maxWidth && c.maxWidth < m,
                    v = c.maxHeight && c.maxHeight <
                    q,
                    y = c.minWidth && c.minWidth > m,
                    p = c.minHeight && c.minHeight > q;
                c.grid = h;
                y && (m += n);
                p && (q += l);
                r && (m -= n);
                v && (q -= l);
                if (/^(se|s|e)$/.test(f)) b.size.width = m, b.size.height = q;
                else if (/^(ne)$/.test(f)) b.size.width = m, b.size.height = q, b.position.top = d.top - k;
                else if (/^(sw)$/.test(f)) b.size.width = m, b.size.height = q, b.position.left = d.left - g;
                else {
                    if (0 >= q - l || 0 >= m - n) var t = b._getPaddingPlusBorderDimensions(this);
                    0 < q - l ? (b.size.height = q, b.position.top = d.top - k) : (q = l - t.height, b.size.height = q, b.position.top = d.top + e.height - q);
                    0 < m - n ? (b.size.width = m, b.position.left = d.left - g) : (m = n - t.width, b.size.width = m, b.position.left = d.left + e.width - m)
                }
            }
        });
        a.widget("ui.selectable", a.ui.mouse, {
            version: "1.11.4",
            options: {
                appendTo: "body",
                autoRefresh: !0,
                distance: 0,
                filter: "*",
                tolerance: "touch",
                selected: null,
                selecting: null,
                start: null,
                stop: null,
                unselected: null,
                unselecting: null
            },
            _create: function() {
                var b, c = this;
                this.element.addClass("ui-selectable");
                this.dragged = !1;
                this.refresh = function() {
                    b = a(c.options.filter, c.element[0]);
                    b.addClass("ui-selectee");
                    b.each(function() {
                        var b = a(this),
                            c = b.offset();
                        a.data(this, "selectable-item", {
                            element: this,
                            $element: b,
                            left: c.left,
                            top: c.top,
                            right: c.left + b.outerWidth(),
                            bottom: c.top + b.outerHeight(),
                            startselected: !1,
                            selected: b.hasClass("ui-selected"),
                            selecting: b.hasClass("ui-selecting"),
                            unselecting: b.hasClass("ui-unselecting")
                        })
                    })
                };
                this.refresh();
                this.selectees = b.addClass("ui-selectee");
                this._mouseInit();
                this.helper = a("\x3cdiv class\x3d'ui-selectable-helper'\x3e\x3c/div\x3e")
            },
            _destroy: function() {
                this.selectees.removeClass("ui-selectee").removeData("selectable-item");
                this.element.removeClass("ui-selectable ui-selectable-disabled");
                this._mouseDestroy()
            },
            _mouseStart: function(b) {
                var c = this,
                    k = this.options;
                this.opos = [b.pageX, b.pageY];
                this.options.disabled || (this.selectees = a(k.filter, this.element[0]), this._trigger("start", b), a(k.appendTo).append(this.helper), this.helper.css({
                    left: b.pageX,
                    top: b.pageY,
                    width: 0,
                    height: 0
                }), k.autoRefresh && this.refresh(), this.selectees.filter(".ui-selected").each(function() {
                    var k = a.data(this, "selectable-item");
                    k.startselected = !0;
                    b.metaKey ||
                        b.ctrlKey || (k.$element.removeClass("ui-selected"), k.selected = !1, k.$element.addClass("ui-unselecting"), k.unselecting = !0, c._trigger("unselecting", b, {
                            unselecting: k.element
                        }))
                }), a(b.target).parents().addBack().each(function() {
                    var k = a.data(this, "selectable-item");
                    if (k) {
                        var e = !b.metaKey && !b.ctrlKey || !k.$element.hasClass("ui-selected");
                        k.$element.removeClass(e ? "ui-unselecting" : "ui-selected").addClass(e ? "ui-selecting" : "ui-unselecting");
                        k.unselecting = !e;
                        k.selecting = e;
                        (k.selected = e) ? c._trigger("selecting",
                            b, {
                                selecting: k.element
                            }): c._trigger("unselecting", b, {
                            unselecting: k.element
                        });
                        return !1
                    }
                }))
            },
            _mouseDrag: function(b) {
                this.dragged = !0;
                if (!this.options.disabled) {
                    var c = this,
                        k = this.options,
                        e = this.opos[0],
                        d = this.opos[1],
                        f = b.pageX,
                        h = b.pageY;
                    if (e > f) {
                        var n = f;
                        f = e;
                        e = n
                    }
                    d > h && (n = h, h = d, d = n);
                    this.helper.css({
                        left: e,
                        top: d,
                        width: f - e,
                        height: h - d
                    });
                    this.selectees.each(function() {
                        var n = a.data(this, "selectable-item"),
                            u = !1;
                        n && n.element !== c.element[0] && ("touch" === k.tolerance ? u = !(n.left > f || n.right < e || n.top > h || n.bottom < d) : "fit" ===
                            k.tolerance && (u = n.left > e && n.right < f && n.top > d && n.bottom < h), u ? (n.selected && (n.$element.removeClass("ui-selected"), n.selected = !1), n.unselecting && (n.$element.removeClass("ui-unselecting"), n.unselecting = !1), n.selecting || (n.$element.addClass("ui-selecting"), n.selecting = !0, c._trigger("selecting", b, {
                                selecting: n.element
                            }))) : (n.selecting && ((b.metaKey || b.ctrlKey) && n.startselected ? (n.$element.removeClass("ui-selecting"), n.selecting = !1, n.$element.addClass("ui-selected"), n.selected = !0) : (n.$element.removeClass("ui-selecting"),
                                n.selecting = !1, n.startselected && (n.$element.addClass("ui-unselecting"), n.unselecting = !0), c._trigger("unselecting", b, {
                                    unselecting: n.element
                                }))), !n.selected || b.metaKey || b.ctrlKey || n.startselected || (n.$element.removeClass("ui-selected"), n.selected = !1, n.$element.addClass("ui-unselecting"), n.unselecting = !0, c._trigger("unselecting", b, {
                                unselecting: n.element
                            }))))
                    });
                    return !1
                }
            },
            _mouseStop: function(b) {
                var c = this;
                this.dragged = !1;
                a(".ui-unselecting", this.element[0]).each(function() {
                    var k = a.data(this, "selectable-item");
                    k.$element.removeClass("ui-unselecting");
                    k.unselecting = !1;
                    k.startselected = !1;
                    c._trigger("unselected", b, {
                        unselected: k.element
                    })
                });
                a(".ui-selecting", this.element[0]).each(function() {
                    var k = a.data(this, "selectable-item");
                    k.$element.removeClass("ui-selecting").addClass("ui-selected");
                    k.selecting = !1;
                    k.selected = !0;
                    k.startselected = !0;
                    c._trigger("selected", b, {
                        selected: k.element
                    })
                });
                this._trigger("stop", b);
                this.helper.remove();
                return !1
            }
        });
        a.widget("ui.sortable", a.ui.mouse, {
            version: "1.11.4",
            widgetEventPrefix: "sort",
            ready: !1,
            options: {
                appendTo: "parent",
                axis: !1,
                connectWith: !1,
                containment: !1,
                cursor: "auto",
                cursorAt: !1,
                dropOnEmpty: !0,
                forcePlaceholderSize: !1,
                forceHelperSize: !1,
                grid: !1,
                handle: !1,
                helper: "original",
                items: "\x3e *",
                opacity: !1,
                placeholder: !1,
                revert: !1,
                scroll: !0,
                scrollSensitivity: 20,
                scrollSpeed: 20,
                scope: "default",
                tolerance: "intersect",
                zIndex: 1E3,
                activate: null,
                beforeStop: null,
                change: null,
                deactivate: null,
                out: null,
                over: null,
                receive: null,
                remove: null,
                sort: null,
                start: null,
                stop: null,
                update: null
            },
            _isOverAxis: function(b,
                c, a) {
                return b >= c && b < c + a
            },
            _isFloating: function(b) {
                return /left|right/.test(b.css("float")) || /inline|table-cell/.test(b.css("display"))
            },
            _create: function() {
                this.containerCache = {};
                this.element.addClass("ui-sortable");
                this.refresh();
                this.offset = this.element.offset();
                this._mouseInit();
                this._setHandleClassName();
                this.ready = !0
            },
            _setOption: function(b, c) {
                this._super(b, c);
                "handle" === b && this._setHandleClassName()
            },
            _setHandleClassName: function() {
                this.element.find(".ui-sortable-handle").removeClass("ui-sortable-handle");
                a.each(this.items, function() {
                    (this.instance.options.handle ? this.item.find(this.instance.options.handle) : this.item).addClass("ui-sortable-handle")
                })
            },
            _destroy: function() {
                this.element.removeClass("ui-sortable ui-sortable-disabled").find(".ui-sortable-handle").removeClass("ui-sortable-handle");
                this._mouseDestroy();
                for (var b = this.items.length - 1; 0 <= b; b--) this.items[b].item.removeData(this.widgetName + "-item");
                return this
            },
            _mouseCapture: function(b, c) {
                var k = null,
                    e = !1,
                    d = this;
                if (this.reverting || this.options.disabled ||
                    "static" === this.options.type) return !1;
                this._refreshItems(b);
                a(b.target).parents().each(function() {
                    if (a.data(this, d.widgetName + "-item") === d) return k = a(this), !1
                });
                a.data(b.target, d.widgetName + "-item") === d && (k = a(b.target));
                if (!k || this.options.handle && !c && (a(this.options.handle, k).find("*").addBack().each(function() {
                        this === b.target && (e = !0)
                    }), !e)) return !1;
                this.currentItem = k;
                this._removeCurrentsFromItems();
                return !0
            },
            _mouseStart: function(b, c, k) {
                c = this.options;
                this.currentContainer = this;
                this.refreshPositions();
                this.helper = this._createHelper(b);
                this._cacheHelperProportions();
                this._cacheMargins();
                this.scrollParent = this.helper.scrollParent();
                this.offset = this.currentItem.offset();
                this.offset = {
                    top: this.offset.top - this.margins.top,
                    left: this.offset.left - this.margins.left
                };
                a.extend(this.offset, {
                    click: {
                        left: b.pageX - this.offset.left,
                        top: b.pageY - this.offset.top
                    },
                    parent: this._getParentOffset(),
                    relative: this._getRelativeOffset()
                });
                this.helper.css("position", "absolute");
                this.cssPosition = this.helper.css("position");
                this.originalPosition =
                    this._generatePosition(b);
                this.originalPageX = b.pageX;
                this.originalPageY = b.pageY;
                c.cursorAt && this._adjustOffsetFromHelper(c.cursorAt);
                this.domPosition = {
                    prev: this.currentItem.prev()[0],
                    parent: this.currentItem.parent()[0]
                };
                this.helper[0] !== this.currentItem[0] && this.currentItem.hide();
                this._createPlaceholder();
                c.containment && this._setContainment();
                if (c.cursor && "auto" !== c.cursor) {
                    var e = this.document.find("body");
                    this.storedCursor = e.css("cursor");
                    e.css("cursor", c.cursor);
                    this.storedStylesheet = a("\x3cstyle\x3e*{ cursor: " +
                        c.cursor + " !important; }\x3c/style\x3e").appendTo(e)
                }
                c.opacity && (this.helper.css("opacity") && (this._storedOpacity = this.helper.css("opacity")), this.helper.css("opacity", c.opacity));
                c.zIndex && (this.helper.css("zIndex") && (this._storedZIndex = this.helper.css("zIndex")), this.helper.css("zIndex", c.zIndex));
                this.scrollParent[0] !== this.document[0] && "HTML" !== this.scrollParent[0].tagName && (this.overflowOffset = this.scrollParent.offset());
                this._trigger("start", b, this._uiHash());
                this._preserveHelperProportions ||
                    this._cacheHelperProportions();
                if (!k)
                    for (k = this.containers.length - 1; 0 <= k; k--) this.containers[k]._trigger("activate", b, this._uiHash(this));
                a.ui.ddmanager && (a.ui.ddmanager.current = this);
                a.ui.ddmanager && !c.dropBehaviour && a.ui.ddmanager.prepareOffsets(this, b);
                this.dragging = !0;
                this.helper.addClass("ui-sortable-helper");
                this._mouseDrag(b);
                return !0
            },
            _mouseDrag: function(b) {
                var c;
                var k = this.options;
                var e = !1;
                this.position = this._generatePosition(b);
                this.positionAbs = this._convertPositionTo("absolute");
                this.lastPositionAbs ||
                    (this.lastPositionAbs = this.positionAbs);
                this.options.scroll && (this.scrollParent[0] !== this.document[0] && "HTML" !== this.scrollParent[0].tagName ? (this.overflowOffset.top + this.scrollParent[0].offsetHeight - b.pageY < k.scrollSensitivity ? this.scrollParent[0].scrollTop = e = this.scrollParent[0].scrollTop + k.scrollSpeed : b.pageY - this.overflowOffset.top < k.scrollSensitivity && (this.scrollParent[0].scrollTop = e = this.scrollParent[0].scrollTop - k.scrollSpeed), this.overflowOffset.left + this.scrollParent[0].offsetWidth - b.pageX <
                    k.scrollSensitivity ? this.scrollParent[0].scrollLeft = e = this.scrollParent[0].scrollLeft + k.scrollSpeed : b.pageX - this.overflowOffset.left < k.scrollSensitivity && (this.scrollParent[0].scrollLeft = e = this.scrollParent[0].scrollLeft - k.scrollSpeed)) : (b.pageY - this.document.scrollTop() < k.scrollSensitivity ? e = this.document.scrollTop(this.document.scrollTop() - k.scrollSpeed) : this.window.height() - (b.pageY - this.document.scrollTop()) < k.scrollSensitivity && (e = this.document.scrollTop(this.document.scrollTop() + k.scrollSpeed)),
                    b.pageX - this.document.scrollLeft() < k.scrollSensitivity ? e = this.document.scrollLeft(this.document.scrollLeft() - k.scrollSpeed) : this.window.width() - (b.pageX - this.document.scrollLeft()) < k.scrollSensitivity && (e = this.document.scrollLeft(this.document.scrollLeft() + k.scrollSpeed))), !1 !== e && a.ui.ddmanager && !k.dropBehaviour && a.ui.ddmanager.prepareOffsets(this, b));
                this.positionAbs = this._convertPositionTo("absolute");
                this.options.axis && "y" === this.options.axis || (this.helper[0].style.left = this.position.left + "px");
                this.options.axis && "x" === this.options.axis || (this.helper[0].style.top = this.position.top + "px");
                for (k = this.items.length - 1; 0 <= k; k--) {
                    e = this.items[k];
                    var d = e.item[0];
                    if ((c = this._intersectsWithPointer(e)) && e.instance === this.currentContainer && d !== this.currentItem[0] && this.placeholder[1 === c ? "next" : "prev"]()[0] !== d && !a.contains(this.placeholder[0], d) && ("semi-dynamic" === this.options.type ? !a.contains(this.element[0], d) : 1)) {
                        this.direction = 1 === c ? "down" : "up";
                        if ("pointer" === this.options.tolerance || this._intersectsWithSides(e)) this._rearrange(b,
                            e);
                        else break;
                        this._trigger("change", b, this._uiHash());
                        break
                    }
                }
                this._contactContainers(b);
                a.ui.ddmanager && a.ui.ddmanager.drag(this, b);
                this._trigger("sort", b, this._uiHash());
                this.lastPositionAbs = this.positionAbs;
                return !1
            },
            _mouseStop: function(b, c) {
                if (b) {
                    a.ui.ddmanager && !this.options.dropBehaviour && a.ui.ddmanager.drop(this, b);
                    if (this.options.revert) {
                        var k = this;
                        c = this.placeholder.offset();
                        var e = this.options.axis,
                            d = {};
                        e && "x" !== e || (d.left = c.left - this.offset.parent.left - this.margins.left + (this.offsetParent[0] ===
                            this.document[0].body ? 0 : this.offsetParent[0].scrollLeft));
                        e && "y" !== e || (d.top = c.top - this.offset.parent.top - this.margins.top + (this.offsetParent[0] === this.document[0].body ? 0 : this.offsetParent[0].scrollTop));
                        this.reverting = !0;
                        a(this.helper).animate(d, parseInt(this.options.revert, 10) || 500, function() {
                            k._clear(b)
                        })
                    } else this._clear(b, c);
                    return !1
                }
            },
            cancel: function() {
                if (this.dragging) {
                    this._mouseUp({
                        target: null
                    });
                    "original" === this.options.helper ? this.currentItem.css(this._storedCSS).removeClass("ui-sortable-helper") :
                        this.currentItem.show();
                    for (var b = this.containers.length - 1; 0 <= b; b--) this.containers[b]._trigger("deactivate", null, this._uiHash(this)), this.containers[b].containerCache.over && (this.containers[b]._trigger("out", null, this._uiHash(this)), this.containers[b].containerCache.over = 0)
                }
                this.placeholder && (this.placeholder[0].parentNode && this.placeholder[0].parentNode.removeChild(this.placeholder[0]), "original" !== this.options.helper && this.helper && this.helper[0].parentNode && this.helper.remove(), a.extend(this, {
                    helper: null,
                    dragging: !1,
                    reverting: !1,
                    _noFinalSort: null
                }), this.domPosition.prev ? a(this.domPosition.prev).after(this.currentItem) : a(this.domPosition.parent).prepend(this.currentItem));
                return this
            },
            serialize: function(b) {
                var c = this._getItemsAsjQuery(b && b.connected),
                    k = [];
                b = b || {};
                a(c).each(function() {
                    var c = (a(b.item || this).attr(b.attribute || "id") || "").match(b.expression || /(.+)[\-=_](.+)/);
                    c && k.push((b.key || c[1] + "[]") + "\x3d" + (b.key && b.expression ? c[1] : c[2]))
                });
                !k.length && b.key && k.push(b.key + "\x3d");
                return k.join("\x26")
            },
            toArray: function(b) {
                var c = this._getItemsAsjQuery(b && b.connected),
                    k = [];
                b = b || {};
                c.each(function() {
                    k.push(a(b.item || this).attr(b.attribute || "id") || "")
                });
                return k
            },
            _intersectsWith: function(b) {
                var c = this.positionAbs.left,
                    a = c + this.helperProportions.width,
                    e = this.positionAbs.top,
                    d = e + this.helperProportions.height,
                    f = b.left,
                    h = f + b.width,
                    n = b.top,
                    l = n + b.height,
                    g = this.offset.click.top,
                    m = this.offset.click.left;
                g = "x" === this.options.axis || e + g > n && e + g < l;
                m = "y" === this.options.axis || c + m > f && c + m < h;
                return "pointer" === this.options.tolerance ||
                    this.options.forcePointerForContainers || "pointer" !== this.options.tolerance && this.helperProportions[this.floating ? "width" : "height"] > b[this.floating ? "width" : "height"] ? g && m : f < c + this.helperProportions.width / 2 && a - this.helperProportions.width / 2 < h && n < e + this.helperProportions.height / 2 && d - this.helperProportions.height / 2 < l
            },
            _intersectsWithPointer: function(b) {
                var c = "x" === this.options.axis || this._isOverAxis(this.positionAbs.top + this.offset.click.top, b.top, b.height);
                b = "y" === this.options.axis || this._isOverAxis(this.positionAbs.left +
                    this.offset.click.left, b.left, b.width);
                c = c && b;
                b = this._getDragVerticalDirection();
                var a = this._getDragHorizontalDirection();
                return c ? this.floating ? a && "right" === a || "down" === b ? 2 : 1 : b && ("down" === b ? 2 : 1) : !1
            },
            _intersectsWithSides: function(b) {
                var c = this._isOverAxis(this.positionAbs.top + this.offset.click.top, b.top + b.height / 2, b.height);
                b = this._isOverAxis(this.positionAbs.left + this.offset.click.left, b.left + b.width / 2, b.width);
                var a = this._getDragVerticalDirection(),
                    e = this._getDragHorizontalDirection();
                return this.floating &&
                    e ? "right" === e && b || "left" === e && !b : a && ("down" === a && c || "up" === a && !c)
            },
            _getDragVerticalDirection: function() {
                var b = this.positionAbs.top - this.lastPositionAbs.top;
                return 0 !== b && (0 < b ? "down" : "up")
            },
            _getDragHorizontalDirection: function() {
                var b = this.positionAbs.left - this.lastPositionAbs.left;
                return 0 !== b && (0 < b ? "right" : "left")
            },
            refresh: function(b) {
                this._refreshItems(b);
                this._setHandleClassName();
                this.refreshPositions();
                return this
            },
            _connectWith: function() {
                var b = this.options;
                return b.connectWith.constructor ===
                    String ? [b.connectWith] : b.connectWith
            },
            _getItemsAsjQuery: function(b) {
                function c() {
                    d.push(this)
                }
                var k, e, d = [],
                    f = [],
                    h = this._connectWith();
                if (h && b)
                    for (b = h.length - 1; 0 <= b; b--) {
                        var n = a(h[b], this.document[0]);
                        for (k = n.length - 1; 0 <= k; k--)(e = a.data(n[k], this.widgetFullName)) && e !== this && !e.options.disabled && f.push([a.isFunction(e.options.items) ? e.options.items.call(e.element) : a(e.options.items, e.element).not(".ui-sortable-helper").not(".ui-sortable-placeholder"), e])
                    }
                f.push([a.isFunction(this.options.items) ? this.options.items.call(this.element,
                    null, {
                        options: this.options,
                        item: this.currentItem
                    }) : a(this.options.items, this.element).not(".ui-sortable-helper").not(".ui-sortable-placeholder"), this]);
                for (b = f.length - 1; 0 <= b; b--) f[b][0].each(c);
                return a(d)
            },
            _removeCurrentsFromItems: function() {
                var b = this.currentItem.find(":data(" + this.widgetName + "-item)");
                this.items = a.grep(this.items, function(c) {
                    for (var a = 0; a < b.length; a++)
                        if (b[a] === c.item[0]) return !1;
                    return !0
                })
            },
            _refreshItems: function(b) {
                this.items = [];
                this.containers = [this];
                var c, k, e, d, f = this.items,
                    h = [
                        [a.isFunction(this.options.items) ? this.options.items.call(this.element[0], b, {
                            item: this.currentItem
                        }) : a(this.options.items, this.element), this]
                    ];
                if ((d = this._connectWith()) && this.ready)
                    for (c = d.length - 1; 0 <= c; c--) {
                        var n = a(d[c], this.document[0]);
                        for (k = n.length - 1; 0 <= k; k--)(e = a.data(n[k], this.widgetFullName)) && e !== this && !e.options.disabled && (h.push([a.isFunction(e.options.items) ? e.options.items.call(e.element[0], b, {
                            item: this.currentItem
                        }) : a(e.options.items, e.element), e]), this.containers.push(e))
                    }
                for (c =
                    h.length - 1; 0 <= c; c--)
                    for (b = h[c][1], n = h[c][0], k = 0, d = n.length; k < d; k++) e = a(n[k]), e.data(this.widgetName + "-item", b), f.push({
                        item: e,
                        instance: b,
                        width: 0,
                        height: 0,
                        left: 0,
                        top: 0
                    })
            },
            refreshPositions: function(b) {
                this.floating = this.items.length ? "x" === this.options.axis || this._isFloating(this.items[0].item) : !1;
                this.offsetParent && this.helper && (this.offset.parent = this._getParentOffset());
                var c;
                for (c = this.items.length - 1; 0 <= c; c--) {
                    var k = this.items[c];
                    if (k.instance === this.currentContainer || !this.currentContainer || k.item[0] ===
                        this.currentItem[0]) {
                        var e = this.options.toleranceElement ? a(this.options.toleranceElement, k.item) : k.item;
                        b || (k.width = e.outerWidth(), k.height = e.outerHeight());
                        e = e.offset();
                        k.left = e.left;
                        k.top = e.top
                    }
                }
                if (this.options.custom && this.options.custom.refreshContainers) this.options.custom.refreshContainers.call(this);
                else
                    for (c = this.containers.length - 1; 0 <= c; c--) e = this.containers[c].element.offset(), this.containers[c].containerCache.left = e.left, this.containers[c].containerCache.top = e.top, this.containers[c].containerCache.width =
                        this.containers[c].element.outerWidth(), this.containers[c].containerCache.height = this.containers[c].element.outerHeight();
                return this
            },
            _createPlaceholder: function(b) {
                b = b || this;
                var c = b.options;
                if (!c.placeholder || c.placeholder.constructor === String) {
                    var k = c.placeholder;
                    c.placeholder = {
                        element: function() {
                            var c = b.currentItem[0].nodeName.toLowerCase(),
                                e = a("\x3c" + c + "\x3e", b.document[0]).addClass(k || b.currentItem[0].className + " ui-sortable-placeholder").removeClass("ui-sortable-helper");
                            "tbody" === c ? b._createTrPlaceholder(b.currentItem.find("tr").eq(0),
                                a("\x3ctr\x3e", b.document[0]).appendTo(e)) : "tr" === c ? b._createTrPlaceholder(b.currentItem, e) : "img" === c && e.attr("src", b.currentItem.attr("src"));
                            k || e.css("visibility", "hidden");
                            return e
                        },
                        update: function(a, e) {
                            if (!k || c.forcePlaceholderSize) e.height() || e.height(b.currentItem.innerHeight() - parseInt(b.currentItem.css("paddingTop") || 0, 10) - parseInt(b.currentItem.css("paddingBottom") || 0, 10)), e.width() || e.width(b.currentItem.innerWidth() - parseInt(b.currentItem.css("paddingLeft") || 0, 10) - parseInt(b.currentItem.css("paddingRight") ||
                                0, 10))
                        }
                    }
                }
                b.placeholder = a(c.placeholder.element.call(b.element, b.currentItem));
                b.currentItem.after(b.placeholder);
                c.placeholder.update(b, b.placeholder)
            },
            _createTrPlaceholder: function(b, c) {
                var k = this;
                b.children().each(function() {
                    a("\x3ctd\x3e\x26#160;\x3c/td\x3e", k.document[0]).attr("colspan", a(this).attr("colspan") || 1).appendTo(c)
                })
            },
            _contactContainers: function(b) {
                var c, k, e, d = e = null;
                for (c = this.containers.length - 1; 0 <= c; c--) a.contains(this.currentItem[0], this.containers[c].element[0]) || (this._intersectsWith(this.containers[c].containerCache) ?
                    e && a.contains(this.containers[c].element[0], e.element[0]) || (e = this.containers[c], d = c) : this.containers[c].containerCache.over && (this.containers[c]._trigger("out", b, this._uiHash(this)), this.containers[c].containerCache.over = 0));
                if (e)
                    if (1 === this.containers.length) this.containers[d].containerCache.over || (this.containers[d]._trigger("over", b, this._uiHash(this)), this.containers[d].containerCache.over = 1);
                    else {
                        c = 1E4;
                        var f = null;
                        e = (k = e.floating || this._isFloating(this.currentItem)) ? "left" : "top";
                        var h = k ? "width" :
                            "height";
                        var n = k ? "clientX" : "clientY";
                        for (k = this.items.length - 1; 0 <= k; k--)
                            if (a.contains(this.containers[d].element[0], this.items[k].item[0]) && this.items[k].item[0] !== this.currentItem[0]) {
                                var l = this.items[k].item.offset()[e];
                                var g = !1;
                                b[n] - l > this.items[k][h] / 2 && (g = !0);
                                Math.abs(b[n] - l) < c && (c = Math.abs(b[n] - l), f = this.items[k], this.direction = g ? "up" : "down")
                            } if (f || this.options.dropOnEmpty) this.currentContainer === this.containers[d] ? this.currentContainer.containerCache.over || (this.containers[d]._trigger("over",
                            b, this._uiHash()), this.currentContainer.containerCache.over = 1) : (f ? this._rearrange(b, f, null, !0) : this._rearrange(b, null, this.containers[d].element, !0), this._trigger("change", b, this._uiHash()), this.containers[d]._trigger("change", b, this._uiHash(this)), this.currentContainer = this.containers[d], this.options.placeholder.update(this.currentContainer, this.placeholder), this.containers[d]._trigger("over", b, this._uiHash(this)), this.containers[d].containerCache.over = 1)
                    }
            },
            _createHelper: function(b) {
                var c = this.options;
                b = a.isFunction(c.helper) ? a(c.helper.apply(this.element[0], [b, this.currentItem])) : "clone" === c.helper ? this.currentItem.clone() : this.currentItem;
                b.parents("body").length || a("parent" !== c.appendTo ? c.appendTo : this.currentItem[0].parentNode)[0].appendChild(b[0]);
                b[0] === this.currentItem[0] && (this._storedCSS = {
                    width: this.currentItem[0].style.width,
                    height: this.currentItem[0].style.height,
                    position: this.currentItem.css("position"),
                    top: this.currentItem.css("top"),
                    left: this.currentItem.css("left")
                });
                b[0].style.width &&
                    !c.forceHelperSize || b.width(this.currentItem.width());
                b[0].style.height && !c.forceHelperSize || b.height(this.currentItem.height());
                return b
            },
            _adjustOffsetFromHelper: function(b) {
                "string" === typeof b && (b = b.split(" "));
                a.isArray(b) && (b = {
                    left: +b[0],
                    top: +b[1] || 0
                });
                "left" in b && (this.offset.click.left = b.left + this.margins.left);
                "right" in b && (this.offset.click.left = this.helperProportions.width - b.right + this.margins.left);
                "top" in b && (this.offset.click.top = b.top + this.margins.top);
                "bottom" in b && (this.offset.click.top =
                    this.helperProportions.height - b.bottom + this.margins.top)
            },
            _getParentOffset: function() {
                this.offsetParent = this.helper.offsetParent();
                var b = this.offsetParent.offset();
                "absolute" === this.cssPosition && this.scrollParent[0] !== this.document[0] && a.contains(this.scrollParent[0], this.offsetParent[0]) && (b.left += this.scrollParent.scrollLeft(), b.top += this.scrollParent.scrollTop());
                if (this.offsetParent[0] === this.document[0].body || this.offsetParent[0].tagName && "html" === this.offsetParent[0].tagName.toLowerCase() &&
                    a.ui.ie) b = {
                    top: 0,
                    left: 0
                };
                return {
                    top: b.top + (parseInt(this.offsetParent.css("borderTopWidth"), 10) || 0),
                    left: b.left + (parseInt(this.offsetParent.css("borderLeftWidth"), 10) || 0)
                }
            },
            _getRelativeOffset: function() {
                if ("relative" === this.cssPosition) {
                    var b = this.currentItem.position();
                    return {
                        top: b.top - (parseInt(this.helper.css("top"), 10) || 0) + this.scrollParent.scrollTop(),
                        left: b.left - (parseInt(this.helper.css("left"), 10) || 0) + this.scrollParent.scrollLeft()
                    }
                }
                return {
                    top: 0,
                    left: 0
                }
            },
            _cacheMargins: function() {
                this.margins = {
                    left: parseInt(this.currentItem.css("marginLeft"), 10) || 0,
                    top: parseInt(this.currentItem.css("marginTop"), 10) || 0
                }
            },
            _cacheHelperProportions: function() {
                this.helperProportions = {
                    width: this.helper.outerWidth(),
                    height: this.helper.outerHeight()
                }
            },
            _setContainment: function() {
                var b = this.options;
                "parent" === b.containment && (b.containment = this.helper[0].parentNode);
                if ("document" === b.containment || "window" === b.containment) this.containment = [0 - this.offset.relative.left - this.offset.parent.left, 0 - this.offset.relative.top -
                    this.offset.parent.top, "document" === b.containment ? this.document.width() : this.window.width() - this.helperProportions.width - this.margins.left, ("document" === b.containment ? this.document.width() : this.window.height() || this.document[0].body.parentNode.scrollHeight) - this.helperProportions.height - this.margins.top
                ];
                if (!/^(document|window|parent)$/.test(b.containment)) {
                    var c = a(b.containment)[0];
                    b = a(b.containment).offset();
                    var e = "hidden" !== a(c).css("overflow");
                    this.containment = [b.left + (parseInt(a(c).css("borderLeftWidth"),
                        10) || 0) + (parseInt(a(c).css("paddingLeft"), 10) || 0) - this.margins.left, b.top + (parseInt(a(c).css("borderTopWidth"), 10) || 0) + (parseInt(a(c).css("paddingTop"), 10) || 0) - this.margins.top, b.left + (e ? Math.max(c.scrollWidth, c.offsetWidth) : c.offsetWidth) - (parseInt(a(c).css("borderLeftWidth"), 10) || 0) - (parseInt(a(c).css("paddingRight"), 10) || 0) - this.helperProportions.width - this.margins.left, b.top + (e ? Math.max(c.scrollHeight, c.offsetHeight) : c.offsetHeight) - (parseInt(a(c).css("borderTopWidth"), 10) || 0) - (parseInt(a(c).css("paddingBottom"),
                        10) || 0) - this.helperProportions.height - this.margins.top]
                }
            },
            _convertPositionTo: function(b, c) {
                c || (c = this.position);
                b = "absolute" === b ? 1 : -1;
                var e = "absolute" !== this.cssPosition || this.scrollParent[0] !== this.document[0] && a.contains(this.scrollParent[0], this.offsetParent[0]) ? this.scrollParent : this.offsetParent,
                    d = /(html|body)/i.test(e[0].tagName);
                return {
                    top: c.top + this.offset.relative.top * b + this.offset.parent.top * b - ("fixed" === this.cssPosition ? -this.scrollParent.scrollTop() : d ? 0 : e.scrollTop()) * b,
                    left: c.left + this.offset.relative.left *
                        b + this.offset.parent.left * b - ("fixed" === this.cssPosition ? -this.scrollParent.scrollLeft() : d ? 0 : e.scrollLeft()) * b
                }
            },
            _generatePosition: function(b) {
                var c = this.options;
                var e = b.pageX;
                var d = b.pageY;
                var f = "absolute" !== this.cssPosition || this.scrollParent[0] !== this.document[0] && a.contains(this.scrollParent[0], this.offsetParent[0]) ? this.scrollParent : this.offsetParent,
                    h = /(html|body)/i.test(f[0].tagName);
                "relative" !== this.cssPosition || this.scrollParent[0] !== this.document[0] && this.scrollParent[0] !== this.offsetParent[0] ||
                    (this.offset.relative = this._getRelativeOffset());
                this.originalPosition && (this.containment && (b.pageX - this.offset.click.left < this.containment[0] && (e = this.containment[0] + this.offset.click.left), b.pageY - this.offset.click.top < this.containment[1] && (d = this.containment[1] + this.offset.click.top), b.pageX - this.offset.click.left > this.containment[2] && (e = this.containment[2] + this.offset.click.left), b.pageY - this.offset.click.top > this.containment[3] && (d = this.containment[3] + this.offset.click.top)), c.grid && (d = this.originalPageY +
                    Math.round((d - this.originalPageY) / c.grid[1]) * c.grid[1], d = this.containment ? d - this.offset.click.top >= this.containment[1] && d - this.offset.click.top <= this.containment[3] ? d : d - this.offset.click.top >= this.containment[1] ? d - c.grid[1] : d + c.grid[1] : d, e = this.originalPageX + Math.round((e - this.originalPageX) / c.grid[0]) * c.grid[0], e = this.containment ? e - this.offset.click.left >= this.containment[0] && e - this.offset.click.left <= this.containment[2] ? e : e - this.offset.click.left >= this.containment[0] ? e - c.grid[0] : e + c.grid[0] : e));
                return {
                    top: d - this.offset.click.top - this.offset.relative.top - this.offset.parent.top + ("fixed" === this.cssPosition ? -this.scrollParent.scrollTop() : h ? 0 : f.scrollTop()),
                    left: e - this.offset.click.left - this.offset.relative.left - this.offset.parent.left + ("fixed" === this.cssPosition ? -this.scrollParent.scrollLeft() : h ? 0 : f.scrollLeft())
                }
            },
            _rearrange: function(b, c, a, e) {
                a ? a[0].appendChild(this.placeholder[0]) : c.item[0].parentNode.insertBefore(this.placeholder[0], "down" === this.direction ? c.item[0] : c.item[0].nextSibling);
                var k = this.counter = this.counter ? ++this.counter : 1;
                this._delay(function() {
                    k === this.counter && this.refreshPositions(!e)
                })
            },
            _clear: function(b, c) {
                function a(b, c, a) {
                    return function(e) {
                        a._trigger(b, e, c._uiHash(c))
                    }
                }
                this.reverting = !1;
                var e, d = [];
                !this._noFinalSort && this.currentItem.parent().length && this.placeholder.before(this.currentItem);
                this._noFinalSort = null;
                if (this.helper[0] === this.currentItem[0]) {
                    for (e in this._storedCSS)
                        if ("auto" === this._storedCSS[e] || "static" === this._storedCSS[e]) this._storedCSS[e] =
                            "";
                    this.currentItem.css(this._storedCSS).removeClass("ui-sortable-helper")
                } else this.currentItem.show();
                this.fromOutside && !c && d.push(function(b) {
                    this._trigger("receive", b, this._uiHash(this.fromOutside))
                });
                !this.fromOutside && this.domPosition.prev === this.currentItem.prev().not(".ui-sortable-helper")[0] && this.domPosition.parent === this.currentItem.parent()[0] || c || d.push(function(b) {
                    this._trigger("update", b, this._uiHash())
                });
                this === this.currentContainer || c || (d.push(function(b) {
                    this._trigger("remove", b,
                        this._uiHash())
                }), d.push(function(b) {
                    return function(c) {
                        b._trigger("receive", c, this._uiHash(this))
                    }
                }.call(this, this.currentContainer)), d.push(function(b) {
                    return function(c) {
                        b._trigger("update", c, this._uiHash(this))
                    }
                }.call(this, this.currentContainer)));
                for (e = this.containers.length - 1; 0 <= e; e--) c || d.push(a("deactivate", this, this.containers[e])), this.containers[e].containerCache.over && (d.push(a("out", this, this.containers[e])), this.containers[e].containerCache.over = 0);
                this.storedCursor && (this.document.find("body").css("cursor",
                    this.storedCursor), this.storedStylesheet.remove());
                this._storedOpacity && this.helper.css("opacity", this._storedOpacity);
                this._storedZIndex && this.helper.css("zIndex", "auto" === this._storedZIndex ? "" : this._storedZIndex);
                this.dragging = !1;
                c || this._trigger("beforeStop", b, this._uiHash());
                this.placeholder[0].parentNode.removeChild(this.placeholder[0]);
                this.cancelHelperRemoval || (this.helper[0] !== this.currentItem[0] && this.helper.remove(), this.helper = null);
                if (!c) {
                    for (e = 0; e < d.length; e++) d[e].call(this, b);
                    this._trigger("stop",
                        b, this._uiHash())
                }
                this.fromOutside = !1;
                return !this.cancelHelperRemoval
            },
            _trigger: function() {
                !1 === a.Widget.prototype._trigger.apply(this, arguments) && this.cancel()
            },
            _uiHash: function(b) {
                var c = b || this;
                return {
                    helper: c.helper,
                    placeholder: c.placeholder || a([]),
                    position: c.position,
                    originalPosition: c.originalPosition,
                    offset: c.positionAbs,
                    item: c.currentItem,
                    sender: b ? b.element : null
                }
            }
        });
        a.widget("ui.accordion", {
            version: "1.11.4",
            options: {
                active: 0,
                animate: {},
                collapsible: !1,
                event: "click",
                header: "\x3e li \x3e :first-child,\x3e :not(li):even",
                heightStyle: "auto",
                icons: {
                    activeHeader: "ui-icon-triangle-1-s",
                    header: "ui-icon-triangle-1-e"
                },
                activate: null,
                beforeActivate: null
            },
            hideProps: {
                borderTopWidth: "hide",
                borderBottomWidth: "hide",
                paddingTop: "hide",
                paddingBottom: "hide",
                height: "hide"
            },
            showProps: {
                borderTopWidth: "show",
                borderBottomWidth: "show",
                paddingTop: "show",
                paddingBottom: "show",
                height: "show"
            },
            _create: function() {
                var b = this.options;
                this.prevShow = this.prevHide = a();
                this.element.addClass("ui-accordion ui-widget ui-helper-reset").attr("role", "tablist");
                b.collapsible || !1 !== b.active && null != b.active || (b.active = 0);
                this._processPanels();
                0 > b.active && (b.active += this.headers.length);
                this._refresh()
            },
            _getCreateEventData: function() {
                return {
                    header: this.active,
                    panel: this.active.length ? this.active.next() : a()
                }
            },
            _createIcons: function() {
                var b = this.options.icons;
                b && (a("\x3cspan\x3e").addClass("ui-accordion-header-icon ui-icon " + b.header).prependTo(this.headers), this.active.children(".ui-accordion-header-icon").removeClass(b.header).addClass(b.activeHeader), this.headers.addClass("ui-accordion-icons"))
            },
            _destroyIcons: function() {
                this.headers.removeClass("ui-accordion-icons").children(".ui-accordion-header-icon").remove()
            },
            _destroy: function() {
                this.element.removeClass("ui-accordion ui-widget ui-helper-reset").removeAttr("role");
                this.headers.removeClass("ui-accordion-header ui-accordion-header-active ui-state-default ui-corner-all ui-state-active ui-state-disabled ui-corner-top").removeAttr("role").removeAttr("aria-expanded").removeAttr("aria-selected").removeAttr("aria-controls").removeAttr("tabIndex").removeUniqueId();
                this._destroyIcons();
                var b = this.headers.next().removeClass("ui-helper-reset ui-widget-content ui-corner-bottom ui-accordion-content ui-accordion-content-active ui-state-disabled").css("display", "").removeAttr("role").removeAttr("aria-hidden").removeAttr("aria-labelledby").removeUniqueId();
                "content" !== this.options.heightStyle && b.css("height", "")
            },
            _setOption: function(b, c) {
                "active" === b ? this._activate(c) : ("event" === b && (this.options.event && this._off(this.headers, this.options.event), this._setupEvents(c)),
                    this._super(b, c), "collapsible" !== b || c || !1 !== this.options.active || this._activate(0), "icons" === b && (this._destroyIcons(), c && this._createIcons()), "disabled" === b && (this.element.toggleClass("ui-state-disabled", !!c).attr("aria-disabled", c), this.headers.add(this.headers.next()).toggleClass("ui-state-disabled", !!c)))
            },
            _keydown: function(b) {
                if (!b.altKey && !b.ctrlKey) {
                    var c = a.ui.keyCode,
                        e = this.headers.length,
                        d = this.headers.index(b.target),
                        f = !1;
                    switch (b.keyCode) {
                        case c.RIGHT:
                        case c.DOWN:
                            f = this.headers[(d + 1) % e];
                            break;
                        case c.LEFT:
                        case c.UP:
                            f = this.headers[(d - 1 + e) % e];
                            break;
                        case c.SPACE:
                        case c.ENTER:
                            this._eventHandler(b);
                            break;
                        case c.HOME:
                            f = this.headers[0];
                            break;
                        case c.END:
                            f = this.headers[e - 1]
                    }
                    f && (a(b.target).attr("tabIndex", -1), a(f).attr("tabIndex", 0), f.focus(), b.preventDefault())
                }
            },
            _panelKeyDown: function(b) {
                b.keyCode === a.ui.keyCode.UP && b.ctrlKey && a(b.currentTarget).prev().focus()
            },
            refresh: function() {
                var b = this.options;
                this._processPanels();
                !1 === b.active && !0 === b.collapsible || !this.headers.length ? (b.active = !1,
                    this.active = a()) : !1 === b.active ? this._activate(0) : this.active.length && !a.contains(this.element[0], this.active[0]) ? this.headers.length === this.headers.find(".ui-state-disabled").length ? (b.active = !1, this.active = a()) : this._activate(Math.max(0, b.active - 1)) : b.active = this.headers.index(this.active);
                this._destroyIcons();
                this._refresh()
            },
            _processPanels: function() {
                var b = this.headers,
                    c = this.panels;
                this.headers = this.element.find(this.options.header).addClass("ui-accordion-header ui-state-default ui-corner-all");
                this.panels = this.headers.next().addClass("ui-accordion-content ui-helper-reset ui-widget-content ui-corner-bottom").filter(":not(.ui-accordion-content-active)").hide();
                c && (this._off(b.not(this.headers)), this._off(c.not(this.panels)))
            },
            _refresh: function() {
                var b = this.options,
                    c = b.heightStyle,
                    e = this.element.parent();
                this.active = this._findActive(b.active).addClass("ui-accordion-header-active ui-state-active ui-corner-top").removeClass("ui-corner-all");
                this.active.next().addClass("ui-accordion-content-active").show();
                this.headers.attr("role", "tab").each(function() {
                    var b = a(this),
                        c = b.uniqueId().attr("id"),
                        e = b.next(),
                        k = e.uniqueId().attr("id");
                    b.attr("aria-controls", k);
                    e.attr("aria-labelledby", c)
                }).next().attr("role", "tabpanel");
                this.headers.not(this.active).attr({
                    "aria-selected": "false",
                    "aria-expanded": "false",
                    tabIndex: -1
                }).next().attr({
                    "aria-hidden": "true"
                }).hide();
                this.active.length ? this.active.attr({
                    "aria-selected": "true",
                    "aria-expanded": "true",
                    tabIndex: 0
                }).next().attr({
                    "aria-hidden": "false"
                }) : this.headers.eq(0).attr("tabIndex",
                    0);
                this._createIcons();
                this._setupEvents(b.event);
                if ("fill" === c) {
                    var d = e.height();
                    this.element.siblings(":visible").each(function() {
                        var b = a(this),
                            c = b.css("position");
                        "absolute" !== c && "fixed" !== c && (d -= b.outerHeight(!0))
                    });
                    this.headers.each(function() {
                        d -= a(this).outerHeight(!0)
                    });
                    this.headers.next().each(function() {
                        a(this).height(Math.max(0, d - a(this).innerHeight() + a(this).height()))
                    }).css("overflow", "auto")
                } else "auto" === c && (d = 0, this.headers.next().each(function() {
                    d = Math.max(d, a(this).css("height", "").height())
                }).height(d))
            },
            _activate: function(b) {
                b = this._findActive(b)[0];
                b !== this.active[0] && (b = b || this.active[0], this._eventHandler({
                    target: b,
                    currentTarget: b,
                    preventDefault: a.noop
                }))
            },
            _findActive: function(b) {
                return "number" === typeof b ? this.headers.eq(b) : a()
            },
            _setupEvents: function(b) {
                var c = {
                    keydown: "_keydown"
                };
                b && a.each(b.split(" "), function(b, a) {
                    c[a] = "_eventHandler"
                });
                this._off(this.headers.add(this.headers.next()));
                this._on(this.headers, c);
                this._on(this.headers.next(), {
                    keydown: "_panelKeyDown"
                });
                this._hoverable(this.headers);
                this._focusable(this.headers)
            },
            _eventHandler: function(b) {
                var c = this.options,
                    e = this.active,
                    d = a(b.currentTarget),
                    f = d[0] === e[0],
                    h = f && c.collapsible,
                    n = h ? a() : d.next(),
                    l = e.next();
                n = {
                    oldHeader: e,
                    oldPanel: l,
                    newHeader: h ? a() : d,
                    newPanel: n
                };
                b.preventDefault();
                f && !c.collapsible || !1 === this._trigger("beforeActivate", b, n) || (c.active = h ? !1 : this.headers.index(d), this.active = f ? a() : d, this._toggle(n), e.removeClass("ui-accordion-header-active ui-state-active"), c.icons && e.children(".ui-accordion-header-icon").removeClass(c.icons.activeHeader).addClass(c.icons.header),
                    f || (d.removeClass("ui-corner-all").addClass("ui-accordion-header-active ui-state-active ui-corner-top"), c.icons && d.children(".ui-accordion-header-icon").removeClass(c.icons.header).addClass(c.icons.activeHeader), d.next().addClass("ui-accordion-content-active")))
            },
            _toggle: function(b) {
                var c = b.newPanel,
                    e = this.prevShow.length ? this.prevShow : b.oldPanel;
                this.prevShow.add(this.prevHide).stop(!0, !0);
                this.prevShow = c;
                this.prevHide = e;
                this.options.animate ? this._animate(c, e, b) : (e.hide(), c.show(), this._toggleComplete(b));
                e.attr({
                    "aria-hidden": "true"
                });
                e.prev().attr({
                    "aria-selected": "false",
                    "aria-expanded": "false"
                });
                c.length && e.length ? e.prev().attr({
                    tabIndex: -1,
                    "aria-expanded": "false"
                }) : c.length && this.headers.filter(function() {
                    return 0 === parseInt(a(this).attr("tabIndex"), 10)
                }).attr("tabIndex", -1);
                c.attr("aria-hidden", "false").prev().attr({
                    "aria-selected": "true",
                    "aria-expanded": "true",
                    tabIndex: 0
                })
            },
            _animate: function(b, c, a) {
                var e, k, d = this,
                    f = 0,
                    h = b.css("box-sizing"),
                    n = b.length && (!c.length || b.index() < c.index()),
                    l = this.options.animate || {};
                n = n && l.down || l;
                var g = function() {
                    d._toggleComplete(a)
                };
                "number" === typeof n && (k = n);
                "string" === typeof n && (e = n);
                e = e || n.easing || l.easing;
                k = k || n.duration || l.duration;
                if (!c.length) return b.animate(this.showProps, k, e, g);
                if (!b.length) return c.animate(this.hideProps, k, e, g);
                var m = b.show().outerHeight();
                c.animate(this.hideProps, {
                    duration: k,
                    easing: e,
                    step: function(b, c) {
                        c.now = Math.round(b)
                    }
                });
                b.hide().animate(this.showProps, {
                    duration: k,
                    easing: e,
                    complete: g,
                    step: function(b, a) {
                        a.now = Math.round(b);
                        "height" !== a.prop ?
                            "content-box" === h && (f += a.now) : "content" !== d.options.heightStyle && (a.now = Math.round(m - c.outerHeight() - f), f = 0)
                    }
                })
            },
            _toggleComplete: function(b) {
                var c = b.oldPanel;
                c.removeClass("ui-accordion-content-active").prev().removeClass("ui-corner-top").addClass("ui-corner-all");
                c.length && (c.parent()[0].className = c.parent()[0].className);
                this._trigger("activate", null, b)
            }
        });
        a.widget("ui.menu", {
            version: "1.11.4",
            defaultElement: "\x3cul\x3e",
            delay: 300,
            options: {
                icons: {
                    submenu: "ui-icon-carat-1-e"
                },
                items: "\x3e *",
                menus: "ul",
                position: {
                    my: "left-1 top",
                    at: "right top"
                },
                role: "menu",
                blur: null,
                focus: null,
                select: null
            },
            _create: function() {
                this.activeMenu = this.element;
                this.mouseHandled = !1;
                this.element.uniqueId().addClass("ui-menu ui-widget ui-widget-content").toggleClass("ui-menu-icons", !!this.element.find(".ui-icon").length).attr({
                    role: this.options.role,
                    tabIndex: 0
                });
                this.options.disabled && this.element.addClass("ui-state-disabled").attr("aria-disabled", "true");
                this._on({
                    "mousedown .ui-menu-item": function(b) {
                        b.preventDefault()
                    },
                    "click .ui-menu-item": function(b) {
                        var c = a(b.target);
                        !this.mouseHandled && c.not(".ui-state-disabled").length && (this.select(b), b.isPropagationStopped() || (this.mouseHandled = !0), c.has(".ui-menu").length ? this.expand(b) : !this.element.is(":focus") && a(this.document[0].activeElement).closest(".ui-menu").length && (this.element.trigger("focus", [!0]), this.active && 1 === this.active.parents(".ui-menu").length && clearTimeout(this.timer)))
                    },
                    "mouseenter .ui-menu-item": function(b) {
                        if (!this.previousFilter) {
                            var c = a(b.currentTarget);
                            c.siblings(".ui-state-active").removeClass("ui-state-active");
                            this.focus(b, c)
                        }
                    },
                    mouseleave: "collapseAll",
                    "mouseleave .ui-menu": "collapseAll",
                    focus: function(b, c) {
                        var a = this.active || this.element.find(this.options.items).eq(0);
                        c || this.focus(b, a)
                    },
                    blur: function(b) {
                        this._delay(function() {
                            a.contains(this.element[0], this.document[0].activeElement) || this.collapseAll(b)
                        })
                    },
                    keydown: "_keydown"
                });
                this.refresh();
                this._on(this.document, {
                    click: function(b) {
                        this._closeOnDocumentClick(b) && this.collapseAll(b);
                        this.mouseHandled = !1
                    }
                })
            },
            _destroy: function() {
                this.element.removeAttr("aria-activedescendant").find(".ui-menu").addBack().removeClass("ui-menu ui-widget ui-widget-content ui-menu-icons ui-front").removeAttr("role").removeAttr("tabIndex").removeAttr("aria-labelledby").removeAttr("aria-expanded").removeAttr("aria-hidden").removeAttr("aria-disabled").removeUniqueId().show();
                this.element.find(".ui-menu-item").removeClass("ui-menu-item").removeAttr("role").removeAttr("aria-disabled").removeUniqueId().removeClass("ui-state-hover").removeAttr("tabIndex").removeAttr("role").removeAttr("aria-haspopup").children().each(function() {
                    var b =
                        a(this);
                    b.data("ui-menu-submenu-carat") && b.remove()
                });
                this.element.find(".ui-menu-divider").removeClass("ui-menu-divider ui-widget-content")
            },
            _keydown: function(b) {
                var c = !0;
                switch (b.keyCode) {
                    case a.ui.keyCode.PAGE_UP:
                        this.previousPage(b);
                        break;
                    case a.ui.keyCode.PAGE_DOWN:
                        this.nextPage(b);
                        break;
                    case a.ui.keyCode.HOME:
                        this._move("first", "first", b);
                        break;
                    case a.ui.keyCode.END:
                        this._move("last", "last", b);
                        break;
                    case a.ui.keyCode.UP:
                        this.previous(b);
                        break;
                    case a.ui.keyCode.DOWN:
                        this.next(b);
                        break;
                    case a.ui.keyCode.LEFT:
                        this.collapse(b);
                        break;
                    case a.ui.keyCode.RIGHT:
                        this.active && !this.active.is(".ui-state-disabled") && this.expand(b);
                        break;
                    case a.ui.keyCode.ENTER:
                    case a.ui.keyCode.SPACE:
                        this._activate(b);
                        break;
                    case a.ui.keyCode.ESCAPE:
                        this.collapse(b);
                        break;
                    default:
                        c = !1;
                        var e = this.previousFilter || "";
                        var d = String.fromCharCode(b.keyCode);
                        var f = !1;
                        clearTimeout(this.filterTimer);
                        d === e ? f = !0 : d = e + d;
                        e = this._filterMenuItems(d);
                        e = f && -1 !== e.index(this.active.next()) ? this.active.nextAll(".ui-menu-item") : e;
                        e.length || (d = String.fromCharCode(b.keyCode),
                            e = this._filterMenuItems(d));
                        e.length ? (this.focus(b, e), this.previousFilter = d, this.filterTimer = this._delay(function() {
                            delete this.previousFilter
                        }, 1E3)) : delete this.previousFilter
                }
                c && b.preventDefault()
            },
            _activate: function(b) {
                this.active.is(".ui-state-disabled") || (this.active.is("[aria-haspopup\x3d'true']") ? this.expand(b) : this.select(b))
            },
            refresh: function() {
                var b = this,
                    c = this.options.icons.submenu;
                var e = this.element.find(this.options.menus);
                this.element.toggleClass("ui-menu-icons", !!this.element.find(".ui-icon").length);
                e.filter(":not(.ui-menu)").addClass("ui-menu ui-widget ui-widget-content ui-front").hide().attr({
                    role: this.options.role,
                    "aria-hidden": "true",
                    "aria-expanded": "false"
                }).each(function() {
                    var b = a(this),
                        e = b.parent(),
                        k = a("\x3cspan\x3e").addClass("ui-menu-icon ui-icon " + c).data("ui-menu-submenu-carat", !0);
                    e.attr("aria-haspopup", "true").prepend(k);
                    b.attr("aria-labelledby", e.attr("id"))
                });
                e = e.add(this.element).find(this.options.items);
                e.not(".ui-menu-item").each(function() {
                    var c = a(this);
                    b._isDivider(c) && c.addClass("ui-widget-content ui-menu-divider")
                });
                e.not(".ui-menu-item, .ui-menu-divider").addClass("ui-menu-item").uniqueId().attr({
                    tabIndex: -1,
                    role: this._itemRole()
                });
                e.filter(".ui-state-disabled").attr("aria-disabled", "true");
                this.active && !a.contains(this.element[0], this.active[0]) && this.blur()
            },
            _itemRole: function() {
                return {
                    menu: "menuitem",
                    listbox: "option"
                } [this.options.role]
            },
            _setOption: function(b, c) {
                "icons" === b && this.element.find(".ui-menu-icon").removeClass(this.options.icons.submenu).addClass(c.submenu);
                "disabled" === b && this.element.toggleClass("ui-state-disabled",
                    !!c).attr("aria-disabled", c);
                this._super(b, c)
            },
            focus: function(b, c) {
                this.blur(b, b && "focus" === b.type);
                this._scrollIntoView(c);
                this.active = c.first();
                var a = this.active.addClass("ui-state-focus").removeClass("ui-state-active");
                this.options.role && this.element.attr("aria-activedescendant", a.attr("id"));
                this.active.parent().closest(".ui-menu-item").addClass("ui-state-active");
                b && "keydown" === b.type ? this._close() : this.timer = this._delay(function() {
                    this._close()
                }, this.delay);
                a = c.children(".ui-menu");
                a.length &&
                    b && /^mouse/.test(b.type) && this._startOpening(a);
                this.activeMenu = c.parent();
                this._trigger("focus", b, {
                    item: c
                })
            },
            _scrollIntoView: function(b) {
                if (this._hasScroll()) {
                    var c = parseFloat(a.css(this.activeMenu[0], "borderTopWidth")) || 0;
                    var e = parseFloat(a.css(this.activeMenu[0], "paddingTop")) || 0;
                    c = b.offset().top - this.activeMenu.offset().top - c - e;
                    e = this.activeMenu.scrollTop();
                    var d = this.activeMenu.height();
                    b = b.outerHeight();
                    0 > c ? this.activeMenu.scrollTop(e + c) : c + b > d && this.activeMenu.scrollTop(e + c - d + b)
                }
            },
            blur: function(b,
                c) {
                c || clearTimeout(this.timer);
                this.active && (this.active.removeClass("ui-state-focus"), this.active = null, this._trigger("blur", b, {
                    item: this.active
                }))
            },
            _startOpening: function(b) {
                clearTimeout(this.timer);
                "true" === b.attr("aria-hidden") && (this.timer = this._delay(function() {
                    this._close();
                    this._open(b)
                }, this.delay))
            },
            _open: function(b) {
                var c = a.extend({
                    of: this.active
                }, this.options.position);
                clearTimeout(this.timer);
                this.element.find(".ui-menu").not(b.parents(".ui-menu")).hide().attr("aria-hidden", "true");
                b.show().removeAttr("aria-hidden").attr("aria-expanded",
                    "true").position(c)
            },
            collapseAll: function(b, c) {
                clearTimeout(this.timer);
                this.timer = this._delay(function() {
                    var e = c ? this.element : a(b && b.target).closest(this.element.find(".ui-menu"));
                    e.length || (e = this.element);
                    this._close(e);
                    this.blur(b);
                    this.activeMenu = e
                }, this.delay)
            },
            _close: function(b) {
                b || (b = this.active ? this.active.parent() : this.element);
                b.find(".ui-menu").hide().attr("aria-hidden", "true").attr("aria-expanded", "false").end().find(".ui-state-active").not(".ui-state-focus").removeClass("ui-state-active")
            },
            _closeOnDocumentClick: function(b) {
                return !a(b.target).closest(".ui-menu").length
            },
            _isDivider: function(b) {
                return !/[^\-\u2014\u2013\s]/.test(b.text())
            },
            collapse: function(b) {
                var c = this.active && this.active.parent().closest(".ui-menu-item", this.element);
                c && c.length && (this._close(), this.focus(b, c))
            },
            expand: function(b) {
                var c = this.active && this.active.children(".ui-menu ").find(this.options.items).first();
                c && c.length && (this._open(c.parent()), this._delay(function() {
                    this.focus(b, c)
                }))
            },
            next: function(b) {
                this._move("next",
                    "first", b)
            },
            previous: function(b) {
                this._move("prev", "last", b)
            },
            isFirstItem: function() {
                return this.active && !this.active.prevAll(".ui-menu-item").length
            },
            isLastItem: function() {
                return this.active && !this.active.nextAll(".ui-menu-item").length
            },
            _move: function(b, c, a) {
                var e;
                this.active && (e = "first" === b || "last" === b ? this.active["first" === b ? "prevAll" : "nextAll"](".ui-menu-item").eq(-1) : this.active[b + "All"](".ui-menu-item").eq(0));
                e && e.length && this.active || (e = this.activeMenu.find(this.options.items)[c]());
                this.focus(a,
                    e)
            },
            nextPage: function(b) {
                var c;
                if (!this.active) this.next(b);
                else if (!this.isLastItem())
                    if (this._hasScroll()) {
                        var e = this.active.offset().top;
                        var d = this.element.height();
                        this.active.nextAll(".ui-menu-item").each(function() {
                            c = a(this);
                            return 0 > c.offset().top - e - d
                        });
                        this.focus(b, c)
                    } else this.focus(b, this.activeMenu.find(this.options.items)[this.active ? "last" : "first"]())
            },
            previousPage: function(b) {
                var c;
                if (!this.active) this.next(b);
                else if (!this.isFirstItem())
                    if (this._hasScroll()) {
                        var e = this.active.offset().top;
                        var d = this.element.height();
                        this.active.prevAll(".ui-menu-item").each(function() {
                            c = a(this);
                            return 0 < c.offset().top - e + d
                        });
                        this.focus(b, c)
                    } else this.focus(b, this.activeMenu.find(this.options.items).first())
            },
            _hasScroll: function() {
                return this.element.outerHeight() < this.element.prop("scrollHeight")
            },
            select: function(b) {
                this.active = this.active || a(b.target).closest(".ui-menu-item");
                var c = {
                    item: this.active
                };
                this.active.has(".ui-menu").length || this.collapseAll(b, !0);
                this._trigger("select", b, c)
            },
            _filterMenuItems: function(b) {
                b =
                    b.replace(/[\-\[\]{}()*+?.,\\\^$|#\s]/g, "\\$\x26");
                var c = new RegExp("^" + b, "i");
                return this.activeMenu.find(this.options.items).filter(".ui-menu-item").filter(function() {
                    return c.test(a.trim(a(this).text()))
                })
            }
        });
        a.widget("ui.autocomplete", {
            version: "1.11.4",
            defaultElement: "\x3cinput\x3e",
            options: {
                appendTo: null,
                autoFocus: !1,
                delay: 300,
                minLength: 1,
                position: {
                    my: "left top",
                    at: "left bottom",
                    collision: "none"
                },
                source: null,
                change: null,
                close: null,
                focus: null,
                open: null,
                response: null,
                search: null,
                select: null
            },
            requestIndex: 0,
            pending: 0,
            _create: function() {
                var b, c, e, d = this.element[0].nodeName.toLowerCase(),
                    f = "textarea" === d;
                d = "input" === d;
                this.isMultiLine = f ? !0 : d ? !1 : this.element.prop("isContentEditable");
                this.valueMethod = this.element[f || d ? "val" : "text"];
                this.isNewMenu = !0;
                this.element.addClass("ui-autocomplete-input").attr("autocomplete", "off");
                this._on(this.element, {
                    keydown: function(k) {
                        if (this.element.prop("readOnly")) c = e = b = !0;
                        else {
                            c = e = b = !1;
                            var d = a.ui.keyCode;
                            switch (k.keyCode) {
                                case d.PAGE_UP:
                                    b = !0;
                                    this._move("previousPage", k);
                                    break;
                                case d.PAGE_DOWN:
                                    b = !0;
                                    this._move("nextPage", k);
                                    break;
                                case d.UP:
                                    b = !0;
                                    this._keyEvent("previous", k);
                                    break;
                                case d.DOWN:
                                    b = !0;
                                    this._keyEvent("next", k);
                                    break;
                                case d.ENTER:
                                    this.menu.active && (b = !0, k.preventDefault(), this.menu.select(k));
                                    break;
                                case d.TAB:
                                    this.menu.active && this.menu.select(k);
                                    break;
                                case d.ESCAPE:
                                    this.menu.element.is(":visible") && (this.isMultiLine || this._value(this.term), this.close(k), k.preventDefault());
                                    break;
                                default:
                                    c = !0, this._searchTimeout(k)
                            }
                        }
                    },
                    keypress: function(e) {
                        if (b) b = !1, this.isMultiLine &&
                            !this.menu.element.is(":visible") || e.preventDefault();
                        else if (!c) {
                            var k = a.ui.keyCode;
                            switch (e.keyCode) {
                                case k.PAGE_UP:
                                    this._move("previousPage", e);
                                    break;
                                case k.PAGE_DOWN:
                                    this._move("nextPage", e);
                                    break;
                                case k.UP:
                                    this._keyEvent("previous", e);
                                    break;
                                case k.DOWN:
                                    this._keyEvent("next", e)
                            }
                        }
                    },
                    input: function(b) {
                        e ? (e = !1, b.preventDefault()) : this._searchTimeout(b)
                    },
                    focus: function() {
                        this.selectedItem = null;
                        this.previous = this._value()
                    },
                    blur: function(b) {
                        this.cancelBlur ? delete this.cancelBlur : (clearTimeout(this.searching),
                            this.close(b), this._change(b))
                    }
                });
                this._initSource();
                this.menu = a("\x3cul\x3e").addClass("ui-autocomplete ui-front").appendTo(this._appendTo()).menu({
                    role: null
                }).hide().menu("instance");
                this._on(this.menu.element, {
                    mousedown: function(b) {
                        b.preventDefault();
                        this.cancelBlur = !0;
                        this._delay(function() {
                            delete this.cancelBlur
                        });
                        var c = this.menu.element[0];
                        a(b.target).closest(".ui-menu-item").length || this._delay(function() {
                            var b = this;
                            this.document.one("mousedown", function(e) {
                                e.target === b.element[0] || e.target ===
                                    c || a.contains(c, e.target) || b.close()
                            })
                        })
                    },
                    menufocus: function(b, c) {
                        if (this.isNewMenu && (this.isNewMenu = !1, b.originalEvent && /^mouse/.test(b.originalEvent.type))) {
                            this.menu.blur();
                            this.document.one("mousemove", function() {
                                a(b.target).trigger(b.originalEvent)
                            });
                            return
                        }
                        var e = c.item.data("ui-autocomplete-item");
                        !1 !== this._trigger("focus", b, {
                            item: e
                        }) && b.originalEvent && /^key/.test(b.originalEvent.type) && this._value(e.value);
                        (c = c.item.attr("aria-label") || e.value) && a.trim(c).length && (this.liveRegion.children().hide(),
                            a("\x3cdiv\x3e").text(c).appendTo(this.liveRegion))
                    },
                    menuselect: function(b, c) {
                        var a = c.item.data("ui-autocomplete-item"),
                            e = this.previous;
                        this.element[0] !== this.document[0].activeElement && (this.element.focus(), this.previous = e, this._delay(function() {
                            this.previous = e;
                            this.selectedItem = a
                        }));
                        !1 !== this._trigger("select", b, {
                            item: a
                        }) && this._value(a.value);
                        this.term = this._value();
                        this.close(b);
                        this.selectedItem = a
                    }
                });
                this.liveRegion = a("\x3cspan\x3e", {
                    role: "status",
                    "aria-live": "assertive",
                    "aria-relevant": "additions"
                }).addClass("ui-helper-hidden-accessible").appendTo(this.document[0].body);
                this._on(this.window, {
                    beforeunload: function() {
                        this.element.removeAttr("autocomplete")
                    }
                })
            },
            _destroy: function() {
                clearTimeout(this.searching);
                this.element.removeClass("ui-autocomplete-input").removeAttr("autocomplete");
                this.menu.element.remove();
                this.liveRegion.remove()
            },
            _setOption: function(b, c) {
                this._super(b, c);
                "source" === b && this._initSource();
                "appendTo" === b && this.menu.element.appendTo(this._appendTo());
                "disabled" === b && c && this.xhr && this.xhr.abort()
            },
            _appendTo: function() {
                var b = this.options.appendTo;
                b && (b = b.jquery || b.nodeType ? a(b) : this.document.find(b).eq(0));
                b && b[0] || (b = this.element.closest(".ui-front"));
                b.length || (b = this.document[0].body);
                return b
            },
            _initSource: function() {
                var b = this;
                if (a.isArray(this.options.source)) {
                    var c = this.options.source;
                    this.source = function(b, e) {
                        e(a.ui.autocomplete.filter(c, b.term))
                    }
                } else if ("string" === typeof this.options.source) {
                    var e = this.options.source;
                    this.source = function(c, k) {
                        b.xhr && b.xhr.abort();
                        b.xhr = a.ajax({
                            url: e,
                            data: c,
                            dataType: "json",
                            success: function(b) {
                                k(b)
                            },
                            error: function() {
                                k([])
                            }
                        })
                    }
                } else this.source = this.options.source
            },
            _searchTimeout: function(b) {
                clearTimeout(this.searching);
                this.searching = this._delay(function() {
                    var c = this.term === this._value(),
                        a = this.menu.element.is(":visible"),
                        e = b.altKey || b.ctrlKey || b.metaKey || b.shiftKey;
                    if (!c || c && !a && !e) this.selectedItem = null, this.search(null, b)
                }, this.options.delay)
            },
            search: function(b, c) {
                b = null != b ? b : this._value();
                this.term = this._value();
                if (b.length < this.options.minLength) return this.close(c);
                if (!1 !== this._trigger("search",
                        c)) return this._search(b)
            },
            _search: function(b) {
                this.pending++;
                this.element.addClass("ui-autocomplete-loading");
                this.cancelSearch = !1;
                this.source({
                    term: b
                }, this._response())
            },
            _response: function() {
                var b = ++this.requestIndex;
                return a.proxy(function(c) {
                    b === this.requestIndex && this.__response(c);
                    this.pending--;
                    this.pending || this.element.removeClass("ui-autocomplete-loading")
                }, this)
            },
            __response: function(b) {
                b && (b = this._normalize(b));
                this._trigger("response", null, {
                    content: b
                });
                !this.options.disabled && b && b.length &&
                    !this.cancelSearch ? (this._suggest(b), this._trigger("open")) : this._close()
            },
            close: function(b) {
                this.cancelSearch = !0;
                this._close(b)
            },
            _close: function(b) {
                this.menu.element.is(":visible") && (this.menu.element.hide(), this.menu.blur(), this.isNewMenu = !0, this._trigger("close", b))
            },
            _change: function(b) {
                this.previous !== this._value() && this._trigger("change", b, {
                    item: this.selectedItem
                })
            },
            _normalize: function(b) {
                return b.length && b[0].label && b[0].value ? b : a.map(b, function(b) {
                    return "string" === typeof b ? {
                            label: b,
                            value: b
                        } :
                        a.extend({}, b, {
                            label: b.label || b.value,
                            value: b.value || b.label
                        })
                })
            },
            _suggest: function(b) {
                var c = this.menu.element.empty();
                this._renderMenu(c, b);
                this.isNewMenu = !0;
                this.menu.refresh();
                c.show();
                this._resizeMenu();
                c.position(a.extend({
                    of: this.element
                }, this.options.position));
                this.options.autoFocus && this.menu.next()
            },
            _resizeMenu: function() {
                var b = this.menu.element;
                b.outerWidth(Math.max(b.width("").outerWidth() + 1, this.element.outerWidth()))
            },
            _renderMenu: function(b, c) {
                var e = this;
                a.each(c, function(c, a) {
                    e._renderItemData(b,
                        a)
                })
            },
            _renderItemData: function(b, c) {
                return this._renderItem(b, c).data("ui-autocomplete-item", c)
            },
            _renderItem: function(b, c) {
                return a("\x3cli\x3e").text(c.label).appendTo(b)
            },
            _move: function(b, c) {
                if (this.menu.element.is(":visible"))
                    if (this.menu.isFirstItem() && /^previous/.test(b) || this.menu.isLastItem() && /^next/.test(b)) this.isMultiLine || this._value(this.term), this.menu.blur();
                    else this.menu[b](c);
                else this.search(null, c)
            },
            widget: function() {
                return this.menu.element
            },
            _value: function() {
                return this.valueMethod.apply(this.element,
                    arguments)
            },
            _keyEvent: function(b, c) {
                if (!this.isMultiLine || this.menu.element.is(":visible")) this._move(b, c), c.preventDefault()
            }
        });
        a.extend(a.ui.autocomplete, {
            escapeRegex: function(b) {
                return b.replace(/[\-\[\]{}()*+?.,\\\^$|#\s]/g, "\\$\x26")
            },
            filter: function(b, c) {
                var e = new RegExp(a.ui.autocomplete.escapeRegex(c), "i");
                return a.grep(b, function(b) {
                    return e.test(b.label || b.value || b)
                })
            }
        });
        a.widget("ui.autocomplete", a.ui.autocomplete, {
            options: {
                messages: {
                    noResults: "No search results.",
                    results: function(b) {
                        return b +
                            (1 < b ? " results are" : " result is") + " available, use up and down arrow keys to navigate."
                    }
                }
            },
            __response: function(b) {
                this._superApply(arguments);
                if (!this.options.disabled && !this.cancelSearch) {
                    var c = b && b.length ? this.options.messages.results(b.length) : this.options.messages.noResults;
                    this.liveRegion.children().hide();
                    a("\x3cdiv\x3e").text(c).appendTo(this.liveRegion)
                }
            }
        });
        var e, y = function() {
                var b = a(this);
                setTimeout(function() {
                    b.find(":ui-button").button("refresh")
                }, 1)
            },
            x = function(b) {
                var c = b.name,
                    e = b.form,
                    d = a([]);
                c && (c = c.replace(/'/g, "\\'"), d = e ? a(e).find("[name\x3d'" + c + "'][type\x3dradio]") : a("[name\x3d'" + c + "'][type\x3dradio]", b.ownerDocument).filter(function() {
                    return !this.form
                }));
                return d
            };
        a.widget("ui.button", {
            version: "1.11.4",
            defaultElement: "\x3cbutton\x3e",
            options: {
                disabled: null,
                text: !0,
                label: null,
                icons: {
                    primary: null,
                    secondary: null
                }
            },
            _create: function() {
                this.element.closest("form").unbind("reset" + this.eventNamespace).bind("reset" + this.eventNamespace, y);
                "boolean" !== typeof this.options.disabled ? this.options.disabled = !!this.element.prop("disabled") : this.element.prop("disabled", this.options.disabled);
                this._determineButtonType();
                this.hasTitle = !!this.buttonElement.attr("title");
                var b = this,
                    c = this.options,
                    k = "checkbox" === this.type || "radio" === this.type,
                    d = k ? "" : "ui-state-active";
                null === c.label && (c.label = "input" === this.type ? this.buttonElement.val() : this.buttonElement.html());
                this._hoverable(this.buttonElement);
                this.buttonElement.addClass("ui-button ui-widget ui-state-default ui-corner-all").attr("role", "button").bind("mouseenter" +
                    this.eventNamespace,
                    function() {
                        c.disabled || this === e && a(this).addClass("ui-state-active")
                    }).bind("mouseleave" + this.eventNamespace, function() {
                    c.disabled || a(this).removeClass(d)
                }).bind("click" + this.eventNamespace, function(b) {
                    c.disabled && (b.preventDefault(), b.stopImmediatePropagation())
                });
                this._on({
                    focus: function() {
                        this.buttonElement.addClass("ui-state-focus")
                    },
                    blur: function() {
                        this.buttonElement.removeClass("ui-state-focus")
                    }
                });
                k && this.element.bind("change" + this.eventNamespace, function() {
                    b.refresh()
                });
                "checkbox" === this.type ? this.buttonElement.bind("click" + this.eventNamespace, function() {
                    if (c.disabled) return !1
                }) : "radio" === this.type ? this.buttonElement.bind("click" + this.eventNamespace, function() {
                    if (c.disabled) return !1;
                    a(this).addClass("ui-state-active");
                    b.buttonElement.attr("aria-pressed", "true");
                    var e = b.element[0];
                    x(e).not(e).map(function() {
                        return a(this).button("widget")[0]
                    }).removeClass("ui-state-active").attr("aria-pressed", "false")
                }) : (this.buttonElement.bind("mousedown" + this.eventNamespace, function() {
                        if (c.disabled) return !1;
                        a(this).addClass("ui-state-active");
                        e = this;
                        b.document.one("mouseup", function() {
                            e = null
                        })
                    }).bind("mouseup" + this.eventNamespace, function() {
                        if (c.disabled) return !1;
                        a(this).removeClass("ui-state-active")
                    }).bind("keydown" + this.eventNamespace, function(b) {
                        if (c.disabled) return !1;
                        b.keyCode !== a.ui.keyCode.SPACE && b.keyCode !== a.ui.keyCode.ENTER || a(this).addClass("ui-state-active")
                    }).bind("keyup" + this.eventNamespace + " blur" + this.eventNamespace, function() {
                        a(this).removeClass("ui-state-active")
                    }), this.buttonElement.is("a") &&
                    this.buttonElement.keyup(function(b) {
                        b.keyCode === a.ui.keyCode.SPACE && a(this).click()
                    }));
                this._setOption("disabled", c.disabled);
                this._resetButton()
            },
            _determineButtonType: function() {
                this.element.is("[type\x3dcheckbox]") ? this.type = "checkbox" : this.element.is("[type\x3dradio]") ? this.type = "radio" : this.element.is("input") ? this.type = "input" : this.type = "button";
                if ("checkbox" === this.type || "radio" === this.type) {
                    var b = this.element.parents().last();
                    var c = "label[for\x3d'" + this.element.attr("id") + "']";
                    this.buttonElement =
                        b.find(c);
                    this.buttonElement.length || (b = b.length ? b.siblings() : this.element.siblings(), this.buttonElement = b.filter(c), this.buttonElement.length || (this.buttonElement = b.find(c)));
                    this.element.addClass("ui-helper-hidden-accessible");
                    (b = this.element.is(":checked")) && this.buttonElement.addClass("ui-state-active");
                    this.buttonElement.prop("aria-pressed", b)
                } else this.buttonElement = this.element
            },
            widget: function() {
                return this.buttonElement
            },
            _destroy: function() {
                this.element.removeClass("ui-helper-hidden-accessible");
                this.buttonElement.removeClass("ui-button ui-widget ui-state-default ui-corner-all ui-state-active ui-button-icons-only ui-button-icon-only ui-button-text-icons ui-button-text-icon-primary ui-button-text-icon-secondary ui-button-text-only").removeAttr("role").removeAttr("aria-pressed").html(this.buttonElement.find(".ui-button-text").html());
                this.hasTitle || this.buttonElement.removeAttr("title")
            },
            _setOption: function(b, c) {
                this._super(b, c);
                "disabled" === b ? (this.widget().toggleClass("ui-state-disabled",
                    !!c), this.element.prop("disabled", !!c), c && ("checkbox" === this.type || "radio" === this.type ? this.buttonElement.removeClass("ui-state-focus") : this.buttonElement.removeClass("ui-state-focus ui-state-active"))) : this._resetButton()
            },
            refresh: function() {
                var b = this.element.is("input, button") ? this.element.is(":disabled") : this.element.hasClass("ui-button-disabled");
                b !== this.options.disabled && this._setOption("disabled", b);
                "radio" === this.type ? x(this.element[0]).each(function() {
                    a(this).is(":checked") ? a(this).button("widget").addClass("ui-state-active").attr("aria-pressed",
                        "true") : a(this).button("widget").removeClass("ui-state-active").attr("aria-pressed", "false")
                }) : "checkbox" === this.type && (this.element.is(":checked") ? this.buttonElement.addClass("ui-state-active").attr("aria-pressed", "true") : this.buttonElement.removeClass("ui-state-active").attr("aria-pressed", "false"))
            },
            _resetButton: function() {
                if ("input" === this.type) this.options.label && this.element.val(this.options.label);
                else {
                    var b = this.buttonElement.removeClass("ui-button-icons-only ui-button-icon-only ui-button-text-icons ui-button-text-icon-primary ui-button-text-icon-secondary ui-button-text-only"),
                        c = a("\x3cspan\x3e\x3c/span\x3e", this.document[0]).addClass("ui-button-text").html(this.options.label).appendTo(b.empty()).text(),
                        e = this.options.icons,
                        d = e.primary && e.secondary,
                        f = [];
                    e.primary || e.secondary ? (this.options.text && f.push("ui-button-text-icon" + (d ? "s" : e.primary ? "-primary" : "-secondary")), e.primary && b.prepend("\x3cspan class\x3d'ui-button-icon-primary ui-icon " + e.primary + "'\x3e\x3c/span\x3e"), e.secondary && b.append("\x3cspan class\x3d'ui-button-icon-secondary ui-icon " + e.secondary + "'\x3e\x3c/span\x3e"),
                        this.options.text || (f.push(d ? "ui-button-icons-only" : "ui-button-icon-only"), this.hasTitle || b.attr("title", a.trim(c)))) : f.push("ui-button-text-only");
                    b.addClass(f.join(" "))
                }
            }
        });
        a.widget("ui.buttonset", {
            version: "1.11.4",
            options: {
                items: "button, input[type\x3dbutton], input[type\x3dsubmit], input[type\x3dreset], input[type\x3dcheckbox], input[type\x3dradio], a, :data(ui-button)"
            },
            _create: function() {
                this.element.addClass("ui-buttonset")
            },
            _init: function() {
                this.refresh()
            },
            _setOption: function(b, c) {
                "disabled" ===
                b && this.buttons.button("option", b, c);
                this._super(b, c)
            },
            refresh: function() {
                var b = "rtl" === this.element.css("direction"),
                    c = this.element.find(this.options.items),
                    e = c.filter(":ui-button");
                c.not(":ui-button").button();
                e.button("refresh");
                this.buttons = c.map(function() {
                    return a(this).button("widget")[0]
                }).removeClass("ui-corner-all ui-corner-left ui-corner-right").filter(":first").addClass(b ? "ui-corner-right" : "ui-corner-left").end().filter(":last").addClass(b ? "ui-corner-left" : "ui-corner-right").end().end()
            },
            _destroy: function() {
                this.element.removeClass("ui-buttonset");
                this.buttons.map(function() {
                    return a(this).button("widget")[0]
                }).removeClass("ui-corner-left ui-corner-right").end().button("destroy")
            }
        });
        a.extend(a.ui, {
            datepicker: {
                version: "1.11.4"
            }
        });
        var w;
        a.extend(h.prototype, {
            markerClassName: "hasDatepicker",
            maxRows: 4,
            _widgetDatepicker: function() {
                return this.dpDiv
            },
            setDefaults: function(b) {
                t(this._defaults, b || {});
                return this
            },
            _attachDatepicker: function(b, c) {
                var e = b.nodeName.toLowerCase();
                var d = "div" ===
                    e || "span" === e;
                b.id || (this.uuid += 1, b.id = "dp" + this.uuid);
                var f = this._newInst(a(b), d);
                f.settings = a.extend({}, c || {});
                "input" === e ? this._connectDatepicker(b, f) : d && this._inlineDatepicker(b, f)
            },
            _newInst: function(b, c) {
                return {
                    id: b[0].id.replace(/([^A-Za-z0-9_\-])/g, "\\\\$1"),
                    input: b,
                    selectedDay: 0,
                    selectedMonth: 0,
                    selectedYear: 0,
                    drawMonth: 0,
                    drawYear: 0,
                    inline: c,
                    dpDiv: c ? d(a("\x3cdiv class\x3d'" + this._inlineClass + " ui-datepicker ui-widget ui-widget-content ui-helper-clearfix ui-corner-all'\x3e\x3c/div\x3e")) : this.dpDiv
                }
            },
            _connectDatepicker: function(b, c) {
                var e = a(b);
                c.append = a([]);
                c.trigger = a([]);
                e.hasClass(this.markerClassName) || (this._attachments(e, c), e.addClass(this.markerClassName).keydown(this._doKeyDown).keypress(this._doKeyPress).keyup(this._doKeyUp), this._autoSize(c), a.data(b, "datepicker", c), c.settings.disabled && this._disableDatepicker(b))
            },
            _attachments: function(b, c) {
                var e = this._get(c, "appendText");
                var d = this._get(c, "isRTL");
                c.append && c.append.remove();
                e && (c.append = a("\x3cspan class\x3d'" + this._appendClass +
                    "'\x3e" + e + "\x3c/span\x3e"), b[d ? "before" : "after"](c.append));
                b.unbind("focus", this._showDatepicker);
                c.trigger && c.trigger.remove();
                e = this._get(c, "showOn");
                "focus" !== e && "both" !== e || b.focus(this._showDatepicker);
                if ("button" === e || "both" === e) {
                    e = this._get(c, "buttonText");
                    var f = this._get(c, "buttonImage");
                    c.trigger = a(this._get(c, "buttonImageOnly") ? a("\x3cimg/\x3e").addClass(this._triggerClass).attr({
                        src: f,
                        alt: e,
                        title: e
                    }) : a("\x3cbutton type\x3d'button'\x3e\x3c/button\x3e").addClass(this._triggerClass).html(f ?
                        a("\x3cimg/\x3e").attr({
                            src: f,
                            alt: e,
                            title: e
                        }) : e));
                    b[d ? "before" : "after"](c.trigger);
                    c.trigger.click(function() {
                        a.datepicker._datepickerShowing && a.datepicker._lastInput === b[0] ? a.datepicker._hideDatepicker() : (a.datepicker._datepickerShowing && a.datepicker._lastInput !== b[0] && a.datepicker._hideDatepicker(), a.datepicker._showDatepicker(b[0]));
                        return !1
                    })
                }
            },
            _autoSize: function(b) {
                if (this._get(b, "autoSize") && !b.inline) {
                    var c, a, e, d = new Date(2009, 11, 20),
                        f = this._get(b, "dateFormat");
                    if (f.match(/[DM]/)) {
                        var h = function(b) {
                            for (e =
                                a = c = 0; e < b.length; e++) b[e].length > c && (c = b[e].length, a = e);
                            return a
                        };
                        d.setMonth(h(this._get(b, f.match(/MM/) ? "monthNames" : "monthNamesShort")));
                        d.setDate(h(this._get(b, f.match(/DD/) ? "dayNames" : "dayNamesShort")) + 20 - d.getDay())
                    }
                    b.input.attr("size", this._formatDate(b, d).length)
                }
            },
            _inlineDatepicker: function(b, c) {
                var e = a(b);
                e.hasClass(this.markerClassName) || (e.addClass(this.markerClassName).append(c.dpDiv), a.data(b, "datepicker", c), this._setDate(c, this._getDefaultDate(c), !0), this._updateDatepicker(c), this._updateAlternate(c),
                    c.settings.disabled && this._disableDatepicker(b), c.dpDiv.css("display", "block"))
            },
            _dialogDatepicker: function(b, c, e, d, f) {
                b = this._dialogInst;
                b || (this.uuid += 1, b = "dp" + this.uuid, this._dialogInput = a("\x3cinput type\x3d'text' id\x3d'" + b + "' style\x3d'position: absolute; top: -100px; width: 0px;'/\x3e"), this._dialogInput.keydown(this._doKeyDown), a("body").append(this._dialogInput), b = this._dialogInst = this._newInst(this._dialogInput, !1), b.settings = {}, a.data(this._dialogInput[0], "datepicker", b));
                t(b.settings,
                    d || {});
                c = c && c.constructor === Date ? this._formatDate(b, c) : c;
                this._dialogInput.val(c);
                this._pos = f ? f.length ? f : [f.pageX, f.pageY] : null;
                if (!this._pos) {
                    c = document.documentElement.clientWidth;
                    d = document.documentElement.clientHeight;
                    f = document.documentElement.scrollLeft || document.body.scrollLeft;
                    var k = document.documentElement.scrollTop || document.body.scrollTop;
                    this._pos = [c / 2 - 100 + f, d / 2 - 150 + k]
                }
                this._dialogInput.css("left", this._pos[0] + 20 + "px").css("top", this._pos[1] + "px");
                b.settings.onSelect = e;
                this._inDialog = !0;
                this.dpDiv.addClass(this._dialogClass);
                this._showDatepicker(this._dialogInput[0]);
                a.blockUI && a.blockUI(this.dpDiv);
                a.data(this._dialogInput[0], "datepicker", b);
                return this
            },
            _destroyDatepicker: function(b) {
                var c = a(b),
                    e = a.data(b, "datepicker");
                if (c.hasClass(this.markerClassName)) {
                    var d = b.nodeName.toLowerCase();
                    a.removeData(b, "datepicker");
                    "input" === d ? (e.append.remove(), e.trigger.remove(), c.removeClass(this.markerClassName).unbind("focus", this._showDatepicker).unbind("keydown", this._doKeyDown).unbind("keypress",
                        this._doKeyPress).unbind("keyup", this._doKeyUp)) : "div" !== d && "span" !== d || c.removeClass(this.markerClassName).empty();
                    w === e && (w = null)
                }
            },
            _enableDatepicker: function(b) {
                var c = a(b),
                    e = a.data(b, "datepicker");
                if (c.hasClass(this.markerClassName)) {
                    var d = b.nodeName.toLowerCase();
                    if ("input" === d) b.disabled = !1, e.trigger.filter("button").each(function() {
                        this.disabled = !1
                    }).end().filter("img").css({
                        opacity: "1.0",
                        cursor: ""
                    });
                    else if ("div" === d || "span" === d) d = c.children("." + this._inlineClass), d.children().removeClass("ui-state-disabled"),
                        d.find("select.ui-datepicker-month, select.ui-datepicker-year").prop("disabled", !1);
                    this._disabledInputs = a.map(this._disabledInputs, function(c) {
                        return c === b ? null : c
                    })
                }
            },
            _disableDatepicker: function(b) {
                var c = a(b),
                    e = a.data(b, "datepicker");
                if (c.hasClass(this.markerClassName)) {
                    var d = b.nodeName.toLowerCase();
                    if ("input" === d) b.disabled = !0, e.trigger.filter("button").each(function() {
                        this.disabled = !0
                    }).end().filter("img").css({
                        opacity: "0.5",
                        cursor: "default"
                    });
                    else if ("div" === d || "span" === d) d = c.children("." + this._inlineClass),
                        d.children().addClass("ui-state-disabled"), d.find("select.ui-datepicker-month, select.ui-datepicker-year").prop("disabled", !0);
                    this._disabledInputs = a.map(this._disabledInputs, function(c) {
                        return c === b ? null : c
                    });
                    this._disabledInputs[this._disabledInputs.length] = b
                }
            },
            _isDisabledDatepicker: function(b) {
                if (!b) return !1;
                for (var c = 0; c < this._disabledInputs.length; c++)
                    if (this._disabledInputs[c] === b) return !0;
                return !1
            },
            _getInst: function(b) {
                try {
                    return a.data(b, "datepicker")
                } catch (c) {
                    throw "Missing instance data for this datepicker";
                }
            },
            _optionDatepicker: function(b, c, e) {
                var d = this._getInst(b);
                if (2 === arguments.length && "string" === typeof c) return "defaults" === c ? a.extend({}, a.datepicker._defaults) : d ? "all" === c ? a.extend({}, d.settings) : this._get(d, c) : null;
                var k = c || {};
                "string" === typeof c && (k = {}, k[c] = e);
                if (d) {
                    this._curInst === d && this._hideDatepicker();
                    var f = this._getDateDatepicker(b, !0);
                    var h = this._getMinMaxDate(d, "min");
                    var n = this._getMinMaxDate(d, "max");
                    t(d.settings, k);
                    null !== h && void 0 !== k.dateFormat && void 0 === k.minDate && (d.settings.minDate =
                        this._formatDate(d, h));
                    null !== n && void 0 !== k.dateFormat && void 0 === k.maxDate && (d.settings.maxDate = this._formatDate(d, n));
                    "disabled" in k && (k.disabled ? this._disableDatepicker(b) : this._enableDatepicker(b));
                    this._attachments(a(b), d);
                    this._autoSize(d);
                    this._setDate(d, f);
                    this._updateAlternate(d);
                    this._updateDatepicker(d)
                }
            },
            _changeDatepicker: function(b, c, a) {
                this._optionDatepicker(b, c, a)
            },
            _refreshDatepicker: function(b) {
                (b = this._getInst(b)) && this._updateDatepicker(b)
            },
            _setDateDatepicker: function(b, c) {
                if (b = this._getInst(b)) this._setDate(b,
                    c), this._updateDatepicker(b), this._updateAlternate(b)
            },
            _getDateDatepicker: function(b, c) {
                (b = this._getInst(b)) && !b.inline && this._setDateFromField(b, c);
                return b ? this._getDate(b) : null
            },
            _doKeyDown: function(b) {
                var c = a.datepicker._getInst(b.target);
                var e = !0;
                var d = c.dpDiv.is(".ui-datepicker-rtl");
                c._keyEvent = !0;
                if (a.datepicker._datepickerShowing) switch (b.keyCode) {
                    case 9:
                        a.datepicker._hideDatepicker();
                        e = !1;
                        break;
                    case 13:
                        return e = a("td." + a.datepicker._dayOverClass + ":not(." + a.datepicker._currentClass + ")", c.dpDiv),
                            e[0] && a.datepicker._selectDay(b.target, c.selectedMonth, c.selectedYear, e[0]), (b = a.datepicker._get(c, "onSelect")) ? (e = a.datepicker._formatDate(c), b.apply(c.input ? c.input[0] : null, [e, c])) : a.datepicker._hideDatepicker(), !1;
                    case 27:
                        a.datepicker._hideDatepicker();
                        break;
                    case 33:
                        a.datepicker._adjustDate(b.target, b.ctrlKey ? -a.datepicker._get(c, "stepBigMonths") : -a.datepicker._get(c, "stepMonths"), "M");
                        break;
                    case 34:
                        a.datepicker._adjustDate(b.target, b.ctrlKey ? +a.datepicker._get(c, "stepBigMonths") : +a.datepicker._get(c,
                            "stepMonths"), "M");
                        break;
                    case 35:
                        (b.ctrlKey || b.metaKey) && a.datepicker._clearDate(b.target);
                        e = b.ctrlKey || b.metaKey;
                        break;
                    case 36:
                        (b.ctrlKey || b.metaKey) && a.datepicker._gotoToday(b.target);
                        e = b.ctrlKey || b.metaKey;
                        break;
                    case 37:
                        (b.ctrlKey || b.metaKey) && a.datepicker._adjustDate(b.target, d ? 1 : -1, "D");
                        e = b.ctrlKey || b.metaKey;
                        b.originalEvent.altKey && a.datepicker._adjustDate(b.target, b.ctrlKey ? -a.datepicker._get(c, "stepBigMonths") : -a.datepicker._get(c, "stepMonths"), "M");
                        break;
                    case 38:
                        (b.ctrlKey || b.metaKey) && a.datepicker._adjustDate(b.target,
                            -7, "D");
                        e = b.ctrlKey || b.metaKey;
                        break;
                    case 39:
                        (b.ctrlKey || b.metaKey) && a.datepicker._adjustDate(b.target, d ? -1 : 1, "D");
                        e = b.ctrlKey || b.metaKey;
                        b.originalEvent.altKey && a.datepicker._adjustDate(b.target, b.ctrlKey ? +a.datepicker._get(c, "stepBigMonths") : +a.datepicker._get(c, "stepMonths"), "M");
                        break;
                    case 40:
                        (b.ctrlKey || b.metaKey) && a.datepicker._adjustDate(b.target, 7, "D");
                        e = b.ctrlKey || b.metaKey;
                        break;
                    default:
                        e = !1
                } else 36 === b.keyCode && b.ctrlKey ? a.datepicker._showDatepicker(this) : e = !1;
                e && (b.preventDefault(), b.stopPropagation())
            },
            _doKeyPress: function(b) {
                var c = a.datepicker._getInst(b.target);
                if (a.datepicker._get(c, "constrainInput")) {
                    c = a.datepicker._possibleChars(a.datepicker._get(c, "dateFormat"));
                    var e = String.fromCharCode(null == b.charCode ? b.keyCode : b.charCode);
                    return b.ctrlKey || b.metaKey || " " > e || !c || -1 < c.indexOf(e)
                }
            },
            _doKeyUp: function(b) {
                var c;
                b = a.datepicker._getInst(b.target);
                if (b.input.val() !== b.lastVal) try {
                    if (c = a.datepicker.parseDate(a.datepicker._get(b, "dateFormat"), b.input ? b.input.val() : null, a.datepicker._getFormatConfig(b))) a.datepicker._setDateFromField(b),
                        a.datepicker._updateAlternate(b), a.datepicker._updateDatepicker(b)
                } catch (k) {}
                return !0
            },
            _showDatepicker: function(b) {
                b = b.target || b;
                "input" !== b.nodeName.toLowerCase() && (b = a("input", b.parentNode)[0]);
                if (!a.datepicker._isDisabledDatepicker(b) && a.datepicker._lastInput !== b) {
                    var c = a.datepicker._getInst(b);
                    a.datepicker._curInst && a.datepicker._curInst !== c && (a.datepicker._curInst.dpDiv.stop(!0, !0), c && a.datepicker._datepickerShowing && a.datepicker._hideDatepicker(a.datepicker._curInst.input[0]));
                    var e = (e = a.datepicker._get(c,
                        "beforeShow")) ? e.apply(b, [b, c]) : {};
                    if (!1 !== e) {
                        t(c.settings, e);
                        c.lastVal = null;
                        a.datepicker._lastInput = b;
                        a.datepicker._setDateFromField(c);
                        a.datepicker._inDialog && (b.value = "");
                        a.datepicker._pos || (a.datepicker._pos = a.datepicker._findPos(b), a.datepicker._pos[1] += b.offsetHeight);
                        var d = !1;
                        a(b).parents().each(function() {
                            d |= "fixed" === a(this).css("position");
                            return !d
                        });
                        e = {
                            left: a.datepicker._pos[0],
                            top: a.datepicker._pos[1]
                        };
                        a.datepicker._pos = null;
                        c.dpDiv.empty();
                        c.dpDiv.css({
                            position: "absolute",
                            display: "block",
                            top: "-1000px"
                        });
                        a.datepicker._updateDatepicker(c);
                        e = a.datepicker._checkOffset(c, e, d);
                        c.dpDiv.css({
                            position: a.datepicker._inDialog && a.blockUI ? "static" : d ? "fixed" : "absolute",
                            display: "none",
                            left: e.left + "px",
                            top: e.top + "px"
                        });
                        if (!c.inline) {
                            e = a.datepicker._get(c, "showAnim");
                            var f = a.datepicker._get(c, "duration");
                            c.dpDiv.css("z-index", m(a(b)) + 1);
                            a.datepicker._datepickerShowing = !0;
                            if (a.effects && a.effects.effect[e]) c.dpDiv.show(e, a.datepicker._get(c, "showOptions"), f);
                            else c.dpDiv[e || "show"](e ? f : null);
                            a.datepicker._shouldFocusInput(c) &&
                                c.input.focus();
                            a.datepicker._curInst = c
                        }
                    }
                }
            },
            _updateDatepicker: function(b) {
                this.maxRows = 4;
                w = b;
                b.dpDiv.empty().append(this._generateHTML(b));
                this._attachHandlers(b);
                var c = this._getNumberOfMonths(b),
                    e = c[1],
                    d = b.dpDiv.find("." + this._dayOverClass + " a");
                0 < d.length && l.apply(d.get(0));
                b.dpDiv.removeClass("ui-datepicker-multi-2 ui-datepicker-multi-3 ui-datepicker-multi-4").width("");
                1 < e && b.dpDiv.addClass("ui-datepicker-multi-" + e).css("width", 17 * e + "em");
                b.dpDiv[(1 !== c[0] || 1 !== c[1] ? "add" : "remove") + "Class"]("ui-datepicker-multi");
                b.dpDiv[(this._get(b, "isRTL") ? "add" : "remove") + "Class"]("ui-datepicker-rtl");
                b === a.datepicker._curInst && a.datepicker._datepickerShowing && a.datepicker._shouldFocusInput(b) && b.input.focus();
                if (b.yearshtml) {
                    var f = b.yearshtml;
                    setTimeout(function() {
                        f === b.yearshtml && b.yearshtml && b.dpDiv.find("select.ui-datepicker-year:first").replaceWith(b.yearshtml);
                        f = b.yearshtml = null
                    }, 0)
                }
            },
            _shouldFocusInput: function(b) {
                return b.input && b.input.is(":visible") && !b.input.is(":disabled") && !b.input.is(":focus")
            },
            _checkOffset: function(b,
                c, e) {
                var d = b.dpDiv.outerWidth(),
                    k = b.dpDiv.outerHeight(),
                    f = b.input ? b.input.outerWidth() : 0,
                    h = b.input ? b.input.outerHeight() : 0,
                    n = document.documentElement.clientWidth + (e ? 0 : a(document).scrollLeft()),
                    l = document.documentElement.clientHeight + (e ? 0 : a(document).scrollTop());
                c.left -= this._get(b, "isRTL") ? d - f : 0;
                c.left -= e && c.left === b.input.offset().left ? a(document).scrollLeft() : 0;
                c.top -= e && c.top === b.input.offset().top + h ? a(document).scrollTop() : 0;
                c.left -= Math.min(c.left, c.left + d > n && n > d ? Math.abs(c.left + d - n) : 0);
                c.top -=
                    Math.min(c.top, c.top + k > l && l > k ? Math.abs(k + h) : 0);
                return c
            },
            _findPos: function(b) {
                var c = this._getInst(b);
                for (c = this._get(c, "isRTL"); b && ("hidden" === b.type || 1 !== b.nodeType || a.expr.filters.hidden(b));) b = b[c ? "previousSibling" : "nextSibling"];
                b = a(b).offset();
                return [b.left, b.top]
            },
            _hideDatepicker: function(b) {
                var c = this._curInst;
                if (c && (!b || c === a.data(b, "datepicker")) && this._datepickerShowing) {
                    b = this._get(c, "showAnim");
                    var e = this._get(c, "duration");
                    var d = function() {
                        a.datepicker._tidyDialog(c)
                    };
                    if (a.effects && (a.effects.effect[b] ||
                            a.effects[b])) c.dpDiv.hide(b, a.datepicker._get(c, "showOptions"), e, d);
                    else c.dpDiv["slideDown" === b ? "slideUp" : "fadeIn" === b ? "fadeOut" : "hide"](b ? e : null, d);
                    b || d();
                    this._datepickerShowing = !1;
                    (b = this._get(c, "onClose")) && b.apply(c.input ? c.input[0] : null, [c.input ? c.input.val() : "", c]);
                    this._lastInput = null;
                    this._inDialog && (this._dialogInput.css({
                        position: "absolute",
                        left: "0",
                        top: "-100px"
                    }), a.blockUI && (a.unblockUI(), a("body").append(this.dpDiv)));
                    this._inDialog = !1
                }
            },
            _tidyDialog: function(b) {
                b.dpDiv.removeClass(this._dialogClass).unbind(".ui-datepicker-calendar")
            },
            _checkExternalClick: function(b) {
                if (a.datepicker._curInst) {
                    b = a(b.target);
                    var c = a.datepicker._getInst(b[0]);
                    (!(b[0].id === a.datepicker._mainDivId || 0 !== b.parents("#" + a.datepicker._mainDivId).length || b.hasClass(a.datepicker.markerClassName) || b.closest("." + a.datepicker._triggerClass).length || !a.datepicker._datepickerShowing || a.datepicker._inDialog && a.blockUI) || b.hasClass(a.datepicker.markerClassName) && a.datepicker._curInst !== c) && a.datepicker._hideDatepicker()
                }
            },
            _adjustDate: function(b, c, e) {
                b = a(b);
                var d =
                    this._getInst(b[0]);
                this._isDisabledDatepicker(b[0]) || (this._adjustInstDate(d, c + ("M" === e ? this._get(d, "showCurrentAtPos") : 0), e), this._updateDatepicker(d))
            },
            _gotoToday: function(b) {
                var c = a(b),
                    e = this._getInst(c[0]);
                this._get(e, "gotoCurrent") && e.currentDay ? (e.selectedDay = e.currentDay, e.drawMonth = e.selectedMonth = e.currentMonth, e.drawYear = e.selectedYear = e.currentYear) : (b = new Date, e.selectedDay = b.getDate(), e.drawMonth = e.selectedMonth = b.getMonth(), e.drawYear = e.selectedYear = b.getFullYear());
                this._notifyChange(e);
                this._adjustDate(c)
            },
            _selectMonthYear: function(b, c, e) {
                b = a(b);
                var d = this._getInst(b[0]);
                d["selected" + ("M" === e ? "Month" : "Year")] = d["draw" + ("M" === e ? "Month" : "Year")] = parseInt(c.options[c.selectedIndex].value, 10);
                this._notifyChange(d);
                this._adjustDate(b)
            },
            _selectDay: function(b, c, e, d) {
                var k = a(b);
                a(d).hasClass(this._unselectableClass) || this._isDisabledDatepicker(k[0]) || (k = this._getInst(k[0]), k.selectedDay = k.currentDay = a("a", d).html(), k.selectedMonth = k.currentMonth = c, k.selectedYear = k.currentYear = e, this._selectDate(b,
                    this._formatDate(k, k.currentDay, k.currentMonth, k.currentYear)))
            },
            _clearDate: function(b) {
                b = a(b);
                this._selectDate(b, "")
            },
            _selectDate: function(b, c) {
                b = a(b);
                var e = this._getInst(b[0]);
                c = null != c ? c : this._formatDate(e);
                e.input && e.input.val(c);
                this._updateAlternate(e);
                (b = this._get(e, "onSelect")) ? b.apply(e.input ? e.input[0] : null, [c, e]): e.input && e.input.trigger("change");
                e.inline ? this._updateDatepicker(e) : (this._hideDatepicker(), this._lastInput = e.input[0], "object" !== typeof e.input[0] && e.input.focus(), this._lastInput =
                    null)
            },
            _updateAlternate: function(b) {
                var c = this._get(b, "altField");
                if (c) {
                    var e = this._get(b, "altFormat") || this._get(b, "dateFormat");
                    var d = this._getDate(b);
                    var f = this.formatDate(e, d, this._getFormatConfig(b));
                    a(c).each(function() {
                        a(this).val(f)
                    })
                }
            },
            noWeekends: function(b) {
                b = b.getDay();
                return [0 < b && 6 > b, ""]
            },
            iso8601Week: function(b) {
                var c = new Date(b.getTime());
                c.setDate(c.getDate() + 4 - (c.getDay() || 7));
                b = c.getTime();
                c.setMonth(0);
                c.setDate(1);
                return Math.floor(Math.round((b - c) / 864E5) / 7) + 1
            },
            parseDate: function(b,
                c, e) {
                if (null == b || null == c) throw "Invalid arguments";
                c = "object" === typeof c ? c.toString() : c + "";
                if ("" === c) return null;
                var d, k = 0;
                var f = (e ? e.shortYearCutoff : null) || this._defaults.shortYearCutoff;
                f = "string" !== typeof f ? f : (new Date).getFullYear() % 100 + parseInt(f, 10);
                var h = (e ? e.dayNamesShort : null) || this._defaults.dayNamesShort;
                var n = (e ? e.dayNames : null) || this._defaults.dayNames,
                    l = (e ? e.monthNamesShort : null) || this._defaults.monthNamesShort,
                    g = (e ? e.monthNames : null) || this._defaults.monthNames,
                    m = e = -1,
                    q = -1,
                    r = -1,
                    v = !1,
                    y = function(c) {
                        (c = d + 1 < b.length && b.charAt(d + 1) === c) && d++;
                        return c
                    },
                    p = function(b) {
                        var e = y(b);
                        e = "@" === b ? 14 : "!" === b ? 20 : "y" === b && e ? 4 : "o" === b ? 3 : 2;
                        b = new RegExp("^\\d{" + ("y" === b ? e : 1) + "," + e + "}");
                        b = c.substring(k).match(b);
                        if (!b) throw "Missing number at position " + k;
                        k += b[0].length;
                        return parseInt(b[0], 10)
                    },
                    t = function(b, e, d) {
                        var f = -1;
                        b = a.map(y(b) ? d : e, function(b, c) {
                            return [
                                [c, b]
                            ]
                        }).sort(function(b, c) {
                            return -(b[1].length - c[1].length)
                        });
                        a.each(b, function(b, e) {
                            b = e[1];
                            if (c.substr(k, b.length).toLowerCase() === b.toLowerCase()) return f =
                                e[0], k += b.length, !1
                        });
                        if (-1 !== f) return f + 1;
                        throw "Unknown name at position " + k;
                    },
                    x = function() {
                        if (c.charAt(k) !== b.charAt(d)) throw "Unexpected literal at position " + k;
                        k++
                    };
                for (d = 0; d < b.length; d++)
                    if (v) "'" !== b.charAt(d) || y("'") ? x() : v = !1;
                    else switch (b.charAt(d)) {
                        case "d":
                            q = p("d");
                            break;
                        case "D":
                            t("D", h, n);
                            break;
                        case "o":
                            r = p("o");
                            break;
                        case "m":
                            m = p("m");
                            break;
                        case "M":
                            m = t("M", l, g);
                            break;
                        case "y":
                            e = p("y");
                            break;
                        case "@":
                            var w = new Date(p("@"));
                            e = w.getFullYear();
                            m = w.getMonth() + 1;
                            q = w.getDate();
                            break;
                        case "!":
                            w =
                                new Date((p("!") - this._ticksTo1970) / 1E4);
                            e = w.getFullYear();
                            m = w.getMonth() + 1;
                            q = w.getDate();
                            break;
                        case "'":
                            y("'") ? x() : v = !0;
                            break;
                        default:
                            x()
                    }
                if (k < c.length && (h = c.substr(k), !/^\s+/.test(h))) throw "Extra/unparsed characters found in date: " + h; - 1 === e ? e = (new Date).getFullYear() : 100 > e && (e += (new Date).getFullYear() - (new Date).getFullYear() % 100 + (e <= f ? 0 : -100));
                if (-1 < r) {
                    m = 1;
                    q = r;
                    do {
                        f = this._getDaysInMonth(e, m - 1);
                        if (q <= f) break;
                        m++;
                        q -= f
                    } while (1)
                }
                w = this._daylightSavingAdjust(new Date(e, m - 1, q));
                if (w.getFullYear() !==
                    e || w.getMonth() + 1 !== m || w.getDate() !== q) throw "Invalid date";
                return w
            },
            ATOM: "yy-mm-dd",
            COOKIE: "D, dd M yy",
            ISO_8601: "yy-mm-dd",
            RFC_822: "D, d M y",
            RFC_850: "DD, dd-M-y",
            RFC_1036: "D, d M y",
            RFC_1123: "D, d M yy",
            RFC_2822: "D, d M yy",
            RSS: "D, d M y",
            TICKS: "!",
            TIMESTAMP: "@",
            W3C: "yy-mm-dd",
            _ticksTo1970: 62135596800 * 1E7,
            formatDate: function(b, c, e) {
                if (!c) return "";
                var a, d = (e ? e.dayNamesShort : null) || this._defaults.dayNamesShort,
                    k = (e ? e.dayNames : null) || this._defaults.dayNames,
                    f = (e ? e.monthNamesShort : null) || this._defaults.monthNamesShort;
                e = (e ? e.monthNames : null) || this._defaults.monthNames;
                var h = function(c) {
                        (c = a + 1 < b.length && b.charAt(a + 1) === c) && a++;
                        return c
                    },
                    n = function(b, c, e) {
                        c = "" + c;
                        if (h(b))
                            for (; c.length < e;) c = "0" + c;
                        return c
                    },
                    l = function(b, c, e, a) {
                        return h(b) ? a[c] : e[c]
                    },
                    g = "",
                    m = !1;
                if (c)
                    for (a = 0; a < b.length; a++)
                        if (m) "'" !== b.charAt(a) || h("'") ? g += b.charAt(a) : m = !1;
                        else switch (b.charAt(a)) {
                            case "d":
                                g += n("d", c.getDate(), 2);
                                break;
                            case "D":
                                g += l("D", c.getDay(), d, k);
                                break;
                            case "o":
                                g += n("o", Math.round(((new Date(c.getFullYear(), c.getMonth(), c.getDate())).getTime() -
                                    (new Date(c.getFullYear(), 0, 0)).getTime()) / 864E5), 3);
                                break;
                            case "m":
                                g += n("m", c.getMonth() + 1, 2);
                                break;
                            case "M":
                                g += l("M", c.getMonth(), f, e);
                                break;
                            case "y":
                                g += h("y") ? c.getFullYear() : (10 > c.getYear() % 100 ? "0" : "") + c.getYear() % 100;
                                break;
                            case "@":
                                g += c.getTime();
                                break;
                            case "!":
                                g += 1E4 * c.getTime() + this._ticksTo1970;
                                break;
                            case "'":
                                h("'") ? g += "'" : m = !0;
                                break;
                            default:
                                g += b.charAt(a)
                        }
                return g
            },
            _possibleChars: function(b) {
                var c, e = "",
                    a = !1,
                    d = function(e) {
                        (e = c + 1 < b.length && b.charAt(c + 1) === e) && c++;
                        return e
                    };
                for (c = 0; c < b.length; c++)
                    if (a) "'" !==
                        b.charAt(c) || d("'") ? e += b.charAt(c) : a = !1;
                    else switch (b.charAt(c)) {
                        case "d":
                        case "m":
                        case "y":
                        case "@":
                            e += "0123456789";
                            break;
                        case "D":
                        case "M":
                            return null;
                        case "'":
                            d("'") ? e += "'" : a = !0;
                            break;
                        default:
                            e += b.charAt(c)
                    }
                return e
            },
            _get: function(b, c) {
                return void 0 !== b.settings[c] ? b.settings[c] : this._defaults[c]
            },
            _setDateFromField: function(b, c) {
                if (b.input.val() !== b.lastVal) {
                    var e = this._get(b, "dateFormat"),
                        a = b.lastVal = b.input ? b.input.val() : null,
                        d = this._getDefaultDate(b),
                        f = d,
                        h = this._getFormatConfig(b);
                    try {
                        f = this.parseDate(e,
                            a, h) || d
                    } catch (z) {
                        a = c ? "" : a
                    }
                    b.selectedDay = f.getDate();
                    b.drawMonth = b.selectedMonth = f.getMonth();
                    b.drawYear = b.selectedYear = f.getFullYear();
                    b.currentDay = a ? f.getDate() : 0;
                    b.currentMonth = a ? f.getMonth() : 0;
                    b.currentYear = a ? f.getFullYear() : 0;
                    this._adjustInstDate(b)
                }
            },
            _getDefaultDate: function(b) {
                return this._restrictMinMax(b, this._determineDate(b, this._get(b, "defaultDate"), new Date))
            },
            _determineDate: function(b, c, e) {
                var d = function(b) {
                        var c = new Date;
                        c.setDate(c.getDate() + b);
                        return c
                    },
                    k = function(c) {
                        try {
                            return a.datepicker.parseDate(a.datepicker._get(b,
                                "dateFormat"), c, a.datepicker._getFormatConfig(b))
                        } catch (Y) {}
                        var e = (c.toLowerCase().match(/^c/) ? a.datepicker._getDate(b) : null) || new Date,
                            d = e.getFullYear(),
                            k = e.getMonth();
                        e = e.getDate();
                        for (var f = /([+\-]?[0-9]+)\s*(d|D|w|W|m|M|y|Y)?/g, h = f.exec(c); h;) {
                            switch (h[2] || "d") {
                                case "d":
                                case "D":
                                    e += parseInt(h[1], 10);
                                    break;
                                case "w":
                                case "W":
                                    e += 7 * parseInt(h[1], 10);
                                    break;
                                case "m":
                                case "M":
                                    k += parseInt(h[1], 10);
                                    e = Math.min(e, a.datepicker._getDaysInMonth(d, k));
                                    break;
                                case "y":
                                case "Y":
                                    d += parseInt(h[1], 10), e = Math.min(e,
                                        a.datepicker._getDaysInMonth(d, k))
                            }
                            h = f.exec(c)
                        }
                        return new Date(d, k, e)
                    };
                if (c = (c = null == c || "" === c ? e : "string" === typeof c ? k(c) : "number" === typeof c ? isNaN(c) ? e : d(c) : new Date(c.getTime())) && "Invalid Date" === c.toString() ? e : c) c.setHours(0), c.setMinutes(0), c.setSeconds(0), c.setMilliseconds(0);
                return this._daylightSavingAdjust(c)
            },
            _daylightSavingAdjust: function(b) {
                if (!b) return null;
                b.setHours(12 < b.getHours() ? b.getHours() + 2 : 0);
                return b
            },
            _setDate: function(b, c, e) {
                var a = !c,
                    d = b.selectedMonth,
                    k = b.selectedYear;
                c = this._restrictMinMax(b,
                    this._determineDate(b, c, new Date));
                b.selectedDay = b.currentDay = c.getDate();
                b.drawMonth = b.selectedMonth = b.currentMonth = c.getMonth();
                b.drawYear = b.selectedYear = b.currentYear = c.getFullYear();
                d === b.selectedMonth && k === b.selectedYear || e || this._notifyChange(b);
                this._adjustInstDate(b);
                b.input && b.input.val(a ? "" : this._formatDate(b))
            },
            _getDate: function(b) {
                return !b.currentYear || b.input && "" === b.input.val() ? null : this._daylightSavingAdjust(new Date(b.currentYear, b.currentMonth, b.currentDay))
            },
            _attachHandlers: function(b) {
                var c =
                    this._get(b, "stepMonths"),
                    e = "#" + b.id.replace(/\\\\/g, "\\");
                b.dpDiv.find("[data-handler]").map(function() {
                    a(this).bind(this.getAttribute("data-event"), {
                        prev: function() {
                            a.datepicker._adjustDate(e, -c, "M")
                        },
                        next: function() {
                            a.datepicker._adjustDate(e, +c, "M")
                        },
                        hide: function() {
                            a.datepicker._hideDatepicker()
                        },
                        today: function() {
                            a.datepicker._gotoToday(e)
                        },
                        selectDay: function() {
                            a.datepicker._selectDay(e, +this.getAttribute("data-month"), +this.getAttribute("data-year"), this);
                            return !1
                        },
                        selectMonth: function() {
                            a.datepicker._selectMonthYear(e,
                                this, "M");
                            return !1
                        },
                        selectYear: function() {
                            a.datepicker._selectMonthYear(e, this, "Y");
                            return !1
                        }
                    } [this.getAttribute("data-handler")])
                })
            },
            _generateHTML: function(b) {
                var c, e, a, d, f = new Date;
                f = this._daylightSavingAdjust(new Date(f.getFullYear(), f.getMonth(), f.getDate()));
                var h = this._get(b, "isRTL");
                var n = this._get(b, "showButtonPanel");
                var l = this._get(b, "hideIfNoPrevNext");
                var g = this._get(b, "navigationAsDateFormat");
                var m = this._getNumberOfMonths(b),
                    q = this._get(b, "showCurrentAtPos");
                var r = this._get(b, "stepMonths");
                var v = 1 !== m[0] || 1 !== m[1],
                    y = this._daylightSavingAdjust(b.currentDay ? new Date(b.currentYear, b.currentMonth, b.currentDay) : new Date(9999, 9, 9)),
                    p = this._getMinMaxDate(b, "min"),
                    t = this._getMinMaxDate(b, "max");
                q = b.drawMonth - q;
                var x = b.drawYear;
                0 > q && (q += 12, x--);
                if (t) {
                    var w = this._daylightSavingAdjust(new Date(t.getFullYear(), t.getMonth() - m[0] * m[1] + 1, t.getDate()));
                    for (w = p && w < p ? p : w; this._daylightSavingAdjust(new Date(x, q, 1)) > w;) q--, 0 > q && (q = 11, x--)
                }
                b.drawMonth = q;
                b.drawYear = x;
                w = this._get(b, "prevText");
                w = g ? this.formatDate(w,
                    this._daylightSavingAdjust(new Date(x, q - r, 1)), this._getFormatConfig(b)) : w;
                w = this._canAdjustMonth(b, -1, x, q) ? "\x3ca class\x3d'ui-datepicker-prev ui-corner-all' data-handler\x3d'prev' data-event\x3d'click' title\x3d'" + w + "'\x3e\x3cspan class\x3d'ui-icon ui-icon-circle-triangle-" + (h ? "e" : "w") + "'\x3e" + w + "\x3c/span\x3e\x3c/a\x3e" : l ? "" : "\x3ca class\x3d'ui-datepicker-prev ui-corner-all ui-state-disabled' title\x3d'" + w + "'\x3e\x3cspan class\x3d'ui-icon ui-icon-circle-triangle-" + (h ? "e" : "w") + "'\x3e" + w + "\x3c/span\x3e\x3c/a\x3e";
                var C = this._get(b, "nextText");
                C = g ? this.formatDate(C, this._daylightSavingAdjust(new Date(x, q + r, 1)), this._getFormatConfig(b)) : C;
                l = this._canAdjustMonth(b, 1, x, q) ? "\x3ca class\x3d'ui-datepicker-next ui-corner-all' data-handler\x3d'next' data-event\x3d'click' title\x3d'" + C + "'\x3e\x3cspan class\x3d'ui-icon ui-icon-circle-triangle-" + (h ? "w" : "e") + "'\x3e" + C + "\x3c/span\x3e\x3c/a\x3e" : l ? "" : "\x3ca class\x3d'ui-datepicker-next ui-corner-all ui-state-disabled' title\x3d'" + C + "'\x3e\x3cspan class\x3d'ui-icon ui-icon-circle-triangle-" +
                    (h ? "w" : "e") + "'\x3e" + C + "\x3c/span\x3e\x3c/a\x3e";
                r = this._get(b, "currentText");
                C = this._get(b, "gotoCurrent") && b.currentDay ? y : f;
                r = g ? this.formatDate(r, C, this._getFormatConfig(b)) : r;
                g = b.inline ? "" : "\x3cbutton type\x3d'button' class\x3d'ui-datepicker-close ui-state-default ui-priority-primary ui-corner-all' data-handler\x3d'hide' data-event\x3d'click'\x3e" + this._get(b, "closeText") + "\x3c/button\x3e";
                n = n ? "\x3cdiv class\x3d'ui-datepicker-buttonpane ui-widget-content'\x3e" + (h ? g : "") + (this._isInRange(b, C) ? "\x3cbutton type\x3d'button' class\x3d'ui-datepicker-current ui-state-default ui-priority-secondary ui-corner-all' data-handler\x3d'today' data-event\x3d'click'\x3e" +
                    r + "\x3c/button\x3e" : "") + (h ? "" : g) + "\x3c/div\x3e" : "";
                g = parseInt(this._get(b, "firstDay"), 10);
                g = isNaN(g) ? 0 : g;
                r = this._get(b, "showWeek");
                C = this._get(b, "dayNames");
                var U = this._get(b, "dayNamesMin");
                var V = this._get(b, "monthNames");
                var W = this._get(b, "monthNamesShort");
                var M = this._get(b, "beforeShowDay");
                var K = this._get(b, "showOtherMonths");
                var X = this._get(b, "selectOtherMonths");
                var N = this._getDefaultDate(b);
                var O = "";
                B;
                for (c = 0; c < m[0]; c++) {
                    var P = "";
                    this.maxRows = 4;
                    for (e = 0; e < m[1]; e++) {
                        var Q = this._daylightSavingAdjust(new Date(x,
                            q, b.selectedDay));
                        var B = " ui-corner-all";
                        var D = "";
                        if (v) {
                            D += "\x3cdiv class\x3d'ui-datepicker-group";
                            if (1 < m[1]) switch (e) {
                                case 0:
                                    D += " ui-datepicker-group-first";
                                    B = " ui-corner-" + (h ? "right" : "left");
                                    break;
                                case m[1] - 1:
                                    D += " ui-datepicker-group-last";
                                    B = " ui-corner-" + (h ? "left" : "right");
                                    break;
                                default:
                                    D += " ui-datepicker-group-middle", B = ""
                            }
                            D += "'\x3e"
                        }
                        D += "\x3cdiv class\x3d'ui-datepicker-header ui-widget-header ui-helper-clearfix" + B + "'\x3e" + (/all|left/.test(B) && 0 === c ? h ? l : w : "") + (/all|right/.test(B) && 0 === c ? h ? w : l :
                            "") + this._generateMonthYearHeader(b, q, x, p, t, 0 < c || 0 < e, V, W) + "\x3c/div\x3e\x3ctable class\x3d'ui-datepicker-calendar'\x3e\x3cthead\x3e\x3ctr\x3e";
                        var E = r ? "\x3cth class\x3d'ui-datepicker-week-col'\x3e" + this._get(b, "weekHeader") + "\x3c/th\x3e" : "";
                        for (B = 0; 7 > B; B++) {
                            var A = (B + g) % 7;
                            E += "\x3cth scope\x3d'col'" + (5 <= (B + g + 6) % 7 ? " class\x3d'ui-datepicker-week-end'" : "") + "\x3e\x3cspan title\x3d'" + C[A] + "'\x3e" + U[A] + "\x3c/span\x3e\x3c/th\x3e"
                        }
                        D += E + "\x3c/tr\x3e\x3c/thead\x3e\x3ctbody\x3e";
                        E = this._getDaysInMonth(x, q);
                        x ===
                            b.selectedYear && q === b.selectedMonth && (b.selectedDay = Math.min(b.selectedDay, E));
                        B = (this._getFirstDayOfMonth(x, q) - g + 7) % 7;
                        E = Math.ceil((B + E) / 7);
                        this.maxRows = E = v ? this.maxRows > E ? this.maxRows : E : E;
                        A = this._daylightSavingAdjust(new Date(x, q, 1 - B));
                        for (a = 0; a < E; a++) {
                            D += "\x3ctr\x3e";
                            var R = r ? "\x3ctd class\x3d'ui-datepicker-week-col'\x3e" + this._get(b, "calculateWeek")(A) + "\x3c/td\x3e" : "";
                            for (B = 0; 7 > B; B++) {
                                var J = M ? M.apply(b.input ? b.input[0] : null, [A]) : [!0, ""];
                                var L = (d = A.getMonth() !== q) && !X || !J[0] || p && A < p || t && A > t;
                                R +=
                                    "\x3ctd class\x3d'" + (5 <= (B + g + 6) % 7 ? " ui-datepicker-week-end" : "") + (d ? " ui-datepicker-other-month" : "") + (A.getTime() === Q.getTime() && q === b.selectedMonth && b._keyEvent || N.getTime() === A.getTime() && N.getTime() === Q.getTime() ? " " + this._dayOverClass : "") + (L ? " " + this._unselectableClass + " ui-state-disabled" : "") + (d && !K ? "" : " " + J[1] + (A.getTime() === y.getTime() ? " " + this._currentClass : "") + (A.getTime() === f.getTime() ? " ui-datepicker-today" : "")) + "'" + (d && !K || !J[2] ? "" : " title\x3d'" + J[2].replace(/'/g, "\x26#39;") + "'") + (L ? "" :
                                        " data-handler\x3d'selectDay' data-event\x3d'click' data-month\x3d'" + A.getMonth() + "' data-year\x3d'" + A.getFullYear() + "'") + "\x3e" + (d && !K ? "\x26#xa0;" : L ? "\x3cspan class\x3d'ui-state-default'\x3e" + A.getDate() + "\x3c/span\x3e" : "\x3ca class\x3d'ui-state-default" + (A.getTime() === f.getTime() ? " ui-state-highlight" : "") + (A.getTime() === y.getTime() ? " ui-state-active" : "") + (d ? " ui-priority-secondary" : "") + "' href\x3d'#'\x3e" + A.getDate() + "\x3c/a\x3e") + "\x3c/td\x3e";
                                A.setDate(A.getDate() + 1);
                                A = this._daylightSavingAdjust(A)
                            }
                            D +=
                                R + "\x3c/tr\x3e"
                        }
                        q++;
                        11 < q && (q = 0, x++);
                        D += "\x3c/tbody\x3e\x3c/table\x3e" + (v ? "\x3c/div\x3e" + (0 < m[0] && e === m[1] - 1 ? "\x3cdiv class\x3d'ui-datepicker-row-break'\x3e\x3c/div\x3e" : "") : "");
                        P += D
                    }
                    O += P
                }
                b._keyEvent = !1;
                return O + n
            },
            _generateMonthYearHeader: function(b, c, e, a, d, f, h, n) {
                var k, l = this._get(b, "changeMonth"),
                    g = this._get(b, "changeYear"),
                    m = this._get(b, "showMonthAfterYear"),
                    q = "\x3cdiv class\x3d'ui-datepicker-title'\x3e",
                    r = "";
                if (f || !l) r += "\x3cspan class\x3d'ui-datepicker-month'\x3e" + h[c] + "\x3c/span\x3e";
                else {
                    h =
                        a && a.getFullYear() === e;
                    var v = d && d.getFullYear() === e;
                    r += "\x3cselect class\x3d'ui-datepicker-month' data-handler\x3d'selectMonth' data-event\x3d'change'\x3e";
                    for (k = 0; 12 > k; k++)(!h || k >= a.getMonth()) && (!v || k <= d.getMonth()) && (r += "\x3coption value\x3d'" + k + "'" + (k === c ? " selected\x3d'selected'" : "") + "\x3e" + n[k] + "\x3c/option\x3e");
                    r += "\x3c/select\x3e"
                }
                m || (q += r + (!f && l && g ? "" : "\x26#xa0;"));
                if (!b.yearshtml)
                    if (b.yearshtml = "", f || !g) q += "\x3cspan class\x3d'ui-datepicker-year'\x3e" + e + "\x3c/span\x3e";
                    else {
                        n = this._get(b,
                            "yearRange").split(":");
                        var y = (new Date).getFullYear();
                        h = function(b) {
                            b = b.match(/c[+\-].*/) ? e + parseInt(b.substring(1), 10) : b.match(/[+\-].*/) ? y + parseInt(b, 10) : parseInt(b, 10);
                            return isNaN(b) ? y : b
                        };
                        c = h(n[0]);
                        n = Math.max(c, h(n[1] || ""));
                        c = a ? Math.max(c, a.getFullYear()) : c;
                        n = d ? Math.min(n, d.getFullYear()) : n;
                        for (b.yearshtml += "\x3cselect class\x3d'ui-datepicker-year' data-handler\x3d'selectYear' data-event\x3d'change'\x3e"; c <= n; c++) b.yearshtml += "\x3coption value\x3d'" + c + "'" + (c === e ? " selected\x3d'selected'" : "") +
                            "\x3e" + c + "\x3c/option\x3e";
                        b.yearshtml += "\x3c/select\x3e";
                        q += b.yearshtml;
                        b.yearshtml = null
                    } q += this._get(b, "yearSuffix");
                m && (q += (!f && l && g ? "" : "\x26#xa0;") + r);
                return q + "\x3c/div\x3e"
            },
            _adjustInstDate: function(b, c, e) {
                var a = b.drawYear + ("Y" === e ? c : 0),
                    d = b.drawMonth + ("M" === e ? c : 0);
                c = Math.min(b.selectedDay, this._getDaysInMonth(a, d)) + ("D" === e ? c : 0);
                a = this._restrictMinMax(b, this._daylightSavingAdjust(new Date(a, d, c)));
                b.selectedDay = a.getDate();
                b.drawMonth = b.selectedMonth = a.getMonth();
                b.drawYear = b.selectedYear = a.getFullYear();
                "M" !== e && "Y" !== e || this._notifyChange(b)
            },
            _restrictMinMax: function(b, c) {
                var e = this._getMinMaxDate(b, "min");
                b = this._getMinMaxDate(b, "max");
                c = e && c < e ? e : c;
                return b && c > b ? b : c
            },
            _notifyChange: function(b) {
                var c = this._get(b, "onChangeMonthYear");
                c && c.apply(b.input ? b.input[0] : null, [b.selectedYear, b.selectedMonth + 1, b])
            },
            _getNumberOfMonths: function(b) {
                b = this._get(b, "numberOfMonths");
                return null == b ? [1, 1] : "number" === typeof b ? [1, b] : b
            },
            _getMinMaxDate: function(b, c) {
                return this._determineDate(b, this._get(b, c + "Date"),
                    null)
            },
            _getDaysInMonth: function(b, c) {
                return 32 - this._daylightSavingAdjust(new Date(b, c, 32)).getDate()
            },
            _getFirstDayOfMonth: function(b, c) {
                return (new Date(b, c, 1)).getDay()
            },
            _canAdjustMonth: function(b, c, e, a) {
                var d = this._getNumberOfMonths(b);
                e = this._daylightSavingAdjust(new Date(e, a + (0 > c ? c : d[0] * d[1]), 1));
                0 > c && e.setDate(this._getDaysInMonth(e.getFullYear(), e.getMonth()));
                return this._isInRange(b, e)
            },
            _isInRange: function(b, c) {
                var e = this._getMinMaxDate(b, "min"),
                    a = this._getMinMaxDate(b, "max"),
                    d = null,
                    f = null;
                if (b = this._get(b, "yearRange")) {
                    b = b.split(":");
                    var h = (new Date).getFullYear();
                    d = parseInt(b[0], 10);
                    f = parseInt(b[1], 10);
                    b[0].match(/[+\-].*/) && (d += h);
                    b[1].match(/[+\-].*/) && (f += h)
                }
                return (!e || c.getTime() >= e.getTime()) && (!a || c.getTime() <= a.getTime()) && (!d || c.getFullYear() >= d) && (!f || c.getFullYear() <= f)
            },
            _getFormatConfig: function(b) {
                var c = this._get(b, "shortYearCutoff");
                c = "string" !== typeof c ? c : (new Date).getFullYear() % 100 + parseInt(c, 10);
                return {
                    shortYearCutoff: c,
                    dayNamesShort: this._get(b, "dayNamesShort"),
                    dayNames: this._get(b, "dayNames"),
                    monthNamesShort: this._get(b, "monthNamesShort"),
                    monthNames: this._get(b, "monthNames")
                }
            },
            _formatDate: function(b, c, e, a) {
                c || (b.currentDay = b.selectedDay, b.currentMonth = b.selectedMonth, b.currentYear = b.selectedYear);
                c = c ? "object" === typeof c ? c : this._daylightSavingAdjust(new Date(a, e, c)) : this._daylightSavingAdjust(new Date(b.currentYear, b.currentMonth, b.currentDay));
                return this.formatDate(this._get(b, "dateFormat"), c, this._getFormatConfig(b))
            }
        });
        a.fn.datepicker = function(b) {
            if (!this.length) return this;
            a.datepicker.initialized || (a(document).mousedown(a.datepicker._checkExternalClick), a.datepicker.initialized = !0);
            0 === a("#" + a.datepicker._mainDivId).length && a("body").append(a.datepicker.dpDiv);
            var c = Array.prototype.slice.call(arguments, 1);
            return "string" === typeof b && ("isDisabled" === b || "getDate" === b || "widget" === b) || "option" === b && 2 === arguments.length && "string" === typeof arguments[1] ? a.datepicker["_" + b + "Datepicker"].apply(a.datepicker, [this[0]].concat(c)) : this.each(function() {
                "string" === typeof b ? a.datepicker["_" +
                    b + "Datepicker"].apply(a.datepicker, [this].concat(c)) : a.datepicker._attachDatepicker(this, b)
            })
        };
        a.datepicker = new h;
        a.datepicker.initialized = !1;
        a.datepicker.uuid = (new Date).getTime();
        a.datepicker.version = "1.11.4";
        a.widget("ui.dialog", {
            version: "1.11.4",
            options: {
                appendTo: "body",
                autoOpen: !0,
                buttons: [],
                closeOnEscape: !0,
                closeText: "Close",
                dialogClass: "",
                draggable: !0,
                hide: null,
                height: "auto",
                maxHeight: null,
                maxWidth: null,
                minHeight: 150,
                minWidth: 150,
                modal: !1,
                position: {
                    my: "center",
                    at: "center",
                    of: window,
                    collision: "fit",
                    using: function(b) {
                        var c = a(this).css(b).offset().top;
                        0 > c && a(this).css("top", b.top - c)
                    }
                },
                resizable: !0,
                show: null,
                title: null,
                width: 300,
                beforeClose: null,
                close: null,
                drag: null,
                dragStart: null,
                dragStop: null,
                focus: null,
                open: null,
                resize: null,
                resizeStart: null,
                resizeStop: null
            },
            sizeRelatedOptions: {
                buttons: !0,
                height: !0,
                maxHeight: !0,
                maxWidth: !0,
                minHeight: !0,
                minWidth: !0,
                width: !0
            },
            resizableRelatedOptions: {
                maxHeight: !0,
                maxWidth: !0,
                minHeight: !0,
                minWidth: !0
            },
            _create: function() {
                this.originalCss = {
                    display: this.element[0].style.display,
                    width: this.element[0].style.width,
                    minHeight: this.element[0].style.minHeight,
                    maxHeight: this.element[0].style.maxHeight,
                    height: this.element[0].style.height
                };
                this.originalPosition = {
                    parent: this.element.parent(),
                    index: this.element.parent().children().index(this.element)
                };
                this.originalTitle = this.element.attr("title");
                this.options.title = this.options.title || this.originalTitle;
                this._createWrapper();
                this.element.show().removeAttr("title").addClass("ui-dialog-content ui-widget-content").appendTo(this.uiDialog);
                this._createTitlebar();
                this._createButtonPane();
                this.options.draggable && a.fn.draggable && this._makeDraggable();
                this.options.resizable && a.fn.resizable && this._makeResizable();
                this._isOpen = !1;
                this._trackFocus()
            },
            _init: function() {
                this.options.autoOpen && this.open()
            },
            _appendTo: function() {
                var b = this.options.appendTo;
                return b && (b.jquery || b.nodeType) ? a(b) : this.document.find(b || "body").eq(0)
            },
            _destroy: function() {
                var b = this.originalPosition;
                this._untrackInstance();
                this._destroyOverlay();
                this.element.removeUniqueId().removeClass("ui-dialog-content ui-widget-content").css(this.originalCss).detach();
                this.uiDialog.stop(!0, !0).remove();
                this.originalTitle && this.element.attr("title", this.originalTitle);
                var c = b.parent.children().eq(b.index);
                c.length && c[0] !== this.element[0] ? c.before(this.element) : b.parent.append(this.element)
            },
            widget: function() {
                return this.uiDialog
            },
            disable: a.noop,
            enable: a.noop,
            close: function(b) {
                var c, e = this;
                if (this._isOpen && !1 !== this._trigger("beforeClose", b)) {
                    this._isOpen = !1;
                    this._focusedElement = null;
                    this._destroyOverlay();
                    this._untrackInstance();
                    if (!this.opener.filter(":focusable").focus().length) try {
                        (c =
                            this.document[0].activeElement) && "body" !== c.nodeName.toLowerCase() && a(c).blur()
                    } catch (u) {}
                    this._hide(this.uiDialog, this.options.hide, function() {
                        e._trigger("close", b)
                    })
                }
            },
            isOpen: function() {
                return this._isOpen
            },
            moveToTop: function() {
                this._moveToTop()
            },
            _moveToTop: function(b, c) {
                var e = !1,
                    d = this.uiDialog.siblings(".ui-front:visible").map(function() {
                        return +a(this).css("z-index")
                    }).get();
                d = Math.max.apply(null, d);
                d >= +this.uiDialog.css("z-index") && (this.uiDialog.css("z-index", d + 1), e = !0);
                e && !c && this._trigger("focus",
                    b);
                return e
            },
            open: function() {
                var b = this;
                this._isOpen ? this._moveToTop() && this._focusTabbable() : (this._isOpen = !0, this.opener = a(this.document[0].activeElement), this._size(), this._position(), this._createOverlay(), this._moveToTop(null, !0), this.overlay && this.overlay.css("z-index", this.uiDialog.css("z-index") - 1), this._show(this.uiDialog, this.options.show, function() {
                    b._focusTabbable();
                    b._trigger("focus")
                }), this._makeFocusTarget(), this._trigger("open"))
            },
            _focusTabbable: function() {
                var b = this._focusedElement;
                b || (b = this.element.find("[autofocus]"));
                b.length || (b = this.element.find(":tabbable"));
                b.length || (b = this.uiDialogButtonPane.find(":tabbable"));
                b.length || (b = this.uiDialogTitlebarClose.filter(":tabbable"));
                b.length || (b = this.uiDialog);
                b.eq(0).focus()
            },
            _keepFocus: function(b) {
                function c() {
                    var b = this.document[0].activeElement;
                    this.uiDialog[0] === b || a.contains(this.uiDialog[0], b) || this._focusTabbable()
                }
                b.preventDefault();
                c.call(this);
                this._delay(c)
            },
            _createWrapper: function() {
                this.uiDialog = a("\x3cdiv\x3e").addClass("ui-dialog ui-widget ui-widget-content ui-corner-all ui-front " +
                    this.options.dialogClass).hide().attr({
                    tabIndex: -1,
                    role: "dialog"
                }).appendTo(this._appendTo());
                this._on(this.uiDialog, {
                    keydown: function(b) {
                        if (this.options.closeOnEscape && !b.isDefaultPrevented() && b.keyCode && b.keyCode === a.ui.keyCode.ESCAPE) b.preventDefault(), this.close(b);
                        else if (b.keyCode === a.ui.keyCode.TAB && !b.isDefaultPrevented()) {
                            var c = this.uiDialog.find(":tabbable"),
                                e = c.filter(":first"),
                                d = c.filter(":last");
                            b.target !== d[0] && b.target !== this.uiDialog[0] || b.shiftKey ? b.target !== e[0] && b.target !== this.uiDialog[0] ||
                                !b.shiftKey || (this._delay(function() {
                                    d.focus()
                                }), b.preventDefault()) : (this._delay(function() {
                                    e.focus()
                                }), b.preventDefault())
                        }
                    },
                    mousedown: function(b) {
                        this._moveToTop(b) && this._focusTabbable()
                    }
                });
                this.element.find("[aria-describedby]").length || this.uiDialog.attr({
                    "aria-describedby": this.element.uniqueId().attr("id")
                })
            },
            _createTitlebar: function() {
                this.uiDialogTitlebar = a("\x3cdiv\x3e").addClass("ui-dialog-titlebar ui-widget-header ui-corner-all ui-helper-clearfix").prependTo(this.uiDialog);
                this._on(this.uiDialogTitlebar, {
                    mousedown: function(b) {
                        a(b.target).closest(".ui-dialog-titlebar-close") || this.uiDialog.focus()
                    }
                });
                this.uiDialogTitlebarClose = a("\x3cbutton type\x3d'button'\x3e\x3c/button\x3e").button({
                    label: this.options.closeText,
                    icons: {
                        primary: "ui-icon-closethick"
                    },
                    text: !1
                }).addClass("ui-dialog-titlebar-close").appendTo(this.uiDialogTitlebar);
                this._on(this.uiDialogTitlebarClose, {
                    click: function(b) {
                        b.preventDefault();
                        this.close(b)
                    }
                });
                var b = a("\x3cspan\x3e").uniqueId().addClass("ui-dialog-title").prependTo(this.uiDialogTitlebar);
                this._title(b);
                this.uiDialog.attr({
                    "aria-labelledby": b.attr("id")
                })
            },
            _title: function(b) {
                this.options.title || b.html("\x26#160;");
                b.text(this.options.title)
            },
            _createButtonPane: function() {
                this.uiDialogButtonPane = a("\x3cdiv\x3e").addClass("ui-dialog-buttonpane ui-widget-content ui-helper-clearfix");
                this.uiButtonSet = a("\x3cdiv\x3e").addClass("ui-dialog-buttonset").appendTo(this.uiDialogButtonPane);
                this._createButtons()
            },
            _createButtons: function() {
                var b = this,
                    c = this.options.buttons;
                this.uiDialogButtonPane.remove();
                this.uiButtonSet.empty();
                a.isEmptyObject(c) || a.isArray(c) && !c.length ? this.uiDialog.removeClass("ui-dialog-buttons") : (a.each(c, function(c, e) {
                    e = a.isFunction(e) ? {
                        click: e,
                        text: c
                    } : e;
                    e = a.extend({
                        type: "button"
                    }, e);
                    var d = e.click;
                    e.click = function() {
                        d.apply(b.element[0], arguments)
                    };
                    c = {
                        icons: e.icons,
                        text: e.showText
                    };
                    delete e.icons;
                    delete e.showText;
                    a("\x3cbutton\x3e\x3c/button\x3e", e).button(c).appendTo(b.uiButtonSet)
                }), this.uiDialog.addClass("ui-dialog-buttons"), this.uiDialogButtonPane.appendTo(this.uiDialog))
            },
            _makeDraggable: function() {
                function b(b) {
                    return {
                        position: b.position,
                        offset: b.offset
                    }
                }
                var c = this,
                    e = this.options;
                this.uiDialog.draggable({
                    cancel: ".ui-dialog-content, .ui-dialog-titlebar-close",
                    handle: ".ui-dialog-titlebar",
                    containment: "document",
                    start: function(e, d) {
                        a(this).addClass("ui-dialog-dragging");
                        c._blockFrames();
                        c._trigger("dragStart", e, b(d))
                    },
                    drag: function(e, a) {
                        c._trigger("drag", e, b(a))
                    },
                    stop: function(d, k) {
                        var f = k.offset.left - c.document.scrollLeft(),
                            h = k.offset.top - c.document.scrollTop();
                        e.position = {
                            my: "left top",
                            at: "left" + (0 <= f ? "+" : "") + f + " top" + (0 <= h ? "+" : "") + h,
                            of: c.window
                        };
                        a(this).removeClass("ui-dialog-dragging");
                        c._unblockFrames();
                        c._trigger("dragStop", d, b(k))
                    }
                })
            },
            _makeResizable: function() {
                function b(b) {
                    return {
                        originalPosition: b.originalPosition,
                        originalSize: b.originalSize,
                        position: b.position,
                        size: b.size
                    }
                }
                var c = this,
                    e = this.options,
                    d = e.resizable,
                    f = this.uiDialog.css("position");
                d = "string" === typeof d ? d : "n,e,s,w,se,sw,ne,nw";
                this.uiDialog.resizable({
                    cancel: ".ui-dialog-content",
                    containment: "document",
                    alsoResize: this.element,
                    maxWidth: e.maxWidth,
                    maxHeight: e.maxHeight,
                    minWidth: e.minWidth,
                    minHeight: this._minHeight(),
                    handles: d,
                    start: function(e, d) {
                        a(this).addClass("ui-dialog-resizing");
                        c._blockFrames();
                        c._trigger("resizeStart", e, b(d))
                    },
                    resize: function(e, a) {
                        c._trigger("resize", e, b(a))
                    },
                    stop: function(d, k) {
                        var f = c.uiDialog.offset(),
                            h = f.left - c.document.scrollLeft();
                        f = f.top - c.document.scrollTop();
                        e.height = c.uiDialog.height();
                        e.width = c.uiDialog.width();
                        e.position = {
                            my: "left top",
                            at: "left" + (0 <= h ? "+" : "") + h +
                                " top" + (0 <= f ? "+" : "") + f,
                            of: c.window
                        };
                        a(this).removeClass("ui-dialog-resizing");
                        c._unblockFrames();
                        c._trigger("resizeStop", d, b(k))
                    }
                }).css("position", f)
            },
            _trackFocus: function() {
                this._on(this.widget(), {
                    focusin: function(b) {
                        this._makeFocusTarget();
                        this._focusedElement = a(b.target)
                    }
                })
            },
            _makeFocusTarget: function() {
                this._untrackInstance();
                this._trackingInstances().unshift(this)
            },
            _untrackInstance: function() {
                var b = this._trackingInstances(),
                    c = a.inArray(this, b); - 1 !== c && b.splice(c, 1)
            },
            _trackingInstances: function() {
                var b =
                    this.document.data("ui-dialog-instances");
                b || (b = [], this.document.data("ui-dialog-instances", b));
                return b
            },
            _minHeight: function() {
                var b = this.options;
                return "auto" === b.height ? b.minHeight : Math.min(b.minHeight, b.height)
            },
            _position: function() {
                var b = this.uiDialog.is(":visible");
                b || this.uiDialog.show();
                this.uiDialog.position(this.options.position);
                b || this.uiDialog.hide()
            },
            _setOptions: function(b) {
                var c = this,
                    e = !1,
                    d = {};
                a.each(b, function(b, a) {
                    c._setOption(b, a);
                    b in c.sizeRelatedOptions && (e = !0);
                    b in c.resizableRelatedOptions &&
                        (d[b] = a)
                });
                e && (this._size(), this._position());
                this.uiDialog.is(":data(ui-resizable)") && this.uiDialog.resizable("option", d)
            },
            _setOption: function(b, c) {
                var e, a = this.uiDialog;
                "dialogClass" === b && a.removeClass(this.options.dialogClass).addClass(c);
                "disabled" !== b && (this._super(b, c), "appendTo" === b && this.uiDialog.appendTo(this._appendTo()), "buttons" === b && this._createButtons(), "closeText" === b && this.uiDialogTitlebarClose.button({
                    label: "" + c
                }), "draggable" === b && ((e = a.is(":data(ui-draggable)")) && !c && a.draggable("destroy"),
                    !e && c && this._makeDraggable()), "position" === b && this._position(), "resizable" === b && ((e = a.is(":data(ui-resizable)")) && !c && a.resizable("destroy"), e && "string" === typeof c && a.resizable("option", "handles", c), e || !1 === c || this._makeResizable()), "title" === b && this._title(this.uiDialogTitlebar.find(".ui-dialog-title")))
            },
            _size: function() {
                var b = this.options;
                this.element.show().css({
                    width: "auto",
                    minHeight: 0,
                    maxHeight: "none",
                    height: 0
                });
                b.minWidth > b.width && (b.width = b.minWidth);
                var c = this.uiDialog.css({
                    height: "auto",
                    width: b.width
                }).outerHeight();
                var e = Math.max(0, b.minHeight - c);
                var a = "number" === typeof b.maxHeight ? Math.max(0, b.maxHeight - c) : "none";
                "auto" === b.height ? this.element.css({
                    minHeight: e,
                    maxHeight: a,
                    height: "auto"
                }) : this.element.height(Math.max(0, b.height - c));
                this.uiDialog.is(":data(ui-resizable)") && this.uiDialog.resizable("option", "minHeight", this._minHeight())
            },
            _blockFrames: function() {
                this.iframeBlocks = this.document.find("iframe").map(function() {
                    var b = a(this);
                    return a("\x3cdiv\x3e").css({
                        position: "absolute",
                        width: b.outerWidth(),
                        height: b.outerHeight()
                    }).appendTo(b.parent()).offset(b.offset())[0]
                })
            },
            _unblockFrames: function() {
                this.iframeBlocks && (this.iframeBlocks.remove(), delete this.iframeBlocks)
            },
            _allowInteraction: function(b) {
                return a(b.target).closest(".ui-dialog").length ? !0 : !!a(b.target).closest(".ui-datepicker").length
            },
            _createOverlay: function() {
                if (this.options.modal) {
                    var b = !0;
                    this._delay(function() {
                        b = !1
                    });
                    this.document.data("ui-dialog-overlays") || this._on(this.document, {
                        focusin: function(c) {
                            b || this._allowInteraction(c) ||
                                (c.preventDefault(), this._trackingInstances()[0]._focusTabbable())
                        }
                    });
                    this.overlay = a("\x3cdiv\x3e").addClass("ui-widget-overlay ui-front").appendTo(this._appendTo());
                    this._on(this.overlay, {
                        mousedown: "_keepFocus"
                    });
                    this.document.data("ui-dialog-overlays", (this.document.data("ui-dialog-overlays") || 0) + 1)
                }
            },
            _destroyOverlay: function() {
                if (this.options.modal && this.overlay) {
                    var b = this.document.data("ui-dialog-overlays") - 1;
                    b ? this.document.data("ui-dialog-overlays", b) : this.document.unbind("focusin").removeData("ui-dialog-overlays");
                    this.overlay.remove();
                    this.overlay = null
                }
            }
        });
        a.widget("ui.progressbar", {
            version: "1.11.4",
            options: {
                max: 100,
                value: 0,
                change: null,
                complete: null
            },
            min: 0,
            _create: function() {
                this.oldValue = this.options.value = this._constrainedValue();
                this.element.addClass("ui-progressbar ui-widget ui-widget-content ui-corner-all").attr({
                    role: "progressbar",
                    "aria-valuemin": this.min
                });
                this.valueDiv = a("\x3cdiv class\x3d'ui-progressbar-value ui-widget-header ui-corner-left'\x3e\x3c/div\x3e").appendTo(this.element);
                this._refreshValue()
            },
            _destroy: function() {
                this.element.removeClass("ui-progressbar ui-widget ui-widget-content ui-corner-all").removeAttr("role").removeAttr("aria-valuemin").removeAttr("aria-valuemax").removeAttr("aria-valuenow");
                this.valueDiv.remove()
            },
            value: function(b) {
                if (void 0 === b) return this.options.value;
                this.options.value = this._constrainedValue(b);
                this._refreshValue()
            },
            _constrainedValue: function(b) {
                void 0 === b && (b = this.options.value);
                this.indeterminate = !1 === b;
                "number" !== typeof b && (b = 0);
                return this.indeterminate ?
                    !1 : Math.min(this.options.max, Math.max(this.min, b))
            },
            _setOptions: function(b) {
                var c = b.value;
                delete b.value;
                this._super(b);
                this.options.value = this._constrainedValue(c);
                this._refreshValue()
            },
            _setOption: function(b, c) {
                "max" === b && (c = Math.max(this.min, c));
                "disabled" === b && this.element.toggleClass("ui-state-disabled", !!c).attr("aria-disabled", c);
                this._super(b, c)
            },
            _percentage: function() {
                return this.indeterminate ? 100 : 100 * (this.options.value - this.min) / (this.options.max - this.min)
            },
            _refreshValue: function() {
                var b =
                    this.options.value,
                    c = this._percentage();
                this.valueDiv.toggle(this.indeterminate || b > this.min).toggleClass("ui-corner-right", b === this.options.max).width(c.toFixed(0) + "%");
                this.element.toggleClass("ui-progressbar-indeterminate", this.indeterminate);
                this.indeterminate ? (this.element.removeAttr("aria-valuenow"), this.overlayDiv || (this.overlayDiv = a("\x3cdiv class\x3d'ui-progressbar-overlay'\x3e\x3c/div\x3e").appendTo(this.valueDiv))) : (this.element.attr({
                        "aria-valuemax": this.options.max,
                        "aria-valuenow": b
                    }),
                    this.overlayDiv && (this.overlayDiv.remove(), this.overlayDiv = null));
                this.oldValue !== b && (this.oldValue = b, this._trigger("change"));
                b === this.options.max && this._trigger("complete")
            }
        });
        a.widget("ui.selectmenu", {
            version: "1.11.4",
            defaultElement: "\x3cselect\x3e",
            options: {
                appendTo: null,
                disabled: null,
                icons: {
                    button: "ui-icon-triangle-1-s"
                },
                position: {
                    my: "left top",
                    at: "left bottom",
                    collision: "none"
                },
                width: null,
                change: null,
                close: null,
                focus: null,
                open: null,
                select: null
            },
            _create: function() {
                var b = this.element.uniqueId().attr("id");
                this.ids = {
                    element: b,
                    button: b + "-button",
                    menu: b + "-menu"
                };
                this._drawButton();
                this._drawMenu();
                this.options.disabled && this.disable()
            },
            _drawButton: function() {
                var b = this;
                this.label = a("label[for\x3d'" + this.ids.element + "']").attr("for", this.ids.button);
                this._on(this.label, {
                    click: function(b) {
                        this.button.focus();
                        b.preventDefault()
                    }
                });
                this.element.hide();
                this.button = a("\x3cspan\x3e", {
                    "class": "ui-selectmenu-button ui-widget ui-state-default ui-corner-all",
                    tabindex: this.options.disabled ? -1 : 0,
                    id: this.ids.button,
                    role: "combobox",
                    "aria-expanded": "false",
                    "aria-autocomplete": "list",
                    "aria-owns": this.ids.menu,
                    "aria-haspopup": "true"
                }).insertAfter(this.element);
                a("\x3cspan\x3e", {
                    "class": "ui-icon " + this.options.icons.button
                }).prependTo(this.button);
                this.buttonText = a("\x3cspan\x3e", {
                    "class": "ui-selectmenu-text"
                }).appendTo(this.button);
                this._setText(this.buttonText, this.element.find("option:selected").text());
                this._resizeButton();
                this._on(this.button, this._buttonEvents);
                this.button.one("focusin", function() {
                    b.menuItems ||
                        b._refreshMenu()
                });
                this._hoverable(this.button);
                this._focusable(this.button)
            },
            _drawMenu: function() {
                var b = this;
                this.menu = a("\x3cul\x3e", {
                    "aria-hidden": "true",
                    "aria-labelledby": this.ids.button,
                    id: this.ids.menu
                });
                this.menuWrap = a("\x3cdiv\x3e", {
                    "class": "ui-selectmenu-menu ui-front"
                }).append(this.menu).appendTo(this._appendTo());
                this.menuInstance = this.menu.menu({
                    role: "listbox",
                    select: function(c, e) {
                        c.preventDefault();
                        b._setSelection();
                        b._select(e.item.data("ui-selectmenu-item"), c)
                    },
                    focus: function(c, e) {
                        e =
                            e.item.data("ui-selectmenu-item");
                        null != b.focusIndex && e.index !== b.focusIndex && (b._trigger("focus", c, {
                            item: e
                        }), b.isOpen || b._select(e, c));
                        b.focusIndex = e.index;
                        b.button.attr("aria-activedescendant", b.menuItems.eq(e.index).attr("id"))
                    }
                }).menu("instance");
                this.menu.addClass("ui-corner-bottom").removeClass("ui-corner-all");
                this.menuInstance._off(this.menu, "mouseleave");
                this.menuInstance._closeOnDocumentClick = function() {
                    return !1
                };
                this.menuInstance._isDivider = function() {
                    return !1
                }
            },
            refresh: function() {
                this._refreshMenu();
                this._setText(this.buttonText, this._getSelectedItem().text());
                this.options.width || this._resizeButton()
            },
            _refreshMenu: function() {
                this.menu.empty();
                var b = this.element.find("option");
                b.length && (this._parseOptions(b), this._renderMenu(this.menu, this.items), this.menuInstance.refresh(), this.menuItems = this.menu.find("li").not(".ui-selectmenu-optgroup"), b = this._getSelectedItem(), this.menuInstance.focus(null, b), this._setAria(b.data("ui-selectmenu-item")), this._setOption("disabled", this.element.prop("disabled")))
            },
            open: function(b) {
                this.options.disabled || (this.menuItems ? (this.menu.find(".ui-state-focus").removeClass("ui-state-focus"), this.menuInstance.focus(null, this._getSelectedItem())) : this._refreshMenu(), this.isOpen = !0, this._toggleAttr(), this._resizeMenu(), this._position(), this._on(this.document, this._documentClick), this._trigger("open", b))
            },
            _position: function() {
                this.menuWrap.position(a.extend({
                    of: this.button
                }, this.options.position))
            },
            close: function(b) {
                this.isOpen && (this.isOpen = !1, this._toggleAttr(), this.range =
                    null, this._off(this.document), this._trigger("close", b))
            },
            widget: function() {
                return this.button
            },
            menuWidget: function() {
                return this.menu
            },
            _renderMenu: function(b, c) {
                var e = this,
                    d = "";
                a.each(c, function(c, f) {
                    f.optgroup !== d && (a("\x3cli\x3e", {
                        "class": "ui-selectmenu-optgroup ui-menu-divider" + (f.element.parent("optgroup").prop("disabled") ? " ui-state-disabled" : ""),
                        text: f.optgroup
                    }).appendTo(b), d = f.optgroup);
                    e._renderItemData(b, f)
                })
            },
            _renderItemData: function(b, c) {
                return this._renderItem(b, c).data("ui-selectmenu-item",
                    c)
            },
            _renderItem: function(b, c) {
                var e = a("\x3cli\x3e");
                c.disabled && e.addClass("ui-state-disabled");
                this._setText(e, c.label);
                return e.appendTo(b)
            },
            _setText: function(b, c) {
                c ? b.text(c) : b.html("\x26#160;")
            },
            _move: function(b, c) {
                var e = ".ui-menu-item";
                if (this.isOpen) var a = this.menuItems.eq(this.focusIndex);
                else a = this.menuItems.eq(this.element[0].selectedIndex), e += ":not(.ui-state-disabled)";
                b = "first" === b || "last" === b ? a["first" === b ? "prevAll" : "nextAll"](e).eq(-1) : a[b + "All"](e).eq(0);
                b.length && this.menuInstance.focus(c,
                    b)
            },
            _getSelectedItem: function() {
                return this.menuItems.eq(this.element[0].selectedIndex)
            },
            _toggle: function(b) {
                this[this.isOpen ? "close" : "open"](b)
            },
            _setSelection: function() {
                if (this.range) {
                    if (window.getSelection) {
                        var b = window.getSelection();
                        b.removeAllRanges();
                        b.addRange(this.range)
                    } else this.range.select();
                    this.button.focus()
                }
            },
            _documentClick: {
                mousedown: function(b) {
                    this.isOpen && (a(b.target).closest(".ui-selectmenu-menu, #" + this.ids.button).length || this.close(b))
                }
            },
            _buttonEvents: {
                mousedown: function() {
                    if (window.getSelection) {
                        var b =
                            window.getSelection();
                        b.rangeCount && (this.range = b.getRangeAt(0))
                    } else this.range = document.selection.createRange()
                },
                click: function(b) {
                    this._setSelection();
                    this._toggle(b)
                },
                keydown: function(b) {
                    var c = !0;
                    switch (b.keyCode) {
                        case a.ui.keyCode.TAB:
                        case a.ui.keyCode.ESCAPE:
                            this.close(b);
                            c = !1;
                            break;
                        case a.ui.keyCode.ENTER:
                            this.isOpen && this._selectFocusedItem(b);
                            break;
                        case a.ui.keyCode.UP:
                            b.altKey ? this._toggle(b) : this._move("prev", b);
                            break;
                        case a.ui.keyCode.DOWN:
                            b.altKey ? this._toggle(b) : this._move("next", b);
                            break;
                        case a.ui.keyCode.SPACE:
                            this.isOpen ? this._selectFocusedItem(b) : this._toggle(b);
                            break;
                        case a.ui.keyCode.LEFT:
                            this._move("prev", b);
                            break;
                        case a.ui.keyCode.RIGHT:
                            this._move("next", b);
                            break;
                        case a.ui.keyCode.HOME:
                        case a.ui.keyCode.PAGE_UP:
                            this._move("first", b);
                            break;
                        case a.ui.keyCode.END:
                        case a.ui.keyCode.PAGE_DOWN:
                            this._move("last", b);
                            break;
                        default:
                            this.menu.trigger(b), c = !1
                    }
                    c && b.preventDefault()
                }
            },
            _selectFocusedItem: function(b) {
                var c = this.menuItems.eq(this.focusIndex);
                c.hasClass("ui-state-disabled") ||
                    this._select(c.data("ui-selectmenu-item"), b)
            },
            _select: function(b, c) {
                var e = this.element[0].selectedIndex;
                this.element[0].selectedIndex = b.index;
                this._setText(this.buttonText, b.label);
                this._setAria(b);
                this._trigger("select", c, {
                    item: b
                });
                b.index !== e && this._trigger("change", c, {
                    item: b
                });
                this.close(c)
            },
            _setAria: function(b) {
                b = this.menuItems.eq(b.index).attr("id");
                this.button.attr({
                    "aria-labelledby": b,
                    "aria-activedescendant": b
                });
                this.menu.attr("aria-activedescendant", b)
            },
            _setOption: function(b, c) {
                "icons" ===
                b && this.button.find("span.ui-icon").removeClass(this.options.icons.button).addClass(c.button);
                this._super(b, c);
                "appendTo" === b && this.menuWrap.appendTo(this._appendTo());
                "disabled" === b && (this.menuInstance.option("disabled", c), this.button.toggleClass("ui-state-disabled", c).attr("aria-disabled", c), this.element.prop("disabled", c), c ? (this.button.attr("tabindex", -1), this.close()) : this.button.attr("tabindex", 0));
                "width" === b && this._resizeButton()
            },
            _appendTo: function() {
                var b = this.options.appendTo;
                b && (b = b.jquery ||
                    b.nodeType ? a(b) : this.document.find(b).eq(0));
                b && b[0] || (b = this.element.closest(".ui-front"));
                b.length || (b = this.document[0].body);
                return b
            },
            _toggleAttr: function() {
                this.button.toggleClass("ui-corner-top", this.isOpen).toggleClass("ui-corner-all", !this.isOpen).attr("aria-expanded", this.isOpen);
                this.menuWrap.toggleClass("ui-selectmenu-open", this.isOpen);
                this.menu.attr("aria-hidden", !this.isOpen)
            },
            _resizeButton: function() {
                var b = this.options.width;
                b || (b = this.element.show().outerWidth(), this.element.hide());
                this.button.outerWidth(b)
            },
            _resizeMenu: function() {
                this.menu.outerWidth(Math.max(this.button.outerWidth(), this.menu.width("").outerWidth() + 1))
            },
            _getCreateOptions: function() {
                return {
                    disabled: this.element.prop("disabled")
                }
            },
            _parseOptions: function(b) {
                var c = [];
                b.each(function(b, e) {
                    e = a(e);
                    var d = e.parent("optgroup");
                    c.push({
                        element: e,
                        index: b,
                        value: e.val(),
                        label: e.text(),
                        optgroup: d.attr("label") || "",
                        disabled: d.prop("disabled") || e.prop("disabled")
                    })
                });
                this.items = c
            },
            _destroy: function() {
                this.menuWrap.remove();
                this.button.remove();
                this.element.show();
                this.element.removeUniqueId();
                this.label.attr("for", this.ids.element)
            }
        });
        a.widget("ui.slider", a.ui.mouse, {
            version: "1.11.4",
            widgetEventPrefix: "slide",
            options: {
                animate: !1,
                distance: 0,
                max: 100,
                min: 0,
                orientation: "horizontal",
                range: !1,
                step: 1,
                value: 0,
                values: null,
                change: null,
                slide: null,
                start: null,
                stop: null
            },
            numPages: 5,
            _create: function() {
                this._mouseSliding = this._keySliding = !1;
                this._animateOff = !0;
                this._handleIndex = null;
                this._detectOrientation();
                this._mouseInit();
                this._calculateNewMax();
                this.element.addClass("ui-slider ui-slider-" + this.orientation + " ui-widget ui-widget-content ui-corner-all");
                this._refresh();
                this._setOption("disabled", this.options.disabled);
                this._animateOff = !1
            },
            _refresh: function() {
                this._createRange();
                this._createHandles();
                this._setupEvents();
                this._refreshValue()
            },
            _createHandles: function() {
                var b = this.options;
                var c = this.element.find(".ui-slider-handle").addClass("ui-state-default ui-corner-all"),
                    e = [];
                var d = b.values && b.values.length || 1;
                c.length > d && (c.slice(d).remove(),
                    c = c.slice(0, d));
                for (b = c.length; b < d; b++) e.push("\x3cspan class\x3d'ui-slider-handle ui-state-default ui-corner-all' tabindex\x3d'0'\x3e\x3c/span\x3e");
                this.handles = c.add(a(e.join("")).appendTo(this.element));
                this.handle = this.handles.eq(0);
                this.handles.each(function(b) {
                    a(this).data("ui-slider-handle-index", b)
                })
            },
            _createRange: function() {
                var b = this.options,
                    c = "";
                b.range ? (!0 === b.range && (b.values ? b.values.length && 2 !== b.values.length ? b.values = [b.values[0], b.values[0]] : a.isArray(b.values) && (b.values = b.values.slice(0)) :
                    b.values = [this._valueMin(), this._valueMin()]), this.range && this.range.length ? this.range.removeClass("ui-slider-range-min ui-slider-range-max").css({
                    left: "",
                    bottom: ""
                }) : (this.range = a("\x3cdiv\x3e\x3c/div\x3e").appendTo(this.element), c = "ui-slider-range ui-widget-header ui-corner-all"), this.range.addClass(c + ("min" === b.range || "max" === b.range ? " ui-slider-range-" + b.range : ""))) : (this.range && this.range.remove(), this.range = null)
            },
            _setupEvents: function() {
                this._off(this.handles);
                this._on(this.handles, this._handleEvents);
                this._hoverable(this.handles);
                this._focusable(this.handles)
            },
            _destroy: function() {
                this.handles.remove();
                this.range && this.range.remove();
                this.element.removeClass("ui-slider ui-slider-horizontal ui-slider-vertical ui-widget ui-widget-content ui-corner-all");
                this._mouseDestroy()
            },
            _mouseCapture: function(b) {
                var c, e, d = this,
                    f = this.options;
                if (f.disabled) return !1;
                this.elementSize = {
                    width: this.element.outerWidth(),
                    height: this.element.outerHeight()
                };
                this.elementOffset = this.element.offset();
                var h = this._normValueFromMouse({
                    x: b.pageX,
                    y: b.pageY
                });
                var n = this._valueMax() - this._valueMin() + 1;
                this.handles.each(function(b) {
                    var k = Math.abs(h - d.values(b));
                    if (n > k || n === k && (b === d._lastChangedValue || d.values(b) === f.min)) n = k, c = a(this), e = b
                });
                if (!1 === this._start(b, e)) return !1;
                this._mouseSliding = !0;
                this._handleIndex = e;
                c.addClass("ui-state-active").focus();
                var l = c.offset();
                this._clickOffset = a(b.target).parents().addBack().is(".ui-slider-handle") ? {
                    left: b.pageX - l.left - c.width() / 2,
                    top: b.pageY - l.top - c.height() / 2 - (parseInt(c.css("borderTopWidth"), 10) ||
                        0) - (parseInt(c.css("borderBottomWidth"), 10) || 0) + (parseInt(c.css("marginTop"), 10) || 0)
                } : {
                    left: 0,
                    top: 0
                };
                this.handles.hasClass("ui-state-hover") || this._slide(b, e, h);
                return this._animateOff = !0
            },
            _mouseStart: function() {
                return !0
            },
            _mouseDrag: function(b) {
                var c = this._normValueFromMouse({
                    x: b.pageX,
                    y: b.pageY
                });
                this._slide(b, this._handleIndex, c);
                return !1
            },
            _mouseStop: function(b) {
                this.handles.removeClass("ui-state-active");
                this._mouseSliding = !1;
                this._stop(b, this._handleIndex);
                this._change(b, this._handleIndex);
                this._clickOffset =
                    this._handleIndex = null;
                return this._animateOff = !1
            },
            _detectOrientation: function() {
                this.orientation = "vertical" === this.options.orientation ? "vertical" : "horizontal"
            },
            _normValueFromMouse: function(b) {
                if ("horizontal" === this.orientation) {
                    var c = this.elementSize.width;
                    b = b.x - this.elementOffset.left - (this._clickOffset ? this._clickOffset.left : 0)
                } else c = this.elementSize.height, b = b.y - this.elementOffset.top - (this._clickOffset ? this._clickOffset.top : 0);
                c = b / c;
                1 < c && (c = 1);
                0 > c && (c = 0);
                "vertical" === this.orientation && (c = 1 -
                    c);
                b = this._valueMax() - this._valueMin();
                c = this._valueMin() + c * b;
                return this._trimAlignValue(c)
            },
            _start: function(b, c) {
                var e = {
                    handle: this.handles[c],
                    value: this.value()
                };
                this.options.values && this.options.values.length && (e.value = this.values(c), e.values = this.values());
                return this._trigger("start", b, e)
            },
            _slide: function(b, c, e) {
                if (this.options.values && this.options.values.length) {
                    var a = this.values(c ? 0 : 1);
                    2 === this.options.values.length && !0 === this.options.range && (0 === c && e > a || 1 === c && e < a) && (e = a);
                    e !== this.values(c) &&
                        (a = this.values(), a[c] = e, b = this._trigger("slide", b, {
                            handle: this.handles[c],
                            value: e,
                            values: a
                        }), this.values(c ? 0 : 1), !1 !== b && this.values(c, e))
                } else e !== this.value() && (b = this._trigger("slide", b, {
                    handle: this.handles[c],
                    value: e
                }), !1 !== b && this.value(e))
            },
            _stop: function(b, c) {
                var e = {
                    handle: this.handles[c],
                    value: this.value()
                };
                this.options.values && this.options.values.length && (e.value = this.values(c), e.values = this.values());
                this._trigger("stop", b, e)
            },
            _change: function(b, c) {
                if (!this._keySliding && !this._mouseSliding) {
                    var e = {
                        handle: this.handles[c],
                        value: this.value()
                    };
                    this.options.values && this.options.values.length && (e.value = this.values(c), e.values = this.values());
                    this._lastChangedValue = c;
                    this._trigger("change", b, e)
                }
            },
            value: function(b) {
                if (arguments.length) this.options.value = this._trimAlignValue(b), this._refreshValue(), this._change(null, 0);
                else return this._value()
            },
            values: function(b, c) {
                var e;
                if (1 < arguments.length) this.options.values[b] = this._trimAlignValue(c), this._refreshValue(), this._change(null, b);
                else if (arguments.length)
                    if (a.isArray(arguments[0])) {
                        var d =
                            this.options.values;
                        var f = arguments[0];
                        for (e = 0; e < d.length; e += 1) d[e] = this._trimAlignValue(f[e]), this._change(null, e);
                        this._refreshValue()
                    } else return this.options.values && this.options.values.length ? this._values(b) : this.value();
                else return this._values()
            },
            _setOption: function(b, c) {
                var e = 0;
                "range" === b && !0 === this.options.range && ("min" === c ? (this.options.value = this._values(0), this.options.values = null) : "max" === c && (this.options.value = this._values(this.options.values.length - 1), this.options.values = null));
                a.isArray(this.options.values) &&
                    (e = this.options.values.length);
                "disabled" === b && this.element.toggleClass("ui-state-disabled", !!c);
                this._super(b, c);
                switch (b) {
                    case "orientation":
                        this._detectOrientation();
                        this.element.removeClass("ui-slider-horizontal ui-slider-vertical").addClass("ui-slider-" + this.orientation);
                        this._refreshValue();
                        this.handles.css("horizontal" === c ? "bottom" : "left", "");
                        break;
                    case "value":
                        this._animateOff = !0;
                        this._refreshValue();
                        this._change(null, 0);
                        this._animateOff = !1;
                        break;
                    case "values":
                        this._animateOff = !0;
                        this._refreshValue();
                        for (b = 0; b < e; b += 1) this._change(null, b);
                        this._animateOff = !1;
                        break;
                    case "step":
                    case "min":
                    case "max":
                        this._animateOff = !0;
                        this._calculateNewMax();
                        this._refreshValue();
                        this._animateOff = !1;
                        break;
                    case "range":
                        this._animateOff = !0, this._refresh(), this._animateOff = !1
                }
            },
            _value: function() {
                var b = this.options.value;
                return b = this._trimAlignValue(b)
            },
            _values: function(b) {
                var c;
                if (arguments.length) {
                    var e = this.options.values[b];
                    return e = this._trimAlignValue(e)
                }
                if (this.options.values && this.options.values.length) {
                    e = this.options.values.slice();
                    for (c = 0; c < e.length; c += 1) e[c] = this._trimAlignValue(e[c]);
                    return e
                }
                return []
            },
            _trimAlignValue: function(b) {
                if (b <= this._valueMin()) return this._valueMin();
                if (b >= this._valueMax()) return this._valueMax();
                var c = 0 < this.options.step ? this.options.step : 1,
                    e = (b - this._valueMin()) % c;
                b -= e;
                2 * Math.abs(e) >= c && (b += 0 < e ? c : -c);
                return parseFloat(b.toFixed(5))
            },
            _calculateNewMax: function() {
                var b = this.options.max,
                    c = this._valueMin(),
                    e = this.options.step;
                b = Math.floor(+(b - c).toFixed(this._precision()) / e) * e;
                this.max = parseFloat((b +
                    c).toFixed(this._precision()))
            },
            _precision: function() {
                var b = this._precisionOf(this.options.step);
                null !== this.options.min && (b = Math.max(b, this._precisionOf(this.options.min)));
                return b
            },
            _precisionOf: function(b) {
                b = b.toString();
                var c = b.indexOf(".");
                return -1 === c ? 0 : b.length - c - 1
            },
            _valueMin: function() {
                return this.options.min
            },
            _valueMax: function() {
                return this.max
            },
            _refreshValue: function() {
                var b, c = this.options.range,
                    e = this.options,
                    d = this,
                    f = this._animateOff ? !1 : e.animate,
                    h = {};
                if (this.options.values && this.options.values.length) this.handles.each(function(c) {
                    m =
                        (d.values(c) - d._valueMin()) / (d._valueMax() - d._valueMin()) * 100;
                    h["horizontal" === d.orientation ? "left" : "bottom"] = m + "%";
                    a(this).stop(1, 1)[f ? "animate" : "css"](h, e.animate);
                    if (!0 === d.options.range)
                        if ("horizontal" === d.orientation) {
                            if (0 === c) d.range.stop(1, 1)[f ? "animate" : "css"]({
                                left: m + "%"
                            }, e.animate);
                            if (1 === c) d.range[f ? "animate" : "css"]({
                                width: m - b + "%"
                            }, {
                                queue: !1,
                                duration: e.animate
                            })
                        } else {
                            if (0 === c) d.range.stop(1, 1)[f ? "animate" : "css"]({
                                bottom: m + "%"
                            }, e.animate);
                            if (1 === c) d.range[f ? "animate" : "css"]({
                                height: m - b +
                                    "%"
                            }, {
                                queue: !1,
                                duration: e.animate
                            })
                        } b = m
                });
                else {
                    var n = this.value();
                    var l = this._valueMin();
                    var g = this._valueMax();
                    var m = g !== l ? (n - l) / (g - l) * 100 : 0;
                    h["horizontal" === this.orientation ? "left" : "bottom"] = m + "%";
                    this.handle.stop(1, 1)[f ? "animate" : "css"](h, e.animate);
                    if ("min" === c && "horizontal" === this.orientation) this.range.stop(1, 1)[f ? "animate" : "css"]({
                        width: m + "%"
                    }, e.animate);
                    if ("max" === c && "horizontal" === this.orientation) this.range[f ? "animate" : "css"]({
                        width: 100 - m + "%"
                    }, {
                        queue: !1,
                        duration: e.animate
                    });
                    if ("min" === c &&
                        "vertical" === this.orientation) this.range.stop(1, 1)[f ? "animate" : "css"]({
                        height: m + "%"
                    }, e.animate);
                    if ("max" === c && "vertical" === this.orientation) this.range[f ? "animate" : "css"]({
                        height: 100 - m + "%"
                    }, {
                        queue: !1,
                        duration: e.animate
                    })
                }
            },
            _handleEvents: {
                keydown: function(b) {
                    var c, e = a(b.target).data("ui-slider-handle-index");
                    switch (b.keyCode) {
                        case a.ui.keyCode.HOME:
                        case a.ui.keyCode.END:
                        case a.ui.keyCode.PAGE_UP:
                        case a.ui.keyCode.PAGE_DOWN:
                        case a.ui.keyCode.UP:
                        case a.ui.keyCode.RIGHT:
                        case a.ui.keyCode.DOWN:
                        case a.ui.keyCode.LEFT:
                            if (b.preventDefault(),
                                !this._keySliding) {
                                this._keySliding = !0;
                                a(b.target).addClass("ui-state-active");
                                var d = this._start(b, e);
                                if (!1 === d) return
                            }
                    }
                    var f = this.options.step;
                    d = this.options.values && this.options.values.length ? c = this.values(e) : c = this.value();
                    switch (b.keyCode) {
                        case a.ui.keyCode.HOME:
                            c = this._valueMin();
                            break;
                        case a.ui.keyCode.END:
                            c = this._valueMax();
                            break;
                        case a.ui.keyCode.PAGE_UP:
                            c = this._trimAlignValue(d + (this._valueMax() - this._valueMin()) / this.numPages);
                            break;
                        case a.ui.keyCode.PAGE_DOWN:
                            c = this._trimAlignValue(d - (this._valueMax() -
                                this._valueMin()) / this.numPages);
                            break;
                        case a.ui.keyCode.UP:
                        case a.ui.keyCode.RIGHT:
                            if (d === this._valueMax()) return;
                            c = this._trimAlignValue(d + f);
                            break;
                        case a.ui.keyCode.DOWN:
                        case a.ui.keyCode.LEFT:
                            if (d === this._valueMin()) return;
                            c = this._trimAlignValue(d - f)
                    }
                    this._slide(b, e, c)
                },
                keyup: function(b) {
                    var c = a(b.target).data("ui-slider-handle-index");
                    this._keySliding && (this._keySliding = !1, this._stop(b, c), this._change(b, c), a(b.target).removeClass("ui-state-active"))
                }
            }
        });
        a.widget("ui.spinner", {
            version: "1.11.4",
            defaultElement: "\x3cinput\x3e",
            widgetEventPrefix: "spin",
            options: {
                culture: null,
                icons: {
                    down: "ui-icon-triangle-1-s",
                    up: "ui-icon-triangle-1-n"
                },
                incremental: !0,
                max: null,
                min: null,
                numberFormat: null,
                page: 10,
                step: 1,
                change: null,
                spin: null,
                start: null,
                stop: null
            },
            _create: function() {
                this._setOption("max", this.options.max);
                this._setOption("min", this.options.min);
                this._setOption("step", this.options.step);
                "" !== this.value() && this._value(this.element.val(), !0);
                this._draw();
                this._on(this._events);
                this._refresh();
                this._on(this.window, {
                    beforeunload: function() {
                        this.element.removeAttr("autocomplete")
                    }
                })
            },
            _getCreateOptions: function() {
                var b = {},
                    c = this.element;
                a.each(["min", "max", "step"], function(e, a) {
                    e = c.attr(a);
                    void 0 !== e && e.length && (b[a] = e)
                });
                return b
            },
            _events: {
                keydown: function(b) {
                    this._start(b) && this._keydown(b) && b.preventDefault()
                },
                keyup: "_stop",
                focus: function() {
                    this.previous = this.element.val()
                },
                blur: function(b) {
                    this.cancelBlur ? delete this.cancelBlur : (this._stop(), this._refresh(), this.previous !== this.element.val() && this._trigger("change",
                        b))
                },
                mousewheel: function(b, c) {
                    if (c) {
                        if (!this.spinning && !this._start(b)) return !1;
                        this._spin((0 < c ? 1 : -1) * this.options.step, b);
                        clearTimeout(this.mousewheelTimer);
                        this.mousewheelTimer = this._delay(function() {
                            this.spinning && this._stop(b)
                        }, 100);
                        b.preventDefault()
                    }
                },
                "mousedown .ui-spinner-button": function(b) {
                    function c() {
                        this.element[0] !== this.document[0].activeElement && (this.element.focus(), this.previous = e, this._delay(function() {
                            this.previous = e
                        }))
                    }
                    var e = this.element[0] === this.document[0].activeElement ? this.previous :
                        this.element.val();
                    b.preventDefault();
                    c.call(this);
                    this.cancelBlur = !0;
                    this._delay(function() {
                        delete this.cancelBlur;
                        c.call(this)
                    });
                    !1 !== this._start(b) && this._repeat(null, a(b.currentTarget).hasClass("ui-spinner-up") ? 1 : -1, b)
                },
                "mouseup .ui-spinner-button": "_stop",
                "mouseenter .ui-spinner-button": function(b) {
                    if (a(b.currentTarget).hasClass("ui-state-active")) {
                        if (!1 === this._start(b)) return !1;
                        this._repeat(null, a(b.currentTarget).hasClass("ui-spinner-up") ? 1 : -1, b)
                    }
                },
                "mouseleave .ui-spinner-button": "_stop"
            },
            _draw: function() {
                var b = this.uiSpinner = this.element.addClass("ui-spinner-input").attr("autocomplete", "off").wrap(this._uiSpinnerHtml()).parent().append(this._buttonHtml());
                this.element.attr("role", "spinbutton");
                this.buttons = b.find(".ui-spinner-button").attr("tabIndex", -1).button().removeClass("ui-corner-all");
                this.buttons.height() > Math.ceil(.5 * b.height()) && 0 < b.height() && b.height(b.height());
                this.options.disabled && this.disable()
            },
            _keydown: function(b) {
                var c = this.options,
                    e = a.ui.keyCode;
                switch (b.keyCode) {
                    case e.UP:
                        return this._repeat(null,
                            1, b), !0;
                    case e.DOWN:
                        return this._repeat(null, -1, b), !0;
                    case e.PAGE_UP:
                        return this._repeat(null, c.page, b), !0;
                    case e.PAGE_DOWN:
                        return this._repeat(null, -c.page, b), !0
                }
                return !1
            },
            _uiSpinnerHtml: function() {
                return "\x3cspan class\x3d'ui-spinner ui-widget ui-widget-content ui-corner-all'\x3e\x3c/span\x3e"
            },
            _buttonHtml: function() {
                return "\x3ca class\x3d'ui-spinner-button ui-spinner-up ui-corner-tr'\x3e\x3cspan class\x3d'ui-icon " + this.options.icons.up + "'\x3e\x26#9650;\x3c/span\x3e\x3c/a\x3e\x3ca class\x3d'ui-spinner-button ui-spinner-down ui-corner-br'\x3e\x3cspan class\x3d'ui-icon " +
                    this.options.icons.down + "'\x3e\x26#9660;\x3c/span\x3e\x3c/a\x3e"
            },
            _start: function(b) {
                if (!this.spinning && !1 === this._trigger("start", b)) return !1;
                this.counter || (this.counter = 1);
                return this.spinning = !0
            },
            _repeat: function(b, c, e) {
                b = b || 500;
                clearTimeout(this.timer);
                this.timer = this._delay(function() {
                    this._repeat(40, c, e)
                }, b);
                this._spin(c * this.options.step, e)
            },
            _spin: function(b, c) {
                var e = this.value() || 0;
                this.counter || (this.counter = 1);
                e = this._adjustValue(e + b * this._increment(this.counter));
                this.spinning && !1 === this._trigger("spin",
                    c, {
                        value: e
                    }) || (this._value(e), this.counter++)
            },
            _increment: function(b) {
                var c = this.options.incremental;
                return c ? a.isFunction(c) ? c(b) : Math.floor(b * b * b / 5E4 - b * b / 500 + 17 * b / 200 + 1) : 1
            },
            _precision: function() {
                var b = this._precisionOf(this.options.step);
                null !== this.options.min && (b = Math.max(b, this._precisionOf(this.options.min)));
                return b
            },
            _precisionOf: function(b) {
                b = b.toString();
                var c = b.indexOf(".");
                return -1 === c ? 0 : b.length - c - 1
            },
            _adjustValue: function(b) {
                var c = this.options;
                var e = null !== c.min ? c.min : 0;
                b = e + Math.round((b -
                    e) / c.step) * c.step;
                b = parseFloat(b.toFixed(this._precision()));
                return null !== c.max && b > c.max ? c.max : null !== c.min && b < c.min ? c.min : b
            },
            _stop: function(b) {
                this.spinning && (clearTimeout(this.timer), clearTimeout(this.mousewheelTimer), this.counter = 0, this.spinning = !1, this._trigger("stop", b))
            },
            _setOption: function(b, c) {
                if ("culture" === b || "numberFormat" === b) {
                    var e = this._parse(this.element.val());
                    this.options[b] = c;
                    this.element.val(this._format(e))
                } else "max" !== b && "min" !== b && "step" !== b || "string" !== typeof c || (c = this._parse(c)),
                    "icons" === b && (this.buttons.first().find(".ui-icon").removeClass(this.options.icons.up).addClass(c.up), this.buttons.last().find(".ui-icon").removeClass(this.options.icons.down).addClass(c.down)), this._super(b, c), "disabled" === b && (this.widget().toggleClass("ui-state-disabled", !!c), this.element.prop("disabled", !!c), this.buttons.button(c ? "disable" : "enable"))
            },
            _setOptions: q(function(b) {
                this._super(b)
            }),
            _parse: function(b) {
                "string" === typeof b && "" !== b && (b = window.Globalize && this.options.numberFormat ? Globalize.parseFloat(b,
                    10, this.options.culture) : +b);
                return "" === b || isNaN(b) ? null : b
            },
            _format: function(b) {
                return "" === b ? "" : window.Globalize && this.options.numberFormat ? Globalize.format(b, this.options.numberFormat, this.options.culture) : b
            },
            _refresh: function() {
                this.element.attr({
                    "aria-valuemin": this.options.min,
                    "aria-valuemax": this.options.max,
                    "aria-valuenow": this._parse(this.element.val())
                })
            },
            isValid: function() {
                var b = this.value();
                return null === b ? !1 : b === this._adjustValue(b)
            },
            _value: function(b, c) {
                if ("" !== b) {
                    var e = this._parse(b);
                    null !== e && (c || (e = this._adjustValue(e)), b = this._format(e))
                }
                this.element.val(b);
                this._refresh()
            },
            _destroy: function() {
                this.element.removeClass("ui-spinner-input").prop("disabled", !1).removeAttr("autocomplete").removeAttr("role").removeAttr("aria-valuemin").removeAttr("aria-valuemax").removeAttr("aria-valuenow");
                this.uiSpinner.replaceWith(this.element)
            },
            stepUp: q(function(b) {
                this._stepUp(b)
            }),
            _stepUp: function(b) {
                this._start() && (this._spin((b || 1) * this.options.step), this._stop())
            },
            stepDown: q(function(b) {
                this._stepDown(b)
            }),
            _stepDown: function(b) {
                this._start() && (this._spin((b || 1) * -this.options.step), this._stop())
            },
            pageUp: q(function(b) {
                this._stepUp((b || 1) * this.options.page)
            }),
            pageDown: q(function(b) {
                this._stepDown((b || 1) * this.options.page)
            }),
            value: function(b) {
                if (!arguments.length) return this._parse(this.element.val());
                q(this._value).call(this, b)
            },
            widget: function() {
                return this.uiSpinner
            }
        });
        a.widget("ui.tabs", {
            version: "1.11.4",
            delay: 300,
            options: {
                active: null,
                collapsible: !1,
                event: "click",
                heightStyle: "content",
                hide: null,
                show: null,
                activate: null,
                beforeActivate: null,
                beforeLoad: null,
                load: null
            },
            _isLocal: function() {
                var b = /#.*$/;
                return function(c) {
                    c = c.cloneNode(!1);
                    var e = c.href.replace(b, "");
                    var a = location.href.replace(b, "");
                    try {
                        e = decodeURIComponent(e)
                    } catch (F) {}
                    try {
                        a = decodeURIComponent(a)
                    } catch (F) {}
                    return 1 < c.hash.length && e === a
                }
            }(),
            _create: function() {
                var b = this,
                    c = this.options;
                this.running = !1;
                this.element.addClass("ui-tabs ui-widget ui-widget-content ui-corner-all").toggleClass("ui-tabs-collapsible", c.collapsible);
                this._processTabs();
                c.active = this._initialActive();
                a.isArray(c.disabled) && (c.disabled = a.unique(c.disabled.concat(a.map(this.tabs.filter(".ui-state-disabled"), function(c) {
                    return b.tabs.index(c)
                }))).sort());
                this.active = !1 !== this.options.active && this.anchors.length ? this._findActive(c.active) : a();
                this._refresh();
                this.active.length && this.load(c.active)
            },
            _initialActive: function() {
                var b = this.options.active,
                    c = this.options.collapsible,
                    e = location.hash.substring(1);
                null === b && (e && this.tabs.each(function(c, d) {
                    if (a(d).attr("aria-controls") ===
                        e) return b = c, !1
                }), null === b && (b = this.tabs.index(this.tabs.filter(".ui-tabs-active"))), null === b || -1 === b) && (b = this.tabs.length ? 0 : !1);
                !1 !== b && (b = this.tabs.index(this.tabs.eq(b)), -1 === b && (b = c ? !1 : 0));
                !c && !1 === b && this.anchors.length && (b = 0);
                return b
            },
            _getCreateEventData: function() {
                return {
                    tab: this.active,
                    panel: this.active.length ? this._getPanelForTab(this.active) : a()
                }
            },
            _tabKeydown: function(b) {
                var c = a(this.document[0].activeElement).closest("li"),
                    e = this.tabs.index(c),
                    d = !0;
                if (!this._handlePageNav(b)) {
                    switch (b.keyCode) {
                        case a.ui.keyCode.RIGHT:
                        case a.ui.keyCode.DOWN:
                            e++;
                            break;
                        case a.ui.keyCode.UP:
                        case a.ui.keyCode.LEFT:
                            d = !1;
                            e--;
                            break;
                        case a.ui.keyCode.END:
                            e = this.anchors.length - 1;
                            break;
                        case a.ui.keyCode.HOME:
                            e = 0;
                            break;
                        case a.ui.keyCode.SPACE:
                            b.preventDefault();
                            clearTimeout(this.activating);
                            this._activate(e);
                            return;
                        case a.ui.keyCode.ENTER:
                            b.preventDefault();
                            clearTimeout(this.activating);
                            this._activate(e === this.options.active ? !1 : e);
                            return;
                        default:
                            return
                    }
                    b.preventDefault();
                    clearTimeout(this.activating);
                    e = this._focusNextTab(e, d);
                    b.ctrlKey || b.metaKey || (c.attr("aria-selected",
                        "false"), this.tabs.eq(e).attr("aria-selected", "true"), this.activating = this._delay(function() {
                        this.option("active", e)
                    }, this.delay))
                }
            },
            _panelKeydown: function(b) {
                !this._handlePageNav(b) && b.ctrlKey && b.keyCode === a.ui.keyCode.UP && (b.preventDefault(), this.active.focus())
            },
            _handlePageNav: function(b) {
                if (b.altKey && b.keyCode === a.ui.keyCode.PAGE_UP) return this._activate(this._focusNextTab(this.options.active - 1, !1)), !0;
                if (b.altKey && b.keyCode === a.ui.keyCode.PAGE_DOWN) return this._activate(this._focusNextTab(this.options.active +
                    1, !0)), !0
            },
            _findNextTab: function(b, c) {
                function e() {
                    b > d && (b = 0);
                    0 > b && (b = d);
                    return b
                }
                for (var d = this.tabs.length - 1; - 1 !== a.inArray(e(), this.options.disabled);) b = c ? b + 1 : b - 1;
                return b
            },
            _focusNextTab: function(b, c) {
                b = this._findNextTab(b, c);
                this.tabs.eq(b).focus();
                return b
            },
            _setOption: function(b, c) {
                "active" === b ? this._activate(c) : "disabled" === b ? this._setupDisabled(c) : (this._super(b, c), "collapsible" === b && (this.element.toggleClass("ui-tabs-collapsible", c), c || !1 !== this.options.active || this._activate(0)), "event" ===
                    b && this._setupEvents(c), "heightStyle" === b && this._setupHeightStyle(c))
            },
            _sanitizeSelector: function(b) {
                return b ? b.replace(/[!"$%&'()*+,.\/:;<=>?@\[\]\^`{|}~]/g, "\\$\x26") : ""
            },
            refresh: function() {
                var b = this.options,
                    c = this.tablist.children(":has(a[href])");
                b.disabled = a.map(c.filter(".ui-state-disabled"), function(b) {
                    return c.index(b)
                });
                this._processTabs();
                !1 !== b.active && this.anchors.length ? this.active.length && !a.contains(this.tablist[0], this.active[0]) ? this.tabs.length === b.disabled.length ? (b.active = !1,
                    this.active = a()) : this._activate(this._findNextTab(Math.max(0, b.active - 1), !1)) : b.active = this.tabs.index(this.active) : (b.active = !1, this.active = a());
                this._refresh()
            },
            _refresh: function() {
                this._setupDisabled(this.options.disabled);
                this._setupEvents(this.options.event);
                this._setupHeightStyle(this.options.heightStyle);
                this.tabs.not(this.active).attr({
                    "aria-selected": "false",
                    "aria-expanded": "false",
                    tabIndex: -1
                });
                this.panels.not(this._getPanelForTab(this.active)).hide().attr({
                    "aria-hidden": "true"
                });
                this.active.length ?
                    (this.active.addClass("ui-tabs-active ui-state-active").attr({
                        "aria-selected": "true",
                        "aria-expanded": "true",
                        tabIndex: 0
                    }), this._getPanelForTab(this.active).show().attr({
                        "aria-hidden": "false"
                    })) : this.tabs.eq(0).attr("tabIndex", 0)
            },
            _processTabs: function() {
                var b = this,
                    c = this.tabs,
                    e = this.anchors,
                    d = this.panels;
                this.tablist = this._getList().addClass("ui-tabs-nav ui-helper-reset ui-helper-clearfix ui-widget-header ui-corner-all").attr("role", "tablist").delegate("\x3e li", "mousedown" + this.eventNamespace, function(b) {
                    a(this).is(".ui-state-disabled") &&
                        b.preventDefault()
                }).delegate(".ui-tabs-anchor", "focus" + this.eventNamespace, function() {
                    a(this).closest("li").is(".ui-state-disabled") && this.blur()
                });
                this.tabs = this.tablist.find("\x3e li:has(a[href])").addClass("ui-state-default ui-corner-top").attr({
                    role: "tab",
                    tabIndex: -1
                });
                this.anchors = this.tabs.map(function() {
                    return a("a", this)[0]
                }).addClass("ui-tabs-anchor").attr({
                    role: "presentation",
                    tabIndex: -1
                });
                this.panels = a();
                this.anchors.each(function(c, e) {
                    var d = a(e).uniqueId().attr("id"),
                        f = a(e).closest("li"),
                        h = f.attr("aria-controls");
                    if (b._isLocal(e)) {
                        c = e.hash;
                        e = c.substring(1);
                        var k = b.element.find(b._sanitizeSelector(c))
                    } else e = f.attr("aria-controls") || a({}).uniqueId()[0].id, k = b.element.find("#" + e), k.length || (k = b._createPanel(e), k.insertAfter(b.panels[c - 1] || b.tablist)), k.attr("aria-live", "polite");
                    k.length && (b.panels = b.panels.add(k));
                    h && f.data("ui-tabs-aria-controls", h);
                    f.attr({
                        "aria-controls": e,
                        "aria-labelledby": d
                    });
                    k.attr("aria-labelledby", d)
                });
                this.panels.addClass("ui-tabs-panel ui-widget-content ui-corner-bottom").attr("role",
                    "tabpanel");
                c && (this._off(c.not(this.tabs)), this._off(e.not(this.anchors)), this._off(d.not(this.panels)))
            },
            _getList: function() {
                return this.tablist || this.element.find("ol,ul").eq(0)
            },
            _createPanel: function(b) {
                return a("\x3cdiv\x3e").attr("id", b).addClass("ui-tabs-panel ui-widget-content ui-corner-bottom").data("ui-tabs-destroy", !0)
            },
            _setupDisabled: function(b) {
                a.isArray(b) && (b.length ? b.length === this.anchors.length && (b = !0) : b = !1);
                for (var c = 0, e; e = this.tabs[c]; c++) !0 === b || -1 !== a.inArray(c, b) ? a(e).addClass("ui-state-disabled").attr("aria-disabled",
                    "true") : a(e).removeClass("ui-state-disabled").removeAttr("aria-disabled");
                this.options.disabled = b
            },
            _setupEvents: function(b) {
                var c = {};
                b && a.each(b.split(" "), function(b, e) {
                    c[e] = "_eventHandler"
                });
                this._off(this.anchors.add(this.tabs).add(this.panels));
                this._on(!0, this.anchors, {
                    click: function(b) {
                        b.preventDefault()
                    }
                });
                this._on(this.anchors, c);
                this._on(this.tabs, {
                    keydown: "_tabKeydown"
                });
                this._on(this.panels, {
                    keydown: "_panelKeydown"
                });
                this._focusable(this.tabs);
                this._hoverable(this.tabs)
            },
            _setupHeightStyle: function(b) {
                var c =
                    this.element.parent();
                if ("fill" === b) {
                    var e = c.height();
                    e -= this.element.outerHeight() - this.element.height();
                    this.element.siblings(":visible").each(function() {
                        var b = a(this),
                            c = b.css("position");
                        "absolute" !== c && "fixed" !== c && (e -= b.outerHeight(!0))
                    });
                    this.element.children().not(this.panels).each(function() {
                        e -= a(this).outerHeight(!0)
                    });
                    this.panels.each(function() {
                        a(this).height(Math.max(0, e - a(this).innerHeight() + a(this).height()))
                    }).css("overflow", "auto")
                } else "auto" === b && (e = 0, this.panels.each(function() {
                    e =
                        Math.max(e, a(this).height("").height())
                }).height(e))
            },
            _eventHandler: function(b) {
                var c = this.options,
                    e = this.active,
                    d = a(b.currentTarget).closest("li"),
                    f = d[0] === e[0],
                    h = f && c.collapsible,
                    n = h ? a() : this._getPanelForTab(d),
                    l = e.length ? this._getPanelForTab(e) : a();
                e = {
                    oldTab: e,
                    oldPanel: l,
                    newTab: h ? a() : d,
                    newPanel: n
                };
                b.preventDefault();
                d.hasClass("ui-state-disabled") || d.hasClass("ui-tabs-loading") || this.running || f && !c.collapsible || !1 === this._trigger("beforeActivate", b, e) || (c.active = h ? !1 : this.tabs.index(d), this.active =
                    f ? a() : d, this.xhr && this.xhr.abort(), l.length || n.length || a.error("jQuery UI Tabs: Mismatching fragment identifier."), n.length && this.load(this.tabs.index(d), b), this._toggle(b, e))
            },
            _toggle: function(b, c) {
                function e() {
                    f.running = !1;
                    f._trigger("activate", b, c)
                }

                function d() {
                    c.newTab.closest("li").addClass("ui-tabs-active ui-state-active");
                    h.length && f.options.show ? f._show(h, f.options.show, e) : (h.show(), e())
                }
                var f = this,
                    h = c.newPanel,
                    n = c.oldPanel;
                this.running = !0;
                n.length && this.options.hide ? this._hide(n, this.options.hide,
                    function() {
                        c.oldTab.closest("li").removeClass("ui-tabs-active ui-state-active");
                        d()
                    }) : (c.oldTab.closest("li").removeClass("ui-tabs-active ui-state-active"), n.hide(), d());
                n.attr("aria-hidden", "true");
                c.oldTab.attr({
                    "aria-selected": "false",
                    "aria-expanded": "false"
                });
                h.length && n.length ? c.oldTab.attr("tabIndex", -1) : h.length && this.tabs.filter(function() {
                    return 0 === a(this).attr("tabIndex")
                }).attr("tabIndex", -1);
                h.attr("aria-hidden", "false");
                c.newTab.attr({
                    "aria-selected": "true",
                    "aria-expanded": "true",
                    tabIndex: 0
                })
            },
            _activate: function(b) {
                b = this._findActive(b);
                b[0] !== this.active[0] && (b.length || (b = this.active), b = b.find(".ui-tabs-anchor")[0], this._eventHandler({
                    target: b,
                    currentTarget: b,
                    preventDefault: a.noop
                }))
            },
            _findActive: function(b) {
                return !1 === b ? a() : this.tabs.eq(b)
            },
            _getIndex: function(b) {
                "string" === typeof b && (b = this.anchors.index(this.anchors.filter("[href$\x3d'" + b + "']")));
                return b
            },
            _destroy: function() {
                this.xhr && this.xhr.abort();
                this.element.removeClass("ui-tabs ui-widget ui-widget-content ui-corner-all ui-tabs-collapsible");
                this.tablist.removeClass("ui-tabs-nav ui-helper-reset ui-helper-clearfix ui-widget-header ui-corner-all").removeAttr("role");
                this.anchors.removeClass("ui-tabs-anchor").removeAttr("role").removeAttr("tabIndex").removeUniqueId();
                this.tablist.unbind(this.eventNamespace);
                this.tabs.add(this.panels).each(function() {
                    a.data(this, "ui-tabs-destroy") ? a(this).remove() : a(this).removeClass("ui-state-default ui-state-active ui-state-disabled ui-corner-top ui-corner-bottom ui-widget-content ui-tabs-active ui-tabs-panel").removeAttr("tabIndex").removeAttr("aria-live").removeAttr("aria-busy").removeAttr("aria-selected").removeAttr("aria-labelledby").removeAttr("aria-hidden").removeAttr("aria-expanded").removeAttr("role")
                });
                this.tabs.each(function() {
                    var b = a(this),
                        c = b.data("ui-tabs-aria-controls");
                    c ? b.attr("aria-controls", c).removeData("ui-tabs-aria-controls") : b.removeAttr("aria-controls")
                });
                this.panels.show();
                "content" !== this.options.heightStyle && this.panels.css("height", "")
            },
            enable: function(b) {
                var c = this.options.disabled;
                !1 !== c && (void 0 === b ? c = !1 : (b = this._getIndex(b), c = a.isArray(c) ? a.map(c, function(c) {
                    return c !== b ? c : null
                }) : a.map(this.tabs, function(c, e) {
                    return e !== b ? e : null
                })), this._setupDisabled(c))
            },
            disable: function(b) {
                var c =
                    this.options.disabled;
                if (!0 !== c) {
                    if (void 0 === b) c = !0;
                    else {
                        b = this._getIndex(b);
                        if (-1 !== a.inArray(b, c)) return;
                        c = a.isArray(c) ? a.merge([b], c).sort() : [b]
                    }
                    this._setupDisabled(c)
                }
            },
            load: function(b, c) {
                b = this._getIndex(b);
                var e = this,
                    d = this.tabs.eq(b);
                b = d.find(".ui-tabs-anchor");
                var f = this._getPanelForTab(d),
                    h = {
                        tab: d,
                        panel: f
                    },
                    n = function(b, c) {
                        "abort" === c && e.panels.stop(!1, !0);
                        d.removeClass("ui-tabs-loading");
                        f.removeAttr("aria-busy");
                        b === e.xhr && delete e.xhr
                    };
                this._isLocal(b[0]) || (this.xhr = a.ajax(this._ajaxSettings(b,
                    c, h))) && "canceled" !== this.xhr.statusText && (d.addClass("ui-tabs-loading"), f.attr("aria-busy", "true"), this.xhr.done(function(b, a, d) {
                    setTimeout(function() {
                        f.html(b);
                        e._trigger("load", c, h);
                        n(d, a)
                    }, 1)
                }).fail(function(b, c) {
                    setTimeout(function() {
                        n(b, c)
                    }, 1)
                }))
            },
            _ajaxSettings: function(b, c, e) {
                var d = this;
                return {
                    url: b.attr("href"),
                    beforeSend: function(b, f) {
                        return d._trigger("beforeLoad", c, a.extend({
                            jqXHR: b,
                            ajaxSettings: f
                        }, e))
                    }
                }
            },
            _getPanelForTab: function(b) {
                b = a(b).attr("aria-controls");
                return this.element.find(this._sanitizeSelector("#" +
                    b))
            }
        });
        a.widget("ui.tooltip", {
            version: "1.11.4",
            options: {
                content: function() {
                    var b = a(this).attr("title") || "";
                    return a("\x3ca\x3e").text(b).html()
                },
                hide: !0,
                items: "[title]:not([disabled])",
                position: {
                    my: "left top+15",
                    at: "left bottom",
                    collision: "flipfit flip"
                },
                show: !0,
                tooltipClass: null,
                track: !1,
                close: null,
                open: null
            },
            _addDescribedBy: function(b, c) {
                var e = (b.attr("aria-describedby") || "").split(/\s+/);
                e.push(c);
                b.data("ui-tooltip-id", c).attr("aria-describedby", a.trim(e.join(" ")))
            },
            _removeDescribedBy: function(b) {
                var c =
                    b.data("ui-tooltip-id"),
                    e = (b.attr("aria-describedby") || "").split(/\s+/);
                c = a.inArray(c, e); - 1 !== c && e.splice(c, 1);
                b.removeData("ui-tooltip-id");
                (e = a.trim(e.join(" "))) ? b.attr("aria-describedby", e): b.removeAttr("aria-describedby")
            },
            _create: function() {
                this._on({
                    mouseover: "open",
                    focusin: "open"
                });
                this.tooltips = {};
                this.parents = {};
                this.options.disabled && this._disable();
                this.liveRegion = a("\x3cdiv\x3e").attr({
                    role: "log",
                    "aria-live": "assertive",
                    "aria-relevant": "additions"
                }).addClass("ui-helper-hidden-accessible").appendTo(this.document[0].body)
            },
            _setOption: function(b, c) {
                var e = this;
                "disabled" === b ? (this[c ? "_disable" : "_enable"](), this.options[b] = c) : (this._super(b, c), "content" === b && a.each(this.tooltips, function(b, c) {
                    e._updateContent(c.element)
                }))
            },
            _disable: function() {
                var b = this;
                a.each(this.tooltips, function(c, e) {
                    c = a.Event("blur");
                    c.target = c.currentTarget = e.element[0];
                    b.close(c, !0)
                });
                this.element.find(this.options.items).addBack().each(function() {
                    var b = a(this);
                    b.is("[title]") && b.data("ui-tooltip-title", b.attr("title")).removeAttr("title")
                })
            },
            _enable: function() {
                this.element.find(this.options.items).addBack().each(function() {
                    var b = a(this);
                    b.data("ui-tooltip-title") && b.attr("title", b.data("ui-tooltip-title"))
                })
            },
            open: function(b) {
                var c = this,
                    e = a(b ? b.target : this.element).closest(this.options.items);
                e.length && !e.data("ui-tooltip-id") && (e.attr("title") && e.data("ui-tooltip-title", e.attr("title")), e.data("ui-tooltip-open", !0), b && "mouseover" === b.type && e.parents().each(function() {
                    var b = a(this);
                    if (b.data("ui-tooltip-open")) {
                        var e = a.Event("blur");
                        e.target = e.currentTarget = this;
                        c.close(e, !0)
                    }
                    b.attr("title") && (b.uniqueId(), c.parents[this.id] = {
                        element: this,
                        title: b.attr("title")
                    }, b.attr("title", ""))
                }), this._registerCloseHandlers(b, e), this._updateContent(e, b))
            },
            _updateContent: function(b, c) {
                var e = this.options.content;
                var a = this,
                    d = c ? c.type : null;
                if ("string" === typeof e) return this._open(c, b, e);
                (e = e.call(b[0], function(e) {
                    a._delay(function() {
                        b.data("ui-tooltip-open") && (c && (c.type = d), this._open(c, b, e))
                    })
                })) && this._open(c, b, e)
            },
            _open: function(b, c, e) {
                function d(b) {
                    h.of =
                        b;
                    n.is(":hidden") || n.position(h)
                }
                var f, h = a.extend({}, this.options.position);
                if (e)
                    if (f = this._find(c)) f.tooltip.find(".ui-tooltip-content").html(e);
                    else {
                        c.is("[title]") && (b && "mouseover" === b.type ? c.attr("title", "") : c.removeAttr("title"));
                        f = this._tooltip(c);
                        var n = f.tooltip;
                        this._addDescribedBy(c, n.attr("id"));
                        n.find(".ui-tooltip-content").html(e);
                        this.liveRegion.children().hide();
                        e.clone && (e = e.clone(), e.removeAttr("id").find("[id]").removeAttr("id"));
                        a("\x3cdiv\x3e").html(e).appendTo(this.liveRegion);
                        this.options.track && b && /^mouse/.test(b.type) ? (this._on(this.document, {
                            mousemove: d
                        }), d(b)) : n.position(a.extend({
                            of: c
                        }, this.options.position));
                        n.hide();
                        this._show(n, this.options.show);
                        if (this.options.show && this.options.show.delay) var k = this.delayedShow = setInterval(function() {
                            n.is(":visible") && (d(h.of), clearInterval(k))
                        }, a.fx.interval);
                        this._trigger("open", b, {
                            tooltip: n
                        })
                    }
            },
            _registerCloseHandlers: function(b, c) {
                var e = {
                    keyup: function(b) {
                        b.keyCode === a.ui.keyCode.ESCAPE && (b = a.Event(b), b.currentTarget = c[0],
                            this.close(b, !0))
                    }
                };
                c[0] !== this.element[0] && (e.remove = function() {
                    this._removeTooltip(this._find(c).tooltip)
                });
                b && "mouseover" !== b.type || (e.mouseleave = "close");
                b && "focusin" !== b.type || (e.focusout = "close");
                this._on(!0, c, e)
            },
            close: function(b) {
                var c = this,
                    e = a(b ? b.currentTarget : this.element),
                    d = this._find(e);
                if (d) {
                    var f = d.tooltip;
                    d.closing || (clearInterval(this.delayedShow), e.data("ui-tooltip-title") && !e.attr("title") && e.attr("title", e.data("ui-tooltip-title")), this._removeDescribedBy(e), d.hiding = !0, f.stop(!0),
                        this._hide(f, this.options.hide, function() {
                            c._removeTooltip(a(this))
                        }), e.removeData("ui-tooltip-open"), this._off(e, "mouseleave focusout keyup"), e[0] !== this.element[0] && this._off(e, "remove"), this._off(this.document, "mousemove"), b && "mouseleave" === b.type && a.each(this.parents, function(b, e) {
                            a(e.element).attr("title", e.title);
                            delete c.parents[b]
                        }), d.closing = !0, this._trigger("close", b, {
                            tooltip: f
                        }), d.hiding || (d.closing = !1))
                } else e.removeData("ui-tooltip-open")
            },
            _tooltip: function(b) {
                var c = a("\x3cdiv\x3e").attr("role",
                        "tooltip").addClass("ui-tooltip ui-widget ui-corner-all ui-widget-content " + (this.options.tooltipClass || "")),
                    e = c.uniqueId().attr("id");
                a("\x3cdiv\x3e").addClass("ui-tooltip-content").appendTo(c);
                c.appendTo(this.document[0].body);
                return this.tooltips[e] = {
                    element: b,
                    tooltip: c
                }
            },
            _find: function(b) {
                return (b = b.data("ui-tooltip-id")) ? this.tooltips[b] : null
            },
            _removeTooltip: function(b) {
                b.remove();
                delete this.tooltips[b.attr("id")]
            },
            _destroy: function() {
                var b = this;
                a.each(this.tooltips, function(c, e) {
                    var d = a.Event("blur");
                    e = e.element;
                    d.target = d.currentTarget = e[0];
                    b.close(d, !0);
                    a("#" + c).remove();
                    e.data("ui-tooltip-title") && (e.attr("title") || e.attr("title", e.data("ui-tooltip-title")), e.removeData("ui-tooltip-title"))
                });
                this.liveRegion.remove()
            }
        })
    })
})(ChemDoodle.lib.jQuery);
(function(g) {
    g.fn.simpleColor = function(a) {
        var p = this,
            f = "990033 ff3366 cc0033 ff0033 ff9999 cc3366 ffccff cc6699 993366 660033 cc3399 ff99cc ff66cc ff99ff ff6699 cc0066 ff0066 ff3399 ff0099 ff33cc ff00cc ff66ff ff33ff ff00ff cc0099 990066 cc66cc cc33cc cc99ff cc66ff cc33ff 993399 cc00cc cc00ff 9900cc 990099 cc99cc 996699 663366 660099 9933cc 660066 9900ff 9933ff 9966cc 330033 663399 6633cc 6600cc 9966ff 330066 6600ff 6633ff ccccff 9999ff 9999cc 6666cc 6666ff 666699 333366 333399 330099 3300cc 3300ff 3333ff 3333cc 0066ff 0033ff 3366ff 3366cc 000066 000033 0000ff 000099 0033cc 0000cc 336699 0066cc 99ccff 6699ff 003366 6699cc 006699 3399cc 0099cc 66ccff 3399ff 003399 0099ff 33ccff 00ccff 99ffff 66ffff 33ffff 00ffff 00cccc 009999 669999 99cccc ccffff 33cccc 66cccc 339999 336666 006666 003333 00ffcc 33ffcc 33cc99 00cc99 66ffcc 99ffcc 00ff99 339966 006633 336633 669966 66cc66 99ff99 66ff66 339933 99cc99 66ff99 33ff99 33cc66 00cc66 66cc99 009966 009933 33ff66 00ff66 ccffcc ccff99 99ff66 99ff33 00ff33 33ff33 00cc33 33cc33 66ff33 00ff00 66cc33 006600 003300 009900 33ff00 66ff00 99ff00 66cc00 00cc00 33cc00 339900 99cc66 669933 99cc33 336600 669900 99cc00 ccff66 ccff33 ccff00 999900 cccc00 cccc33 333300 666600 999933 cccc66 666633 999966 cccc99 ffffcc ffff99 ffff66 ffff33 ffff00 ffcc00 ffcc66 ffcc33 cc9933 996600 cc9900 ff9900 cc6600 993300 cc6633 663300 ff9966 ff6633 ff9933 ff6600 cc3300 996633 330000 663333 996666 cc9999 993333 cc6666 ffcccc ff3333 cc3333 ff6666 660000 990000 cc0000 ff0000 ff3300 cc9966 ffcc99 ffffff cccccc 999999 666666 333333 000000 000000 000000 000000 000000 000000 000000 000000 000000".split(" ");
        a =
            g.extend({
                defaultColor: this.attr("defaultColor") || "#FFF",
                cellWidth: this.attr("cellWidth") || 10,
                cellHeight: this.attr("cellHeight") || 10,
                cellMargin: this.attr("cellMargin") || 1,
                boxWidth: this.attr("boxWidth") || "115px",
                boxHeight: this.attr("boxHeight") || "20px",
                columns: this.attr("columns") || 16,
                insert: this.attr("insert") || "after",
                colors: this.attr("colors") || f,
                displayColorCode: this.attr("displayColorCode") || !1,
                colorCodeAlign: this.attr("colorCodeAlign") || "center",
                colorCodeColor: this.attr("colorCodeColor") || "#FFF",
                onSelect: null,
                onCellEnter: null,
                onClose: null,
                livePreview: !1
            }, a || {});
        a.totalWidth = a.columns * (a.cellWidth + 2 * a.cellMargin);
        a.chooserCSS = g.extend({
            border: "1px solid #000",
            margin: "0 0 0 5px",
            width: a.totalWidth,
            height: a.totalHeight,
            top: 0,
            left: a.boxWidth,
            position: "absolute",
            "background-color": "#fff"
        }, a.chooserCSS || {});
        a.displayCSS = g.extend({
            "background-color": a.defaultColor,
            border: "1px solid #000",
            width: a.boxWidth,
            height: a.boxHeight,
            "line-height": a.boxHeight + "px",
            cursor: "pointer"
        }, a.displayCSS || {});
        this.hide(); -
        1 != navigator.userAgent.indexOf("MSIE") && (a.totalWidth += 2);
        a.totalHeight = Math.ceil(a.colors.length / a.columns) * (a.cellHeight + 2 * a.cellMargin);
        g.simpleColorOptions = a;
        this.each(function(f) {
            a = g.simpleColorOptions;
            f = g("\x3cdiv class\x3d'simpleColorContainer' /\x3e");
            f.css("position", "relative");
            var h = this.value && "" != this.value ? this.value : a.defaultColor,
                d = g("\x3cdiv class\x3d'simpleColorDisplay' /\x3e");
            d.css(g.extend(a.displayCSS, {
                "background-color": h
            }));
            d.data("color", h);
            f.append(d);
            a.displayColorCode &&
                (d.data("displayColorCode", !0), d.text(this.value), d.css({
                    color: a.colorCodeColor,
                    textAlign: a.colorCodeAlign
                }));
            d.bind("click", {
                input: this,
                container: f,
                displayBox: d
            }, function(f) {
                g("html").bind("click.simpleColorDisplay", function(h) {
                    g("html").unbind("click.simpleColorDisplay");
                    g(".simpleColorChooser").hide();
                    h = g(h.target);
                    if (!1 === h.is(".simpleColorCell") || !1 === g.contains(g(f.target).closest(".simpleColorContainer")[0], h[0])) d.css("background-color", d.data("color")), a.displayColorCode && d.text(d.data("color"));
                    if (a.onClose) a.onClose(p)
                });
                if (f.data.container.chooser) f.data.container.chooser.toggle();
                else {
                    var h = g("\x3cdiv class\x3d'simpleColorChooser'/\x3e");
                    h.css(a.chooserCSS);
                    f.data.container.chooser = h;
                    f.data.container.append(h);
                    for (var l = 0; l < a.colors.length; l++) {
                        var m = g("\x3cdiv class\x3d'simpleColorCell' id\x3d'" + a.colors[l] + "'/\x3e");
                        m.css({
                            width: a.cellWidth + "px",
                            height: a.cellHeight + "px",
                            margin: a.cellMargin + "px",
                            cursor: "pointer",
                            lineHeight: a.cellHeight + "px",
                            fontSize: "1px",
                            "float": "left",
                            "background-color": "#" +
                                a.colors[l]
                        });
                        h.append(m);
                        (a.onCellEnter || a.livePreview) && m.bind("mouseenter", function(f) {
                            if (a.onCellEnter) a.onCellEnter(this.id, p);
                            a.livePreview && (d.css("background-color", "#" + this.id), a.displayColorCode && d.text("#" + this.id))
                        });
                        m.bind("click", {
                            input: f.data.input,
                            chooser: h,
                            displayBox: d
                        }, function(d) {
                            var f = "#" + this.id;
                            d.data.input.value = f;
                            g(d.data.input).change();
                            g(d.data.displayBox).data("color", f);
                            d.data.displayBox.css("background-color", f);
                            d.data.chooser.hide();
                            a.displayColorCode && d.data.displayBox.text(f);
                            if (a.onSelect) a.onSelect(f, p)
                        })
                    }
                }
            });
            g(this).after(f);
            g(this).data("container", f)
        });
        g(".simpleColorDisplay").each(function() {
            g(this).click(function(a) {
                a.stopPropagation()
            })
        });
        return this
    };
    g.fn.closeChooser = function() {
        this.each(function(a) {
            g(this).data("container").find(".simpleColorChooser").hide()
        });
        return this
    };
    g.fn.setColor = function(a) {
        this.each(function(p) {
            p = g(this).data("container").find(".simpleColorDisplay");
            p.css("background-color", a).data("color", a);
            !0 === p.data("displayColorCode") && p.text(a)
        });
        return this
    }
})(ChemDoodle.lib.jQuery);
(function(g) {
    function a(a, f) {
        if (!(1 < a.originalEvent.touches.length)) {
            a.preventDefault();
            var d = a.originalEvent.changedTouches[0],
                h = document.createEvent("MouseEvents");
            h.initMouseEvent(f, !0, !0, window, 1, d.screenX, d.screenY, d.clientX, d.clientY, !1, !1, !1, !1, 0, null);
            a.target.dispatchEvent(h)
        }
    }
    g.support.touch = "ontouchend" in document;
    if (g.support.touch) {
        var p = g.ui.mouse.prototype,
            f = p._mouseInit,
            m = p._mouseDestroy,
            h;
        p._touchStart = function(d) {
            !h && this._mouseCapture(d.originalEvent.changedTouches[0]) && (h = !0, this._touchMoved = !1, a(d, "mouseover"), a(d, "mousemove"), a(d, "mousedown"), this.psave = {
                x: d.originalEvent.changedTouches ? d.originalEvent.changedTouches[0].pageX : d.pageX,
                y: d.originalEvent.changedTouches ? d.originalEvent.changedTouches[0].pageY : d.pageY
            })
        };
        p._touchMove = function(d) {
            var f = d.pageX,
                g = d.pageY;
            d.originalEvent.changedTouches && (f = d.originalEvent.changedTouches[0].pageX, g = d.originalEvent.changedTouches[0].pageY);
            4 > f - this.psave.x && 4 > g - this.psave.y || !h || (this._touchMoved = !0, a(d, "mousemove"))
        };
        p._touchEnd = function(d) {
            this.psave =
                void 0;
            h && (a(d, "mouseup"), a(d, "mouseout"), this._touchMoved || a(d, "click"), h = !1)
        };
        p._mouseInit = function() {
            this.element.bind({
                touchstart: g.proxy(this, "_touchStart"),
                touchmove: g.proxy(this, "_touchMove"),
                touchend: g.proxy(this, "_touchEnd")
            });
            f.call(this)
        };
        p._mouseDestroy = function() {
            this.element.unbind({
                touchstart: g.proxy(this, "_touchStart"),
                touchmove: g.proxy(this, "_touchMove"),
                touchend: g.proxy(this, "_touchEnd")
            });
            m.call(this)
        }
    }
})(ChemDoodle.lib.jQuery);
ChemDoodle.uis = function(g, a, p) {
    g.INFO.v_jQuery_ui = a.ui.version;
    g = {
        actions: {},
        gui: {}
    };
    g.gui.desktop = {};
    g.gui.mobile = {};
    g.states = {};
    g.tools = {};
    return g
}(ChemDoodle.iChemLabs, ChemDoodle.lib.jQuery);
(function(g, a) {
    g._Action = function() {};
    g = g._Action.prototype;
    g.forward = function(a) {
        this.innerForward();
        this.checks(a)
    };
    g.reverse = function(a) {
        this.innerReverse();
        this.checks(a)
    };
    g.checks = function(a) {
        if (a) {
            for (let f = 0, g = a.molecules.length; f < g; f++) a.molecules[f].check();
            a.lasso && a.lasso.isActive() && a.lasso.setBounds();
            a.checksOnAction();
            a.repaint()
        }
    }
})(ChemDoodle.uis.actions);
(function(g, a, p, f) {
    p.AddAction = function(a, f, d, l) {
        this.sketcher = a;
        this.a = f;
        this.as = d;
        this.bs = l
    };
    p = p.AddAction.prototype = new p._Action;
    p.innerForward = function() {
        let f = this.sketcher.getMoleculeByAtom(this.a);
        f || (f = new a.Molecule, this.sketcher.molecules.push(f));
        if (this.as)
            for (let a = 0, d = this.as.length; a < d; a++) f.atoms.push(this.as[a]);
        if (this.bs) {
            let a = [];
            for (let l = 0, g = this.bs.length; l < g; l++) {
                var h = this.bs[l];
                if (-1 === f.atoms.indexOf(h.a1)) {
                    var d = this.sketcher.getMoleculeByAtom(h.a1); - 1 === a.indexOf(d) &&
                        a.push(d)
                } - 1 === f.atoms.indexOf(h.a2) && (d = this.sketcher.getMoleculeByAtom(h.a2), -1 === a.indexOf(d) && a.push(d));
                f.bonds.push(h)
            }
            for (let d = 0, l = a.length; d < l; d++) h = a[d], this.sketcher.removeMolecule(h), f.atoms = f.atoms.concat(h.atoms), f.bonds = f.bonds.concat(h.bonds)
        }
    };
    p.innerReverse = function() {
        let a = this.sketcher.getMoleculeByAtom(this.a);
        if (this.as) {
            var f = [];
            for (let d = 0, h = a.atoms.length; d < h; d++) - 1 === this.as.indexOf(a.atoms[d]) && f.push(a.atoms[d]);
            a.atoms = f
        }
        if (this.bs) {
            f = [];
            for (let d = 0, h = a.bonds.length; d <
                h; d++) - 1 === this.bs.indexOf(a.bonds[d]) && f.push(a.bonds[d]);
            a.bonds = f
        }
        if (0 === a.atoms.length) this.sketcher.removeMolecule(a);
        else if (f = (new g.Splitter).split(a), 1 < f.length) {
            this.sketcher.removeMolecule(a);
            for (let a = 0, h = f.length; a < h; a++) this.sketcher.molecules.push(f[a])
        }
    }
})(ChemDoodle.informatics, ChemDoodle.structures, ChemDoodle.uis.actions);
(function(g, a) {
    g.AddContentAction = function(a, f, g) {
        this.sketcher = a;
        this.mols = f;
        this.shapes = g
    };
    g = g.AddContentAction.prototype = new g._Action;
    g.innerForward = function() {
        this.sketcher.molecules = this.sketcher.molecules.concat(this.mols);
        this.sketcher.shapes = this.sketcher.shapes.concat(this.shapes)
    };
    g.innerReverse = function() {
        for (let a = 0, f = this.mols.length; a < f; a++) this.sketcher.removeMolecule(this.mols[a]);
        for (let a = 0, f = this.shapes.length; a < f; a++) this.sketcher.removeShape(this.shapes[a])
    }
})(ChemDoodle.uis.actions);
(function(g, a) {
    g.AddShapeAction = function(a, f) {
        this.sketcher = a;
        this.s = f
    };
    g = g.AddShapeAction.prototype = new g._Action;
    g.innerForward = function() {
        this.sketcher.shapes.push(this.s)
    };
    g.innerReverse = function() {
        this.sketcher.removeShape(this.s)
    }
})(ChemDoodle.uis.actions);
(function(g, a) {
    g.AddVAPAttachementAction = function(a, f, g) {
        this.vap = a;
        this.a = f;
        this.substituent = g
    };
    g = g.AddVAPAttachementAction.prototype = new g._Action;
    g.innerForward = function() {
        this.substituent ? this.vap.substituent = this.a : this.vap.attachments.push(this.a)
    };
    g.innerReverse = function() {
        this.substituent ? this.vap.substituent = a : this.vap.attachments.pop()
    }
})(ChemDoodle.uis.actions);
(function(g, a, p, f) {
    g.ChangeBondAction = function(g, h, d) {
        g && (this.b = g, this.orderBefore = g.bondOrder, this.stereoBefore = g.stereo, h === f ? (this.orderAfter = p.floor(g.bondOrder + 1), 3 < this.orderAfter && (this.orderAfter = 1), this.stereoAfter = a.STEREO_NONE) : (this.orderAfter = h, this.stereoAfter = d))
    };
    g = g.ChangeBondAction.prototype = new g._Action;
    g.innerForward = function() {
        this.b.bondOrder = this.orderAfter;
        this.b.stereo = this.stereoAfter
    };
    g.innerReverse = function() {
        this.b.bondOrder = this.orderBefore;
        this.b.stereo = this.stereoBefore
    }
})(ChemDoodle.uis.actions,
    ChemDoodle.structures.Bond, Math);
(function(g, a, p) {
    g.ChangeRepeatUnitAttributeAction = function(a, g) {
        this.s = a;
        this.type = g
    };
    g = g.ChangeRepeatUnitAttributeAction.prototype = new g._Action;
    g.innerForward = function() {
        let f = 0 < this.type ? 1 : -1;
        switch (a.abs(this.type)) {
            case 1:
                this.s.n1 += f;
                break;
            case 2:
                this.s.n2 += f
        }
    };
    g.innerReverse = function() {
        let f = 0 < this.type ? -1 : 1;
        switch (a.abs(this.type)) {
            case 1:
                this.s.n1 += f;
                break;
            case 2:
                this.s.n2 += f
        }
    }
})(ChemDoodle.uis.actions, Math);
(function(g, a, p) {
    g.ChangeBracketAttributeAction = function(a, g) {
        this.s = a;
        this.type = g
    };
    g = g.ChangeBracketAttributeAction.prototype = new g._Action;
    g.innerForward = function() {
        let f = 0 < this.type ? 1 : -1;
        switch (a.abs(this.type)) {
            case 1:
                this.s.charge += f;
                break;
            case 2:
                this.s.repeat += f;
                break;
            case 3:
                this.s.mult += f
        }
    };
    g.innerReverse = function() {
        let f = 0 < this.type ? -1 : 1;
        switch (a.abs(this.type)) {
            case 1:
                this.s.charge += f;
                break;
            case 2:
                this.s.repeat += f;
                break;
            case 3:
                this.s.mult += f
        }
    }
})(ChemDoodle.uis.actions, Math);
(function(g, a) {
    g.ChangeChargeAction = function(a, f) {
        this.a = a;
        this.delta = f
    };
    g = g.ChangeChargeAction.prototype = new g._Action;
    g.innerForward = function() {
        this.a.charge += this.delta
    };
    g.innerReverse = function() {
        this.a.charge -= this.delta
    }
})(ChemDoodle.uis.actions);
(function(g, a) {
    g.ChangeCoordinatesAction = function(a, f) {
        this.as = a;
        this.recs = [];
        for (let a = 0, h = this.as.length; a < h; a++) this.recs[a] = {
            xo: this.as[a].x,
            yo: this.as[a].y,
            xn: f[a].x,
            yn: f[a].y
        }
    };
    g = g.ChangeCoordinatesAction.prototype = new g._Action;
    g.innerForward = function() {
        for (let a = 0, f = this.as.length; a < f; a++) this.as[a].x = this.recs[a].xn, this.as[a].y = this.recs[a].yn
    };
    g.innerReverse = function() {
        for (let a = 0, f = this.as.length; a < f; a++) this.as[a].x = this.recs[a].xo, this.as[a].y = this.recs[a].yo
    }
})(ChemDoodle.uis.actions);
(function(g, a) {
    g.ChangeLabelAction = function(a, f) {
        this.a = a;
        this.before = a.label;
        this.after = f
    };
    g = g.ChangeLabelAction.prototype = new g._Action;
    g.innerForward = function() {
        this.a.label = this.after
    };
    g.innerReverse = function() {
        this.a.label = this.before
    }
})(ChemDoodle.uis.actions);
(function(g, a) {
    g.ChangeLonePairAction = function(a, f) {
        this.a = a;
        this.delta = f
    };
    g = g.ChangeLonePairAction.prototype = new g._Action;
    g.innerForward = function() {
        this.a.numLonePair += this.delta
    };
    g.innerReverse = function() {
        this.a.numLonePair -= this.delta
    }
})(ChemDoodle.uis.actions);
(function(g, a) {
    g.ChangeQueryAction = function(a, f) {
        this.o = a;
        this.before = a.query;
        this.after = f
    };
    g = g.ChangeQueryAction.prototype = new g._Action;
    g.innerForward = function() {
        this.o.query = this.after
    };
    g.innerReverse = function() {
        this.o.query = this.before
    }
})(ChemDoodle.uis.actions);
(function(g, a) {
    g.ChangeRadicalAction = function(a, f) {
        this.a = a;
        this.delta = f
    };
    g = g.ChangeRadicalAction.prototype = new g._Action;
    g.innerForward = function() {
        this.a.numRadical += this.delta
    };
    g.innerReverse = function() {
        this.a.numRadical -= this.delta
    }
})(ChemDoodle.uis.actions);
(function(g, a) {
    g.ChangeIsotopeAction = function(a, f) {
        this.a = a;
        this.old = a.mass;
        this.val = f
    };
    g = g.ChangeIsotopeAction.prototype = new g._Action;
    g.innerForward = function() {
        this.a.mass = this.val
    };
    g.innerReverse = function() {
        this.a.mass = this.old
    }
})(ChemDoodle.uis.actions);
(function(g, a, p, f) {
    g.ChangeVAPOrderAction = function(a, f) {
        this.vap = a;
        this.orderBefore = a.bondType;
        this.orderAfter = f
    };
    g = g.ChangeVAPOrderAction.prototype = new g._Action;
    g.innerForward = function() {
        this.vap.bondType = this.orderAfter
    };
    g.innerReverse = function() {
        this.vap.bondType = this.orderBefore
    }
})(ChemDoodle.uis.actions, ChemDoodle.structures.Bond, Math);
(function(g, a, p, f) {
    g.ChangeVAPSubstituentAction = function(a, f) {
        this.vap = a;
        this.nsub = f;
        this.orderBefore = a.bondType;
        this.osub = a.substituent
    };
    g = g.ChangeVAPSubstituentAction.prototype = new g._Action;
    g.innerForward = function() {
        this.vap.bondType = 1;
        this.vap.substituent = this.nsub;
        this.vap.attachments.splice(this.vap.attachments.indexOf(this.nsub), 1);
        this.osub && this.vap.attachments.push(this.osub)
    };
    g.innerReverse = function() {
        this.vap.bondType = this.orderBefore;
        (this.vap.substituent = this.osub) && this.vap.attachments.pop();
        this.vap.attachments.push(this.nsub)
    }
})(ChemDoodle.uis.actions, ChemDoodle.structures.Bond, Math);
(function(g, a, p) {
    a.ClearAction = function(a) {
        this.sketcher = a;
        this.beforeMols = this.sketcher.molecules;
        this.beforeShapes = this.sketcher.shapes;
        this.sketcher.clear();
        this.sketcher.oneMolecule && !this.sketcher.setupScene && (this.afterMol = new g.Molecule, this.afterMol.atoms.push(new g.Atom), this.sketcher.molecules.push(this.afterMol), this.sketcher.center(), this.sketcher.repaint())
    };
    a = a.ClearAction.prototype = new a._Action;
    a.innerForward = function() {
        this.sketcher.molecules = [];
        this.sketcher.shapes = [];
        this.sketcher.oneMolecule &&
            !this.sketcher.setupScene && this.sketcher.molecules.push(this.afterMol)
    };
    a.innerReverse = function() {
        this.sketcher.molecules = this.beforeMols;
        this.sketcher.shapes = this.beforeShapes
    }
})(ChemDoodle.structures, ChemDoodle.uis.actions);
(function(g, a) {
    g.DeleteAction = function(a, f, g, h) {
        this.sketcher = a;
        this.a = f;
        this.as = g;
        this.bs = h;
        this.ss = []
    };
    a = g.DeleteAction.prototype = new g._Action;
    a.innerForwardAReverse = g.AddAction.prototype.innerReverse;
    a.innerReverseAForward = g.AddAction.prototype.innerForward;
    a.innerForward = function() {
        this.innerForwardAReverse();
        for (let a = 0, f = this.ss.length; a < f; a++) this.sketcher.removeShape(this.ss[a])
    };
    a.innerReverse = function() {
        this.innerReverseAForward();
        0 < this.ss.length && (this.sketcher.shapes = this.sketcher.shapes.concat(this.ss))
    }
})(ChemDoodle.uis.actions);
(function(g, a, p) {
    a.DeleteContentAction = function(a, g, h) {
        this.sketcher = a;
        this.as = g;
        this.ss = h;
        this.bs = [];
        for (let d = 0, f = this.sketcher.molecules.length; d < f; d++) {
            a = this.sketcher.molecules[d];
            for (let d = 0, f = a.bonds.length; d < f; d++) g = a.bonds[d], (g.a1.isLassoed || g.a2.isLassoed) && this.bs.push(g)
        }
    };
    a = a.DeleteContentAction.prototype = new a._Action;
    a.innerForward = function() {
        for (let a = 0, f = this.ss.length; a < f; a++) this.sketcher.removeShape(this.ss[a]);
        let a = [],
            m = [];
        for (let d = 0, f = this.sketcher.molecules.length; d < f; d++) {
            let f =
                this.sketcher.molecules[d];
            for (let d = 0, g = f.atoms.length; d < g; d++) {
                var h = f.atoms[d]; - 1 === this.as.indexOf(h) && a.push(h)
            }
            for (let a = 0, d = f.bonds.length; a < d; a++) h = f.bonds[a], -1 === this.bs.indexOf(h) && m.push(h)
        }
        this.sketcher.molecules = (new g.Splitter).split({
            atoms: a,
            bonds: m
        })
    };
    a.innerReverse = function() {
        this.sketcher.shapes = this.sketcher.shapes.concat(this.ss);
        let a = [],
            m = [];
        for (let f = 0, d = this.sketcher.molecules.length; f < d; f++) {
            let d = this.sketcher.molecules[f];
            a = a.concat(d.atoms);
            m = m.concat(d.bonds)
        }
        this.sketcher.molecules =
            (new g.Splitter).split({
                atoms: a.concat(this.as),
                bonds: m.concat(this.bs)
            })
    }
})(ChemDoodle.informatics, ChemDoodle.uis.actions);
(function(g, a) {
    g.DeleteShapeAction = function(a, f) {
        this.sketcher = a;
        this.s = f
    };
    a = g.DeleteShapeAction.prototype = new g._Action;
    a.innerForward = g.AddShapeAction.prototype.innerReverse;
    a.innerReverse = g.AddShapeAction.prototype.innerForward
})(ChemDoodle.uis.actions);
(function(g, a) {
    g.DeleteVAPConnectionAction = function(a, f) {
        this.vap = a;
        this.connection = f;
        this.substituent = a.substituent === f
    };
    g = g.DeleteVAPConnectionAction.prototype = new g._Action;
    g.innerForward = function() {
        this.substituent ? this.vap.substituent = a : this.vap.attachments.splice(this.vap.attachments.indexOf(this.connection), 1)
    };
    g.innerReverse = function() {
        this.substituent ? this.vap.substituent = this.connection : this.vap.attachments.push(this.connection)
    }
})(ChemDoodle.uis.actions);
(function(g, a, p, f) {
    a.FlipAction = function(a, f, d) {
        this.ps = a;
        this.bs = f;
        f = a = Infinity;
        let h = -Infinity,
            m = -Infinity;
        for (let d = 0, g = this.ps.length; d < g; d++) a = p.min(this.ps[d].x, a), f = p.min(this.ps[d].y, f), h = p.max(this.ps[d].x, h), m = p.max(this.ps[d].y, m);
        this.center = new g.Point((h + a) / 2, (m + f) / 2);
        this.horizontal = d
    };
    a = a.FlipAction.prototype = new a._Action;
    a.innerForward = a.innerReverse = function() {
        for (let f = 0, d = this.ps.length; f < d; f++) {
            var a = this.ps[f];
            this.horizontal ? a.x += 2 * (this.center.x - a.x) : a.y += 2 * (this.center.y -
                a.y)
        }
        for (let f = 0, d = this.bs.length; f < d; f++) a = this.bs[f], a.stereo === g.Bond.STEREO_PROTRUDING ? a.stereo = g.Bond.STEREO_RECESSED : a.stereo === g.Bond.STEREO_RECESSED && (a.stereo = g.Bond.STEREO_PROTRUDING)
    }
})(ChemDoodle.structures, ChemDoodle.uis.actions, Math);
(function(g, a) {
    g.FlipBondAction = function(a) {
        this.b = a
    };
    g = g.FlipBondAction.prototype = new g._Action;
    g.innerForward = function() {
        let a = this.b.a1;
        this.b.a1 = this.b.a2;
        this.b.a2 = a
    };
    g.innerReverse = function() {
        this.innerForward()
    }
})(ChemDoodle.uis.actions);
(function(g, a) {
    g.FlipRepeatUnitAction = function(a) {
        this.b = a
    };
    g = g.FlipRepeatUnitAction.prototype = new g._Action;
    g.innerReverse = g.innerForward = function() {
        this.b.flip = !this.b.flip
    }
})(ChemDoodle.uis.actions);
(function(g, a) {
    g.MoveAction = function(a, f) {
        this.ps = a;
        this.dif = f
    };
    g = g.MoveAction.prototype = new g._Action;
    g.innerForward = function() {
        for (let a = 0, f = this.ps.length; a < f; a++) this.ps[a].add(this.dif)
    };
    g.innerReverse = function() {
        for (let a = 0, f = this.ps.length; a < f; a++) this.ps[a].sub(this.dif)
    }
})(ChemDoodle.uis.actions);
(function(g, a, p) {
    a.NewMoleculeAction = function(a, g, h) {
        this.sketcher = a;
        this.as = g;
        this.bs = h
    };
    a = a.NewMoleculeAction.prototype = new a._Action;
    a.innerForward = function() {
        let a = new g.Molecule;
        a.atoms = a.atoms.concat(this.as);
        a.bonds = a.bonds.concat(this.bs);
        a.check();
        this.sketcher.addMolecule(a)
    };
    a.innerReverse = function() {
        this.sketcher.removeMolecule(this.sketcher.getMoleculeByAtom(this.as[0]))
    }
})(ChemDoodle.structures, ChemDoodle.uis.actions);
(function(g, a, p) {
    g.RotateAction = function(a, g, h) {
        this.ps = a;
        this.dif = g;
        this.center = h
    };
    g = g.RotateAction.prototype = new g._Action;
    g.innerForward = function() {
        for (let f = 0, g = this.ps.length; f < g; f++) {
            let h = this.ps[f],
                d = this.center.distance(h),
                g = this.center.angle(h) + this.dif;
            h.x = this.center.x + d * a.cos(g);
            h.y = this.center.y - d * a.sin(g)
        }
    };
    g.innerReverse = function() {
        for (let f = 0, g = this.ps.length; f < g; f++) {
            let h = this.ps[f],
                d = this.center.distance(h),
                g = this.center.angle(h) - this.dif;
            h.x = this.center.x + d * a.cos(g);
            h.y = this.center.y -
                d * a.sin(g)
        }
    }
})(ChemDoodle.uis.actions, Math);
(function(g, a) {
    g.SwitchContentAction = function(a, f, g) {
        this.sketcher = a;
        this.beforeMols = this.sketcher.molecules;
        this.beforeShapes = this.sketcher.shapes;
        this.molsA = f;
        this.shapesA = g
    };
    g = g.SwitchContentAction.prototype = new g._Action;
    g.innerForward = function() {
        this.sketcher.loadContent(this.molsA, this.shapesA)
    };
    g.innerReverse = function() {
        this.sketcher.molecules = this.beforeMols;
        this.sketcher.shapes = this.beforeShapes
    }
})(ChemDoodle.uis.actions);
(function(g, a) {
    g.SwitchMoleculeAction = function(a, f) {
        this.sketcher = a;
        this.beforeMols = this.sketcher.molecules;
        this.beforeShapes = this.sketcher.shapes;
        this.molA = f
    };
    g = g.SwitchMoleculeAction.prototype = new g._Action;
    g.innerForward = function() {
        this.sketcher.loadMolecule(this.molA)
    };
    g.innerReverse = function() {
        this.sketcher.molecules = this.beforeMols;
        this.sketcher.shapes = this.beforeShapes
    }
})(ChemDoodle.uis.actions);
(function(g, a) {
    g.HistoryManager = function(a) {
        this.sketcher = a;
        this.undoStack = [];
        this.redoStack = []
    };
    g = g.HistoryManager.prototype;
    g.undo = function() {
        if (0 !== this.undoStack.length) {
            this.sketcher.lasso && this.sketcher.lasso.isActive() && this.sketcher.lasso.empty();
            let a = this.undoStack.pop();
            a.reverse(this.sketcher);
            this.redoStack.push(a);
            0 === this.undoStack.length && this.sketcher.toolbarManager.buttonUndo.disable();
            this.sketcher.toolbarManager.buttonRedo.enable()
        }
    };
    g.redo = function() {
        if (0 !== this.redoStack.length) {
            this.sketcher.lasso &&
                this.sketcher.lasso.isActive() && this.sketcher.lasso.empty();
            let a = this.redoStack.pop();
            a.forward(this.sketcher);
            this.undoStack.push(a);
            this.sketcher.toolbarManager.buttonUndo.enable();
            0 === this.redoStack.length && this.sketcher.toolbarManager.buttonRedo.disable()
        }
    };
    g.pushUndo = function(a) {
        a.forward(this.sketcher);
        this.undoStack.push(a);
        0 !== this.redoStack.length && (this.redoStack = []);
        this.sketcher.toolbarManager.buttonUndo.enable();
        this.sketcher.toolbarManager.buttonRedo.disable()
    };
    g.clear = function() {
        0 !==
            this.undoStack.length && (this.undoStack = [], this.sketcher.toolbarManager.buttonUndo.disable());
        0 !== this.redoStack.length && (this.redoStack = [], this.sketcher.toolbarManager.buttonRedo.disable())
    }
})(ChemDoodle.uis.actions);
(function(g, a, p, f, m, h, d, l, t, q, r) {
    f._State = function() {};
    q = f._State.prototype;
    q.setup = function(a) {
        this.sketcher = a
    };
    q.clearHover = function() {
        this.sketcher.hovering && (this.sketcher.hovering.isHover = !1, this.sketcher.hovering.isSelected = !1, this.sketcher.hovering = r)
    };
    q.findHoveredObject = function(a, l, e, q) {
        this.clearHover();
        var n = Infinity;
        let m, b = 10;
        this.sketcher.isMobile || (b /= this.sketcher.styles.scale);
        if (l)
            for (let e = 0, d = this.sketcher.molecules.length; e < d; e++) {
                l = this.sketcher.molecules[e];
                for (let e = 0, d = l.atoms.length; e <
                    d; e++) {
                    var c = l.atoms[e];
                    c.isHover = !1;
                    let d = a.p.distance(c);
                    d < b && d < n && (n = d, m = c)
                }
            }
        if (e)
            for (let d = 0, f = this.sketcher.molecules.length; d < f; d++) {
                e = this.sketcher.molecules[d];
                for (let d = 0, f = e.bonds.length; d < f; d++) l = e.bonds[d], l.isHover = !1, c = g.distanceFromPointToLineInclusive(a.p, l.a1, l.a2, b / 2), -1 !== c && c < b && c < n && (n = c, m = l)
            }
        if (q) {
            for (let k = 0, g = this.sketcher.shapes.length; k < g; k++)
                if (q = this.sketcher.shapes[k], q.isHover = !1, q.hoverPoint = r, !(this instanceof f.RepeatUnitState) || q instanceof d.RepeatUnit && q.contents.flippable) {
                    e =
                        q.getPoints();
                    for (let d = 0, f = e.length; d < f; d++) l = e[d], c = a.p.distance(l), c < b && c < n && (n = c, m = q, q.hoverPoint = l);
                    if (this instanceof f.EraseState && q instanceof d.VAP) {
                        q.hoverBond = r;
                        q.substituent && (e = q.substituent, l = a.p.distance(new h.Point((q.asterisk.x + e.x) / 2, (q.asterisk.y + e.y) / 2)), l < b && l < n && (n = l, q.hoverBond = e, m = q));
                        for (let c = 0, d = q.attachments.length; c < d; c++) e = q.attachments[c], l = a.p.distance(new h.Point((q.asterisk.x + e.x) / 2, (q.asterisk.y + e.y) / 2)), l < b && l < n && (n = l, q.hoverBond = e, m = q)
                    }
                } if (!m)
                for (let c = 0, e = this.sketcher.shapes.length; c <
                    e; c++) n = this.sketcher.shapes[c], n.isOver(a.p, b) && (m = n)
        }
        m && (m.isHover = !0, this.sketcher.hovering = m)
    };
    q.getOptimumAngle = function(a, d) {
        let e = this.sketcher.getMoleculeByAtom(a),
            f = e.getAngles(a),
            h = 0;
        if (0 === f.length) h = t.PI / 6;
        else if (1 === f.length) {
            let n;
            for (let b = 0, c = e.bonds.length; b < c; b++) e.bonds[b].contains(this.sketcher.hovering) && (n = e.bonds[b]);
            3 <= n.bondOrder || 3 <= d ? h = f[0] + t.PI : (a = f[0] % t.PI * 2, h = g.isBetween(a, 0, t.PI / 2) || g.isBetween(a, t.PI, 3 * t.PI / 2) ? f[0] + 2 * t.PI / 3 : f[0] - 2 * t.PI / 3)
        } else {
            let n;
            for (let b = 0, c =
                    e.rings.length; b < c; b++) d = e.rings[b], -1 !== d.atoms.indexOf(a) && (f.push(a.angle(d.getCenter())), n = !0);
            n && f.sort(function(b, c) {
                return b - c
            });
            h = g.angleBetweenLargest(f).angle
        }
        return h
    };
    q.removeStartAtom = function() {
        this.sketcher.startAtom && (this.sketcher.startAtom.x = -10, this.sketcher.startAtom.y = -10, this.sketcher.repaint())
    };
    q.placeRequiredAtom = function(a) {
        let d = new h.Atom("C", a.p.x, a.p.y);
        this.sketcher.hovering = d;
        this.sketcher.hovering.isHover = !0;
        this.sketcher.historyManager.pushUndo(new p.NewMoleculeAction(this.sketcher,
            [d], []));
        this.innermousedown(a)
    };
    q.enter = function() {
        this.sketcher.cursorManager.setCursor(m.CursorManager.CROSSHAIR);
        this.innerenter && this.innerenter()
    };
    q.exit = function() {
        this.innerexit && this.innerexit()
    };
    q.click = function(a) {
        this.innerclick && this.innerclick(a)
    };
    q.rightclick = function(a) {
        this.innerrightclick && this.innerrightclick(a)
    };
    q.dblclick = function(a) {
        this.innerdblclick && this.innerdblclick(a);
        !this.sketcher.hovering && this.sketcher.oneMolecule && this.sketcher.toolbarManager.buttonCenter.func()
    };
    q.mousedown = function(a) {
        this.sketcher.lastPoint = a.p;
        this.sketcher.isHelp || this.sketcher.isMobile && 10 > a.op.distance(new h.Point(this.sketcher.width - 20, 20)) ? (this.sketcher.isHelp = !1, this.sketcher.lastPoint = r, this.sketcher.repaint(), location.href = "https://web.chemdoodle.com/demos/2d-sketcher") : this.innermousedown && this.innermousedown(a)
    };
    q.rightmousedown = function(a) {
        this.innerrightmousedown && this.innerrightmousedown(a)
    };
    q.mousemove = function(a) {
        this.sketcher.lastMousePos = a.p;
        this.innermousemove && this.innermousemove(a);
        this.sketcher.isHelp ? this.sketcher.cursorManager.setCursor(m.CursorManager.POINTER) : this.sketcher.cursorManager.getCurrentCursor() === m.CursorManager.POINTER && this.sketcher.cursorManager.setPreviousCursor();
        this.sketcher.repaint()
    };
    q.mouseout = function(d) {
        this.sketcher.lastMousePos = r;
        this.innermouseout && this.innermouseout(d);
        this.sketcher.isHelp && (this.sketcher.isHelp = !1, this.sketcher.repaint());
        this.sketcher.hovering && a.CANVAS_DRAGGING != this.sketcher && (this.sketcher.hovering = r, this.sketcher.repaint())
    };
    q.mouseover = function(a) {
        this.innermouseover && this.innermouseover(a)
    };
    q.mouseup = function(a) {
        this.parentAction = r;
        this.innermouseup && this.innermouseup(a)
    };
    q.rightmouseup = function(a) {
        this.innerrightmouseup && this.innerrightmouseup(a)
    };
    q.mousewheel = function(a, d) {
        this.innermousewheel && this.innermousewheel(a);
        this.sketcher.styles.scale += d / 50;
        this.sketcher.checkScale();
        this.sketcher.repaint()
    };
    q.drag = function(d) {
        this.innerdrag && this.innerdrag(d);
        if (!this.sketcher.hovering && !this.dontTranslateOnDrag) {
            if (a.SHIFT)
                if (this.parentAction) {
                    var f =
                        this.parentAction.center,
                        e = f.angle(this.sketcher.lastPoint);
                    e = f.angle(d.p) - e;
                    this.parentAction.dif += e;
                    for (let a = 0, d = this.parentAction.ps.length; a < d; a++) {
                        let d = this.parentAction.ps[a],
                            b = f.distance(d),
                            c = f.angle(d) + e;
                        d.x = f.x + b * t.cos(c);
                        d.y = f.y - b * t.sin(c)
                    }
                    for (let e = 0, a = this.sketcher.molecules.length; e < a; e++) this.sketcher.molecules[e].check()
                } else f = new h.Point(this.sketcher.width / 2, this.sketcher.height / 2), e = f.angle(this.sketcher.lastPoint), e = f.angle(d.p) - e, this.parentAction = new p.RotateAction(this.sketcher.getAllPoints(),
                    e, f), this.sketcher.historyManager.pushUndo(this.parentAction);
            else {
                if (!this.sketcher.lastPoint) return;
                f = new h.Point(d.p.x, d.p.y);
                f.sub(this.sketcher.lastPoint);
                if (this.parentAction) {
                    this.parentAction.dif.add(f);
                    for (let e = 0, a = this.parentAction.ps.length; e < a; e++) this.parentAction.ps[e].add(f);
                    this.sketcher.lasso && this.sketcher.lasso.isActive() && (this.sketcher.lasso.bounds.minX += f.x, this.sketcher.lasso.bounds.maxX += f.x, this.sketcher.lasso.bounds.minY += f.y, this.sketcher.lasso.bounds.maxY += f.y);
                    for (let e =
                            0, a = this.sketcher.molecules.length; e < a; e++) this.sketcher.molecules[e].check()
                } else this.parentAction = new p.MoveAction(this.sketcher.getAllPoints(), f), this.sketcher.historyManager.pushUndo(this.parentAction)
            }
            this.sketcher.repaint()
        }
        this.sketcher.lastPoint = d.p
    };
    q.keydown = function(d) {
        if (a.CANVAS_DRAGGING === this.sketcher) this.sketcher.lastPoint && (d.p = new h.Point(this.sketcher.lastPoint.x, this.sketcher.lastPoint.y), this.drag(d));
        else if (a.META) 90 === d.which ? this.sketcher.historyManager.undo() : 89 === d.which ?
            this.sketcher.historyManager.redo() : 83 === d.which ? this.sketcher.toolbarManager.buttonOpen.func() : 78 === d.which ? this.sketcher.toolbarManager.buttonClear.func() : 187 === d.which || 61 === d.which ? this.sketcher.toolbarManager.buttonScalePlus.func() : 189 === d.which || 109 === d.which ? this.sketcher.toolbarManager.buttonScaleMinus.func() : 65 === d.which ? this.sketcher.oneMolecule || (this.sketcher.toolbarManager.buttonLasso.select(), this.sketcher.toolbarManager.buttonLasso.getElement().click(),
                this.sketcher.lasso.select(this.sketcher.getAllAtoms(), this.sketcher.shapes)) : 88 === d.which ? this.sketcher.copyPasteManager.copy(!0) : 67 === d.which ? this.sketcher.copyPasteManager.copy(!1) : 86 === d.which && this.sketcher.copyPasteManager.paste();
        else if (9 === d.which) this.sketcher.oneMolecule || (this.sketcher.lasso.block = !0, this.sketcher.toolbarManager.buttonLasso.select(), this.sketcher.toolbarManager.buttonLasso.getElement().click(), this.sketcher.lasso.block = !1, a.SHIFT ? this.sketcher.lasso.selectNextShape() :
            this.sketcher.lasso.selectNextMolecule());
        else if (32 === d.which) this.sketcher.lasso && this.sketcher.lasso.empty(), this.sketcher.hovering instanceof h.Atom ? m.TextInput && this.sketcher.stateManager.STATE_TEXT_INPUT.innerclick(d) : this.sketcher.stateManager.getCurrentState() === this.sketcher.stateManager.STATE_LASSO && (this.sketcher.floatDrawTools ? (this.sketcher.toolbarManager.buttonBond.getLabelElement().click(), this.sketcher.toolbarManager.buttonBond.getElement().click()) : this.sketcher.toolbarManager.buttonSingle.getElement().click());
        else if (13 === d.which) this.sketcher.hovering instanceof h.Atom && this.sketcher.stateManager.STATE_TEXT_INPUT.lastLabel && this.sketcher.stateManager.STATE_TEXT_INPUT.lastLabel !== this.sketcher.hovering.label && this.sketcher.historyManager.pushUndo(new p.ChangeLabelAction(this.sketcher.hovering, this.sketcher.stateManager.STATE_TEXT_INPUT.lastLabel));
        else if (37 <= d.which && 40 >= d.which) {
            var f = new h.Point;
            switch (d.which) {
                case 37:
                    f.x = -10;
                    break;
                case 38:
                    f.y = -10;
                    break;
                case 39:
                    f.x = 10;
                    break;
                case 40:
                    f.y = 10
            }
            this.sketcher.historyManager.pushUndo(new p.MoveAction(this.sketcher.lasso &&
                this.sketcher.lasso.isActive() ? this.sketcher.lasso.getAllPoints() : this.sketcher.getAllPoints(), f))
        } else if (187 === d.which || 189 === d.which || 61 === d.which || 109 === d.which) this.sketcher.hovering && this.sketcher.hovering instanceof h.Atom && this.sketcher.historyManager.pushUndo(new p.ChangeChargeAction(this.sketcher.hovering, 187 === d.which || 61 === d.which ? 1 : -1));
        else if (8 === d.which || 46 === d.which) this.sketcher.stateManager.STATE_ERASE.handleDelete();
        else if (48 <= d.which && 57 >= d.which) {
            if (this.sketcher.hovering) {
                var e =
                    d.which - 48,
                    n = [],
                    q = [];
                if (this.sketcher.hovering instanceof h.Atom)
                    if (f = this.sketcher.hovering, a.SHIFT) {
                        if (2 < e && 9 > e) {
                            var r = this.sketcher.getMoleculeByAtom(this.sketcher.hovering),
                                b = r.getAngles(this.sketcher.hovering),
                                c = 3 * t.PI / 2;
                            0 !== b.length && (c = g.angleBetweenLargest(b).angle);
                            e = this.sketcher.stateManager.STATE_NEW_RING.getRing(this.sketcher.hovering, e, this.sketcher.styles.bondLength_2D, c, !1); - 1 === r.atoms.indexOf(e[0]) && n.push(e[0]);
                            this.sketcher.bondExists(this.sketcher.hovering, e[0]) || q.push(new h.Bond(this.sketcher.hovering,
                                e[0]));
                            for (let b = 1, c = e.length; b < c; b++) - 1 === r.atoms.indexOf(e[b]) && n.push(e[b]), this.sketcher.bondExists(e[b - 1], e[b]) || q.push(new h.Bond(e[b - 1], e[b]));
                            this.sketcher.bondExists(e[e.length - 1], this.sketcher.hovering) || q.push(new h.Bond(e[e.length - 1], this.sketcher.hovering))
                        }
                    } else {
                        0 === e && (e = 10);
                        b = new h.Point(this.sketcher.hovering.x, this.sketcher.hovering.y);
                        c = this.getOptimumAngle(this.sketcher.hovering);
                        let a = this.sketcher.hovering;
                        for (let d = 0; d < e; d++) {
                            var k = c + (1 === d % 2 ? t.PI / 3 : 0);
                            b.x += this.sketcher.styles.bondLength_2D *
                                t.cos(k);
                            b.y -= this.sketcher.styles.bondLength_2D * t.sin(k);
                            k = new h.Atom("C", b.x, b.y);
                            let e = Infinity;
                            for (let b = 0, c = this.sketcher.molecules.length; b < c; b++) {
                                let c = this.sketcher.molecules[b];
                                for (let b = 0, a = c.atoms.length; b < a; b++) {
                                    let a = c.atoms[b],
                                        d = a.distance(k);
                                    d < e && (e = d, r = a)
                                }
                            }
                            5 > e ? k = r : n.push(k);
                            this.sketcher.bondExists(a, k) || q.push(new h.Bond(a, k));
                            a = k
                        }
                    }
                else if (this.sketcher.hovering instanceof h.Bond)
                    if (f = this.sketcher.hovering.a1, a.SHIFT) {
                        if (2 < e && 9 > e) {
                            e = this.sketcher.stateManager.STATE_NEW_RING.getOptimalRing(this.sketcher.hovering,
                                e);
                            r = this.sketcher.hovering.a2;
                            b = this.sketcher.hovering.a1;
                            c = this.sketcher.getMoleculeByAtom(r);
                            e[0] === this.sketcher.hovering.a1 && (r = this.sketcher.hovering.a1, b = this.sketcher.hovering.a2); - 1 === c.atoms.indexOf(e[1]) && n.push(e[1]);
                            this.sketcher.bondExists(r, e[1]) || q.push(new h.Bond(r, e[1]));
                            for (let b = 2, a = e.length; b < a; b++) - 1 === c.atoms.indexOf(e[b]) && n.push(e[b]), this.sketcher.bondExists(e[b - 1], e[b]) || q.push(new h.Bond(e[b - 1], e[b]));
                            this.sketcher.bondExists(e[e.length - 1], b) || q.push(new h.Bond(e[e.length -
                                1], b))
                        }
                    } else if (0 < e && 4 > e && this.sketcher.hovering.bondOrder !== e) this.sketcher.historyManager.pushUndo(new p.ChangeBondAction(this.sketcher.hovering, e, h.Bond.STEREO_NONE));
                else if (7 === e || 8 === e) r = h.Bond.STEREO_RECESSED, 7 === e && (r = h.Bond.STEREO_PROTRUDING), this.sketcher.historyManager.pushUndo(new p.ChangeBondAction(this.sketcher.hovering, 1, r));
                0 === n.length && 0 === q.length || this.sketcher.historyManager.pushUndo(new p.AddAction(this.sketcher, f, n, q))
            }
        } else if (65 <= d.which && 90 >= d.which && this.sketcher.hovering)
            if (this.sketcher.hovering instanceof h.Atom) {
                f = String.fromCharCode(d.which);
                e = !1;
                for (let b = 0, c = l.length; b < c; b++)
                    if (this.sketcher.hovering.label.charAt(0) === f) l[b] === this.sketcher.hovering.label ? e = !0 : l[b].charAt(0) === f && (e && !q ? q = l[b] : n || (n = l[b]));
                    else if (l[b].charAt(0) === f) {
                    n = l[b];
                    break
                }
                f = "C";
                q ? f = q : n && (f = n);
                f !== this.sketcher.hovering.label && this.sketcher.historyManager.pushUndo(new p.ChangeLabelAction(this.sketcher.hovering, f))
            } else this.sketcher.hovering instanceof h.Bond && 70 === d.which && this.sketcher.historyManager.pushUndo(new p.FlipBondAction(this.sketcher.hovering));
        this.innerkeydown && this.innerkeydown(d)
    };
    q.keypress = function(a) {
        this.innerkeypress && this.innerkeypress(a)
    };
    q.keyup = function(d) {
        a.CANVAS_DRAGGING === this.sketcher && this.sketcher.lastPoint && (d.p = new h.Point(this.sketcher.lastPoint.x, this.sketcher.lastPoint.y), this.sketcher.drag(d));
        this.innerkeyup && this.innerkeyup(d)
    }
})(ChemDoodle.math, ChemDoodle.monitor, ChemDoodle.uis.actions, ChemDoodle.uis.states, ChemDoodle.uis.gui.desktop, ChemDoodle.structures, ChemDoodle.structures.d2, ChemDoodle.SYMBOLS, Math, window);
(function(g, a, p) {
    a.ChargeState = function(a) {
        this.setup(a)
    };
    a = a.ChargeState.prototype = new a._State;
    a.delta = 1;
    a.innermouseup = function(a) {
        this.sketcher.hovering && this.sketcher.historyManager.pushUndo(new g.ChangeChargeAction(this.sketcher.hovering, this.delta))
    };
    a.innermousemove = function(a) {
        this.findHoveredObject(a, !0, !1)
    }
})(ChemDoodle.uis.actions, ChemDoodle.uis.states);
(function(g, a, p, f, m, h, d, l) {
    function t(a, f, h, g, e, l) {
        e && d.abs(e.t) === l && (a.fillStyle = f.colorHover, a.beginPath(), 0 < e.t ? (a.moveTo(h, g), a.lineTo(h + 4, g - 4), a.lineTo(h + 8, g)) : (a.moveTo(h, g + 4), a.lineTo(h + 4, g + 8), a.lineTo(h + 8, g + 4)), a.closePath(), a.fill());
        a.strokeStyle = "blue";
        a.beginPath();
        a.moveTo(h, g);
        a.lineTo(h + 4, g - 4);
        a.lineTo(h + 8, g);
        a.moveTo(h, g + 4);
        a.lineTo(h + 4, g + 8);
        a.lineTo(h + 8, g + 4);
        a.stroke()
    }
    h.RepeatUnitState = function(a) {
        this.setup(a);
        this.dontTranslateOnDrag = !0
    };
    h = h.RepeatUnitState.prototype = new h._State;
    h.superDoubleClick = h.dblclick;
    h.dblclick = function(a) {
        this.control || this.superDoubleClick(a)
    };
    h.innermousedown = function(a) {
        if (this.control) {
            a = !0;
            var f = 0 < this.control.t ? 1 : -1;
            switch (d.abs(this.control.t)) {
                case 1:
                    f = this.control.s.n1 + f;
                    if (0 > f || f > this.control.s.n2) a = !1;
                    break;
                case 2:
                    if (f = this.control.s.n2 + f, 20 < f || f < this.control.s.n1) a = !1
            }
            a && (this.sketcher.historyManager.pushUndo(new m.ChangeRepeatUnitAttributeAction(this.control.s, this.control.t)), this.sketcher.repaint())
        } else this.sketcher.hovering && this.start !==
            this.sketcher.hovering && this.sketcher.hovering instanceof p.Bond ? this.start || (this.start = this.sketcher.hovering) : (this.end = this.start = l, this.sketcher.repaint())
    };
    h.innerdrag = function(a) {
        this.control = l;
        this.start && (this.end = new p.Point(a.p.x, a.p.y), this.findHoveredObject(a, !1, !0), this.sketcher.repaint())
    };
    h.innermouseup = function(a) {
        if (this.start && this.sketcher.hovering && this.sketcher.hovering !== this.start) {
            a = !1;
            for (let h = 0, g = this.sketcher.shapes.length; h < g; h++) {
                let e = this.sketcher.shapes[h];
                if (e instanceof f.RepeatUnit && (e.b1 === this.start && e.b2 === this.sketcher.hovering || e.b2 === this.start && e.b1 === this.sketcher.hovering)) {
                    var d = e;
                    a = !0
                }
            }
            d ? (a && this.sketcher.historyManager.pushUndo(new m.DeleteShapeAction(this.sketcher, d)), this.end = this.start = l, this.sketcher.repaint()) : (d = new f.RepeatUnit(this.start, this.sketcher.hovering), this.end = this.start = l, this.sketcher.historyManager.pushUndo(new m.AddShapeAction(this.sketcher, d)))
        } else this.sketcher.hovering instanceof f.RepeatUnit && this.sketcher.historyManager.pushUndo(new m.FlipRepeatUnitAction(this.sketcher.hovering))
    };
    h.innermousemove = function(d) {
        this.control = l;
        if (this.start) this.end = new p.Point(d.p.x, d.p.y);
        else
            for (let h = 0, n = this.sketcher.shapes.length; h < n; h++) {
                let n = this.sketcher.shapes[h];
                if (n instanceof f.RepeatUnit && !n.error) {
                    let e = [];
                    e.push({
                        x: n.textPos.x - 1,
                        y: n.textPos.y + 6,
                        v: 1
                    });
                    e.push({
                        x: n.textPos.x + 13,
                        y: n.textPos.y + 6,
                        v: 2
                    });
                    for (let f = 0, h = e.length; f < h; f++) {
                        let h = e[f];
                        if (a.isBetween(d.p.x, h.x, h.x + 8) && a.isBetween(d.p.y, h.y - 4, h.y + 3)) {
                            this.control = {
                                s: n,
                                t: h.v
                            };
                            break
                        } else if (a.isBetween(d.p.x, h.x, h.x + 8) && a.isBetween(d.p.y,
                                h.y + 4 - 2, h.y + 8 + 3)) {
                            this.control = {
                                s: n,
                                t: -1 * h.v
                            };
                            break
                        }
                    }
                    if (this.control) break
                }
            }
        this.control ? this.clearHover() : (this.findHoveredObject(d, !1, !0, !0), this.sketcher.hovering && this.sketcher.hovering instanceof f._Shape && !(this.sketcher.hovering instanceof f.RepeatUnit) && this.clearHover());
        this.sketcher.repaint()
    };
    h.draw = function(a, d) {
        if (this.start && this.end) {
            a.strokeStyle = d.colorPreview;
            a.fillStyle = d.colorPreview;
            a.lineWidth = 1;
            d = this.start.getCenter();
            var h = this.end;
            this.sketcher.hovering && this.sketcher.hovering !==
                this.start && (h = this.sketcher.hovering.getCenter());
            a.beginPath();
            a.moveTo(d.x, d.y);
            a.lineTo(h.x, h.y);
            a.setLineDash([2]);
            a.stroke();
            a.setLineDash([])
        } else {
            a.lineWidth = 2;
            a.lineJoin = "miter";
            a.lineCap = "butt";
            for (let n = 0, e = this.sketcher.shapes.length; n < e; n++)
                if (h = this.sketcher.shapes[n], h instanceof f.RepeatUnit && !h.error) {
                    let e = this.control && this.control.s === h ? this.control : l;
                    t(a, d, h.textPos.x - 1, h.textPos.y + 6, e, 1);
                    t(a, d, h.textPos.x + 13, h.textPos.y + 6, e, 2)
                } this.sketcher.hovering && this.sketcher.hovering instanceof
            f.RepeatUnit && this.sketcher.hovering.contents.flippable && (h = this.sketcher.hovering, a.font = g.getFontString(d.text_font_size, d.text_font_families, d.text_font_bold, d.text_font_italic), a.fillStyle = d.colorPreview, a.textAlign = "left", a.textBaseline = "bottom", a.fillText("flip?", h.textPos.x + (h.error ? 0 : 20), h.textPos.y))
        }
    }
})(ChemDoodle.extensions, ChemDoodle.math, ChemDoodle.structures, ChemDoodle.structures.d2, ChemDoodle.uis.actions, ChemDoodle.uis.states, Math);
(function(g, a, p, f, m, h) {
    a.EraseState = function(a) {
        this.setup(a)
    };
    a = a.EraseState.prototype = new a._State;
    a.innerenter = function(a) {
        this.sketcher.cursorManager.setCursor(p.CursorManager.ERASER)
    };
    a.handleDelete = function() {
        if (this.sketcher.lasso && this.sketcher.lasso.isActive()) {
            var a = new g.DeleteContentAction(this.sketcher, this.sketcher.lasso.atoms, this.sketcher.lasso.shapes);
            this.sketcher.lasso.empty()
        } else if (this.sketcher.hovering) {
            if (this.sketcher.hovering instanceof f.Atom)
                if (this.sketcher.oneMolecule) {
                    a =
                        this.sketcher.molecules[0];
                    for (let e = 0, d = a.atoms.length; e < d; e++) a.atoms[e].visited = !1;
                    var l = [],
                        t = [];
                    this.sketcher.hovering.visited = !0;
                    for (let e = 0, d = a.bonds.length; e < d; e++) {
                        var q = a.bonds[e];
                        if (q.contains(this.sketcher.hovering)) {
                            var r = [],
                                n = [],
                                v = new f.Queue;
                            for (v.enqueue(q.getNeighbor(this.sketcher.hovering)); !v.isEmpty();)
                                if (q = v.dequeue(), !q.visited) {
                                    q.visited = !0;
                                    r.push(q);
                                    for (let e = 0, b = a.bonds.length; e < b; e++) {
                                        let b = a.bonds[e];
                                        b.contains(q) && !b.getNeighbor(q).visited && (v.enqueue(b.getNeighbor(q)),
                                            n.push(b))
                                    }
                                } l.push(r);
                            t.push(n)
                        }
                    }
                    r = n = -1;
                    for (let e = 0, a = l.length; e < a; e++) l[e].length > n && (r = e, n = l[e].length);
                    if (-1 < r) {
                        n = [];
                        v = [];
                        var e;
                        for (let d = 0, f = a.atoms.length; d < f; d++) q = a.atoms[d], -1 === l[r].indexOf(q) ? n.push(q) : e || (e = q);
                        for (let e = 0, d = a.bonds.length; e < d; e++) l = a.bonds[e], -1 === t[r].indexOf(l) && v.push(l);
                        a = new g.DeleteAction(this.sketcher, e, n, v)
                    } else a = new g.ClearAction(this.sketcher)
                } else e = this.sketcher.getMoleculeByAtom(this.sketcher.hovering), a = new g.DeleteAction(this.sketcher, e.atoms[0], [this.sketcher.hovering],
                    e.getBonds(this.sketcher.hovering));
            else if (this.sketcher.hovering instanceof f.Bond) {
                if (!this.sketcher.oneMolecule || this.sketcher.hovering.ring) a = new g.DeleteAction(this.sketcher, this.sketcher.hovering.a1, h, [this.sketcher.hovering])
            } else this.sketcher.hovering instanceof m._Shape && (e = this.sketcher.hovering, a = e.hoverBond ? new g.DeleteVAPConnectionAction(e, e.hoverBond) : new g.DeleteShapeAction(this.sketcher, e));
            this.sketcher.hovering.isHover = !1;
            this.sketcher.hovering = h;
            this.sketcher.repaint()
        }
        if (a) {
            this.sketcher.historyManager.pushUndo(a);
            for (e = this.sketcher.shapes.length - 1; 0 <= e; e--) {
                t = this.sketcher.shapes[e];
                if (t instanceof m.Pusher || t instanceof m.AtomMapping) {
                    r = l = !1;
                    for (let e = 0, a = this.sketcher.molecules.length; e < a; e++) {
                        n = this.sketcher.molecules[e];
                        for (let e = 0, b = n.atoms.length; e < b; e++) v = n.atoms[e], v === t.o1 ? l = !0 : v === t.o2 && (r = !0);
                        for (let e = 0, b = n.bonds.length; e < b; e++) v = n.bonds[e], v === t.o1 ? l = !0 : v === t.o2 && (r = !0)
                    }
                    l && r || (a.ss.push(t), this.sketcher.removeShape(t))
                }
                if (t instanceof m.RepeatUnit) {
                    r = l = !1;
                    for (let e = 0, a = this.sketcher.molecules.length; e <
                        a; e++) {
                        n = this.sketcher.molecules[e];
                        for (let e = 0, b = n.bonds.length; e < b; e++) v = n.bonds[e], v === t.b1 ? l = !0 : v === t.b2 && (r = !0)
                    }
                    l && r || (a.ss.push(t), this.sketcher.removeShape(t))
                }
                if (t instanceof m.VAP) {
                    l = !1;
                    for (let e = 0, a = this.sketcher.molecules.length; e < a; e++) {
                        r = this.sketcher.molecules[e];
                        for (let e = 0, b = r.atoms.length; e < b; e++) r.atoms[e].present = !0
                    }
                    t.substituent && !t.substituent.present && (l = !0);
                    if (!l)
                        for (let e = 0, a = t.attachments.length; e < a; e++)
                            if (!t.attachments[e].present) {
                                l = !0;
                                break
                            } for (let e = 0, a = this.sketcher.molecules.length; e <
                        a; e++) {
                        r = this.sketcher.molecules[e];
                        for (let e = 0, b = r.atoms.length; e < b; e++) r.atoms[e].present = h
                    }
                    l && (a.ss.push(t), this.sketcher.removeShape(t))
                }
            }
            this.sketcher.checksOnAction();
            this.sketcher.repaint()
        }
    };
    a.innermouseup = function(a) {
        this.handleDelete()
    };
    a.innermousemove = function(a) {
        this.findHoveredObject(a, !0, !0, !0)
    }
})(ChemDoodle.uis.actions, ChemDoodle.uis.states, ChemDoodle.uis.gui.desktop, ChemDoodle.structures, ChemDoodle.structures.d2);
(function(g, a, p) {
    a.IsotopeState = function(a) {
        this.setup(a)
    };
    g = a.IsotopeState.prototype = new a._State;
    g.innerclick = function(a) {
        this.sketcher.hovering && (this.sketcher.dialogManager.isotopePopup.populate(this.sketcher.hovering), this.sketcher.dialogManager.isotopePopup.show())
    };
    g.innermousemove = function(a) {
        this.findHoveredObject(a, !0, !1)
    }
})(ChemDoodle.uis.actions, ChemDoodle.uis.states);
(function(g, a, p, f, m, h) {
    f.LabelState = function(a) {
        this.setup(a)
    };
    f = f.LabelState.prototype = new f._State;
    f.label = "C";
    f.innermousedown = function(a) {
        this.downPoint = a.p;
        this.newMolAllowed = !0;
        this.sketcher.hovering && (this.sketcher.hovering.isHover = !1, this.sketcher.hovering.isSelected = !0, this.sketcher.repaint())
    };
    f.innermouseup = function(d) {
        this.downPoint = h;
        if (this.sketcher.hovering)
            if (this.sketcher.hovering.isSelected = !1, this.sketcher.tempAtom) {
                let d = new a.Bond(this.sketcher.hovering, this.sketcher.tempAtom);
                this.sketcher.historyManager.pushUndo(new p.AddAction(this.sketcher, d.a1, [d.a2], [d]));
                this.sketcher.tempAtom = h
            } else this.label !== this.sketcher.hovering.label && this.sketcher.historyManager.pushUndo(new p.ChangeLabelAction(this.sketcher.hovering, this.label));
        else !this.sketcher.oneMolecule && this.newMolAllowed && this.sketcher.historyManager.pushUndo(new p.NewMoleculeAction(this.sketcher, [new a.Atom(this.label, d.p.x, d.p.y)], []));
        this.sketcher.isMobile || this.mousemove(d)
    };
    f.innermousemove = function(a) {
        this.findHoveredObject(a,
            !0, !1)
    };
    f.innerdrag = function(d) {
        this.downPoint && 3 < this.downPoint.distance(d.p) && (this.newMolAllowed = !1);
        if (this.sketcher.hovering) {
            if (9 > this.sketcher.hovering.distance(d.p)) this.sketcher.tempAtom = h;
            else if (15 > d.p.distance(this.sketcher.hovering)) {
                d = this.getOptimumAngle(this.sketcher.hovering);
                var f = this.sketcher.hovering.x + this.sketcher.styles.bondLength_2D * m.cos(d);
                d = this.sketcher.hovering.y - this.sketcher.styles.bondLength_2D * m.sin(d);
                this.sketcher.tempAtom = new a.Atom(this.label, f, d, 0)
            } else g.ALT &&
                g.SHIFT ? this.sketcher.tempAtom = new a.Atom(this.label, d.p.x, d.p.y, 0) : (f = this.sketcher.hovering.angle(d.p), d = this.sketcher.hovering.distance(d.p), g.SHIFT || (d = this.sketcher.styles.bondLength_2D), g.ALT || (f = m.floor((f + m.PI / 12) / (m.PI / 6)) * m.PI / 6), this.sketcher.tempAtom = new a.Atom(this.label, this.sketcher.hovering.x + d * m.cos(f), this.sketcher.hovering.y - d * m.sin(f), 0));
            this.sketcher.repaint()
        }
    }
})(ChemDoodle.monitor, ChemDoodle.structures, ChemDoodle.uis.actions, ChemDoodle.uis.states, Math);
(function(g, a, p, f, m, h, d, l, t, q) {
    let r = q,
        n = !1;
    h.LassoState = function(a) {
        this.setup(a);
        this.dontTranslateOnDrag = !0
    };
    h = h.LassoState.prototype = new h._State;
    h.innerdrag = function(d) {
        this.inDrag = !0;
        if (this.sketcher.lasso.isActive() && r) {
            if (this.sketcher.lastPoint)
                if (1 === r) {
                    var e = new p.Point(d.p.x, d.p.y);
                    e.sub(this.sketcher.lastPoint);
                    if (this.parentAction) {
                        this.parentAction.dif.add(e);
                        for (let a = 0, d = this.parentAction.ps.length; a < d; a++) this.parentAction.ps[a].add(e);
                        this.parentAction.checks(this.sketcher)
                    } else this.parentAction =
                        new m.MoveAction(this.sketcher.lasso.getAllPoints(), e), this.sketcher.historyManager.pushUndo(this.parentAction)
                } else if (2 === r)
                if (this.parentAction) {
                    e = this.parentAction.center;
                    var h = e.angle(this.sketcher.lastPoint);
                    d = e.angle(d.p) - h;
                    this.parentAction.dif += d;
                    for (let a = 0, f = this.parentAction.ps.length; a < f; a++) {
                        h = this.parentAction.ps[a];
                        let b = e.distance(h),
                            c = e.angle(h) + d;
                        h.x = e.x + b * t.cos(c);
                        h.y = e.y - b * t.sin(c)
                    }
                    this.parentAction.checks(this.sketcher)
                } else e = new p.Point((this.sketcher.lasso.bounds.minX + this.sketcher.lasso.bounds.maxX) /
                    2, (this.sketcher.lasso.bounds.minY + this.sketcher.lasso.bounds.maxY) / 2), h = e.angle(this.sketcher.lastPoint), d = e.angle(d.p) - h, this.parentAction = new m.RotateAction(this.sketcher.lasso.getAllPoints(), d, e), this.sketcher.historyManager.pushUndo(this.parentAction)
        } else if (this.sketcher.hovering) {
            if (this.sketcher.lastPoint)
                if (d = new p.Point(d.p.x, d.p.y), d.sub(this.sketcher.lastPoint), this.parentAction) {
                    this.parentAction.dif.add(d);
                    for (let e = 0, a = this.parentAction.ps.length; e < a; e++) this.parentAction.ps[e].add(d);
                    this.parentAction.checks(this.sketcher)
                } else this.sketcher.hovering instanceof p.Atom ? e = a.SHIFT ? [this.sketcher.hovering] : this.sketcher.getMoleculeByAtom(this.sketcher.hovering).atoms : this.sketcher.hovering instanceof p.Bond ? e = [this.sketcher.hovering.a1, this.sketcher.hovering.a2] : this.sketcher.hovering instanceof f._Shape && (e = this.sketcher.hovering.hoverPoint ? [this.sketcher.hovering.hoverPoint] : this.sketcher.hovering.getPoints()), this.parentAction = new m.MoveAction(e, d), this.sketcher.historyManager.pushUndo(this.parentAction)
        } else this.sketcher.lasso.addPoint(d.p),
            this.sketcher.repaint()
    };
    h.innermousedown = function(d) {
        this.inDrag = !1;
        r = q;
        let e = this.sketcher.cursorManager.getCurrentCursor();
        if (this.sketcher.lasso.isActive() && !a.SHIFT) {
            let a = 25 / this.sketcher.styles.scale;
            g.isBetween(d.p.x, this.sketcher.lasso.bounds.minX, this.sketcher.lasso.bounds.maxX) && g.isBetween(d.p.y, this.sketcher.lasso.bounds.minY, this.sketcher.lasso.bounds.maxY) ? (r = 1, e = l.CursorManager.HAND_CLOSE) : g.isBetween(d.p.x, this.sketcher.lasso.bounds.minX - a, this.sketcher.lasso.bounds.maxX + a) && g.isBetween(d.p.y,
                this.sketcher.lasso.bounds.minY - a, this.sketcher.lasso.bounds.maxY + a) && (r = 2)
        } else this.sketcher.hovering ? e = l.CursorManager.HAND_CLOSE : (this.sketcher.lasso.addPoint(d.p), this.sketcher.repaint());
        this.sketcher.cursorManager.setCursor(e)
    };
    h.innermouseup = function(a) {
        r || this.sketcher.hovering || this.sketcher.lasso.select();
        this.innermousemove(a)
    };
    h.innerclick = function(a) {
        if (!r && !this.inDrag)
            if (this.sketcher.hovering) {
                a = [];
                let e = [];
                this.sketcher.hovering instanceof p.Atom ? a.push(this.sketcher.hovering) : this.sketcher.hovering instanceof
                p.Bond ? (a.push(this.sketcher.hovering.a1), a.push(this.sketcher.hovering.a2)) : this.sketcher.hovering instanceof f._Shape && e.push(this.sketcher.hovering);
                this.sketcher.lasso.select(a, e)
            } else this.sketcher.lasso.isActive() && this.sketcher.lasso.empty();
        r = q
    };
    h.innermousemove = function(f) {
        let e = l.CursorManager.CROSSHAIR;
        if (!this.sketcher.lasso.isActive()) {
            var h = this.sketcher.lasso.mode !== d.Lasso.MODE_LASSO_SHAPES;
            this.findHoveredObject(f, h, h, !0);
            this.sketcher.hovering && (e = l.CursorManager.HAND_OPEN)
        } else if (!a.SHIFT) {
            h = !1;
            let a = 25 / this.sketcher.styles.scale,
                d = g.isBetween(f.p.x, this.sketcher.lasso.bounds.minX, this.sketcher.lasso.bounds.maxX) && g.isBetween(f.p.y, this.sketcher.lasso.bounds.minY, this.sketcher.lasso.bounds.maxY);
            !d && g.isBetween(f.p.x, this.sketcher.lasso.bounds.minX - a, this.sketcher.lasso.bounds.maxX + a) && g.isBetween(f.p.y, this.sketcher.lasso.bounds.minY - a, this.sketcher.lasso.bounds.maxY + a) && (h = !0);
            h !== n && (n = h, this.sketcher.repaint());
            d ? e = l.CursorManager.HAND_OPEN : n && (e = l.CursorManager.ROTATE)
        }
        this.sketcher.cursorManager.setCursor(e)
    };
    h.innerdblclick = function(a) {
        this.sketcher.lasso.isActive() && this.sketcher.lasso.empty()
    };
    h.draw = function(a, e) {
        if (n && this.sketcher.lasso.bounds) {
            a.fillStyle = e.colorSelect;
            a.globalAlpha = .1;
            e = 25 / this.sketcher.styles.scale;
            let d = this.sketcher.lasso.bounds;
            a.beginPath();
            a.rect(d.minX - e, d.minY - e, d.maxX - d.minX + 2 * e, e);
            a.rect(d.minX - e, d.maxY, d.maxX - d.minX + 2 * e, e);
            a.rect(d.minX - e, d.minY, e, d.maxY - d.minY);
            a.rect(d.maxX, d.minY, e, d.maxY - d.minY);
            a.fill();
            a.globalAlpha = 1
        }
    }
})(ChemDoodle.math, ChemDoodle.monitor, ChemDoodle.structures,
    ChemDoodle.structures.d2, ChemDoodle.uis.actions, ChemDoodle.uis.states, ChemDoodle.uis.tools, ChemDoodle.uis.gui.desktop, Math);
(function(g, a, p) {
    a.LonePairState = function(a) {
        this.setup(a)
    };
    a = a.LonePairState.prototype = new a._State;
    a.delta = 1;
    a.innermouseup = function(a) {
        0 > this.delta && 1 > this.sketcher.hovering.numLonePair || this.sketcher.hovering && this.sketcher.historyManager.pushUndo(new g.ChangeLonePairAction(this.sketcher.hovering, this.delta))
    };
    a.innermousemove = function(a) {
        this.findHoveredObject(a, !0, !1)
    }
})(ChemDoodle.uis.actions, ChemDoodle.uis.states);
(function(g, a, p, f, m) {
    a.MoveState = function(a) {
        this.setup(a)
    };
    a = a.MoveState.prototype = new a._State;
    a.action = m;
    a.innerdrag = function(a) {
        if (this.sketcher.hovering)
            if (this.action) {
                var d = new f.Point(a.p.x, a.p.y);
                d.sub(this.sketcher.lastPoint);
                this.action.dif.add(d);
                for (let a = 0, f = this.action.ps.length; a < f; a++) this.action.ps[a].add(d);
                for (let a = 0, d = this.sketcher.molecules.length; a < d; a++) this.sketcher.molecules[a].check();
                this.sketcher.repaint()
            } else d = [], a = new f.Point(a.p.x, a.p.y), this.sketcher.hovering instanceof
        f.Atom ? (a.sub(this.sketcher.hovering), d[0] = this.sketcher.hovering) : this.sketcher.hovering instanceof f.Bond && (a.sub(this.sketcher.lastPoint), d[0] = this.sketcher.hovering.a1, d[1] = this.sketcher.hovering.a2), this.action = new g.MoveAction(d, a), this.sketcher.historyManager.pushUndo(this.action)
    };
    a.innermousemove = function(a) {
        this.findHoveredObject(a, !0, !0);
        this.sketcher.hovering ? this.sketcher.cursorManager.setCursor(p.CursorManager.HAND_OPEN) : this.sketcher.cursorManager.setCursor(p.CursorManager.CROSSHAIR)
    };
    a.innermousedown = function(a) {
        this.findHoveredObject(a, !0, !0);
        this.sketcher.hovering && this.sketcher.cursorManager.setCursor(p.CursorManager.HAND_CLOSE)
    };
    a.innermouseup = function(a) {
        this.action = m;
        this.sketcher.hovering ? this.sketcher.cursorManager.setCursor(p.CursorManager.HAND_OPEN) : this.sketcher.cursorManager.setCursor(p.CursorManager.CROSSHAIR)
    }
})(ChemDoodle.uis.actions, ChemDoodle.uis.states, ChemDoodle.uis.gui.desktop, ChemDoodle.structures);
(function(g, a, p, f, m, h) {
    p.NewBondState = function(a) {
        this.setup(a)
    };
    p = p.NewBondState.prototype = new p._State;
    p.bondOrder = 1;
    p.stereo = f.Bond.STEREO_NONE;
    p.incrementBondOrder = function(d) {
        this.newMolAllowed = !1;
        1 === this.bondOrder && this.stereo === f.Bond.STEREO_NONE ? this.sketcher.historyManager.pushUndo(new a.ChangeBondAction(d)) : d.bondOrder === this.bondOrder && d.stereo === this.stereo ? (1 >= d.bondOrder && d.stereo !== f.Bond.STEREO_NONE || 2 === d.bondOrder && d.stereo === f.Bond.STEREO_NONE) && this.sketcher.historyManager.pushUndo(new a.FlipBondAction(d)) :
            this.sketcher.historyManager.pushUndo(new a.ChangeBondAction(d, this.bondOrder, this.stereo))
    };
    p.innerexit = function() {
        this.removeStartAtom()
    };
    p.innerdrag = function(a) {
        this.newMolAllowed = !1;
        this.removeStartAtom();
        if (this.sketcher.hovering instanceof f.Atom) {
            if (15 > a.p.distance(this.sketcher.hovering)) {
                var d = this.getOptimumAngle(this.sketcher.hovering, this.bondOrder);
                a = this.sketcher.hovering.x + this.sketcher.styles.bondLength_2D * m.cos(d);
                d = this.sketcher.hovering.y - this.sketcher.styles.bondLength_2D * m.sin(d);
                this.sketcher.tempAtom = new f.Atom("C", a, d, 0)
            } else {
                let h = 1E3;
                for (let f = 0, g = this.sketcher.molecules.length; f < g; f++) {
                    let n = this.sketcher.molecules[f];
                    for (let f = 0, e = n.atoms.length; f < e; f++) {
                        let e = n.atoms[f],
                            g = e.distance(a.p);
                        5 > g && (!d || g < h) && (d = e, h = g)
                    }
                }
                d ? this.sketcher.tempAtom = new f.Atom("C", d.x, d.y, 0) : g.ALT && g.SHIFT ? this.sketcher.tempAtom = new f.Atom("C", a.p.x, a.p.y, 0) : (d = this.sketcher.hovering.angle(a.p), a = this.sketcher.hovering.distance(a.p), g.SHIFT || (a = this.sketcher.styles.bondLength_2D), g.ALT || (d = m.floor((d +
                    m.PI / 12) / (m.PI / 6)) * m.PI / 6), this.sketcher.tempAtom = new f.Atom("C", this.sketcher.hovering.x + a * m.cos(d), this.sketcher.hovering.y - a * m.sin(d), 0))
            }
            for (let f = 0, h = this.sketcher.molecules.length; f < h; f++) {
                a = this.sketcher.molecules[f];
                for (let f = 0, h = a.atoms.length; f < h; f++) d = a.atoms[f], 5 > d.distance(this.sketcher.tempAtom) && (this.sketcher.tempAtom.x = d.x, this.sketcher.tempAtom.y = d.y, this.sketcher.tempAtom.isOverlap = !0)
            }
            this.sketcher.repaint()
        }
    };
    p.innerclick = function(d) {
        this.sketcher.hovering || this.sketcher.oneMolecule ||
            !this.newMolAllowed || (this.sketcher.historyManager.pushUndo(new a.NewMoleculeAction(this.sketcher, [new f.Atom("C", d.p.x, d.p.y)], [])), this.sketcher.isMobile || this.mousemove(d), this.newMolAllowed = !1)
    };
    p.innermousedown = function(a) {
        this.newMolAllowed = !0;
        if (this.sketcher.hovering instanceof f.Atom) this.sketcher.hovering.isHover = !1, this.sketcher.hovering.isSelected = !0, this.drag(a);
        else if (this.sketcher.hovering instanceof f.Bond) {
            this.sketcher.hovering.isHover = !1;
            this.incrementBondOrder(this.sketcher.hovering);
            for (let a = 0, d = this.sketcher.molecules.length; a < d; a++) this.sketcher.molecules[a].check();
            this.sketcher.repaint()
        } else this.sketcher.hovering || this.sketcher.requireStartingAtom || this.placeRequiredAtom(a)
    };
    p.innermouseup = function(d) {
        if (this.sketcher.tempAtom && this.sketcher.hovering) {
            let d = [],
                h = [],
                l = !0;
            if (this.sketcher.tempAtom.isOverlap) {
                for (let a = 0, d = this.sketcher.molecules.length; a < d; a++) {
                    var g = this.sketcher.molecules[a];
                    for (let e = 0, a = g.atoms.length; e < a; e++) {
                        let a = g.atoms[e];
                        5 > a.distance(this.sketcher.tempAtom) &&
                            (this.sketcher.tempAtom = a)
                    }
                }
                if (g = this.sketcher.getBond(this.sketcher.hovering, this.sketcher.tempAtom)) this.incrementBondOrder(g), l = !1
            } else d.push(this.sketcher.tempAtom);
            l && (h[0] = new f.Bond(this.sketcher.hovering, this.sketcher.tempAtom, this.bondOrder), h[0].stereo = this.stereo, this.sketcher.historyManager.pushUndo(new a.AddAction(this.sketcher, h[0].a1, d, h)))
        }
        this.sketcher.tempAtom = h;
        this.sketcher.isMobile || this.mousemove(d)
    };
    p.innermousemove = function(a) {
        this.sketcher.tempAtom || (this.findHoveredObject(a,
            !0, !0), this.sketcher.startAtom && (this.sketcher.hovering ? (this.sketcher.startAtom.x = -10, this.sketcher.startAtom.y = -10) : (this.sketcher.startAtom.x = a.p.x, this.sketcher.startAtom.y = a.p.y)))
    };
    p.innermouseout = function(a) {
        this.removeStartAtom()
    }
})(ChemDoodle.monitor, ChemDoodle.uis.actions, ChemDoodle.uis.states, ChemDoodle.structures, Math);
(function(g, a, p, f, m, h, d) {
    f.NewChainState = function(a) {
        this.setup(a)
    };
    g = f.NewChainState.prototype = new f._State;
    g.getChain = function(d, f) {
        if (a.SHIFT) {
            var g = f.x - d.x,
                l = f.y - d.y;
            h.abs(g) > h.abs(l) ? (f.x = d.x + g, f.y = d.y) : (f.x = d.x, f.y = d.y + l)
        }
        g = [];
        var n = d;
        l = 2 * h.PI - d.angle(f);
        a.SHIFT || a.ALT || (l -= l % (h.PI / 24));
        var v = this.sketcher.styles.bondLength_2D;
        d = h.floor(d.distance(f) / (v * h.cos(h.PI / 6)));
        (f = 1 == h.round(l / (h.PI / 24)) % 2) && (l -= h.PI / 24);
        this.flipOverride && (f = !f);
        for (let e = 0; e < d; e++) {
            let a = h.PI / 6 * (f ? 1 : -1);
            1 == (e & 1) &&
                (a *= -1);
            let d = n.x + v * h.cos(l + a);
            n = n.y + v * h.sin(l + a);
            n = new m.Atom("C", d, n);
            g.push(n)
        }
        l = this.sketcher.getAllAtoms();
        for (let a = 0, d = l.length; a < d; a++) l[a].isOverlap = !1;
        for (let a = 0, d = g.length; a < d; a++) {
            v = Infinity;
            let e;
            for (let d = 0, b = l.length; d < b; d++) n = l[d].distance(g[a]), n < v && (v = n, e = l[d]);
            5 > v && (g[a] = e, e.isOverlap = !0)
        }
        return g
    };
    g.innerexit = function() {
        this.removeStartAtom()
    };
    g.innerdrag = function(a) {
        this.newMolAllowed = !1;
        this.removeStartAtom();
        this.sketcher.hovering && (this.sketcher.tempChain = this.getChain(this.sketcher.hovering,
            new m.Point(a.p.x, a.p.y)), this.sketcher.repaint())
    };
    g.innerclick = function(a) {
        this.sketcher.hovering || this.sketcher.oneMolecule || !this.newMolAllowed || (this.sketcher.historyManager.pushUndo(new p.NewMoleculeAction(this.sketcher, [new m.Atom("C", a.p.x, a.p.y)], [])), this.sketcher.isMobile || this.mousemove(a), this.newMolAllowed = !1)
    };
    g.innermousedown = function(a) {
        this.newMolAllowed = !0;
        this.sketcher.hovering ? (this.sketcher.hovering.isHover = !1, this.sketcher.hovering.isSelected = !0, this.drag(a)) : this.sketcher.requireStartingAtom ||
            this.placeRequiredAtom(a)
    };
    g.innermouseup = function(a) {
        if (this.sketcher.tempChain && this.sketcher.hovering && 0 !== this.sketcher.tempChain.length) {
            let a = [],
                d = [],
                f = this.sketcher.getAllAtoms();
            for (let h = 0, g = this.sketcher.tempChain.length; h < g; h++) - 1 === f.indexOf(this.sketcher.tempChain[h]) && a.push(this.sketcher.tempChain[h]), 0 == h || this.sketcher.bondExists(this.sketcher.tempChain[h - 1], this.sketcher.tempChain[h]) || d.push(new m.Bond(this.sketcher.tempChain[h - 1], this.sketcher.tempChain[h]));
            this.sketcher.bondExists(this.sketcher.tempChain[0],
                this.sketcher.hovering) || d.push(new m.Bond(this.sketcher.tempChain[0], this.sketcher.hovering));
            0 === a.length && 0 === d.length || this.sketcher.historyManager.pushUndo(new p.AddAction(this.sketcher, this.sketcher.hovering, a, d));
            for (let a = 0, d = f.length; a < d; a++) f[a].isOverlap = !1
        }
        this.sketcher.tempChain = d;
        this.sketcher.isMobile || this.mousemove(a)
    };
    g.innermousemove = function(a) {
        this.sketcher.tempAtom || (this.findHoveredObject(a, !0), this.sketcher.startAtom && (this.sketcher.hovering ? (this.sketcher.startAtom.x = -10,
            this.sketcher.startAtom.y = -10) : (this.sketcher.startAtom.x = a.p.x, this.sketcher.startAtom.y = a.p.y)))
    };
    g.innermouseout = function(a) {
        this.removeStartAtom()
    }
})(ChemDoodle.math, ChemDoodle.monitor, ChemDoodle.uis.actions, ChemDoodle.uis.states, ChemDoodle.structures, Math);
(function(g, a, p, f, m, h, d) {
    f.NewRingState = function(a) {
        this.setup(a)
    };
    f = f.NewRingState.prototype = new f._State;
    f.numSides = 6;
    f.unsaturated = !1;
    f.getRing = function(a, d, f, g, n) {
        let l = h.PI - 2 * h.PI / d;
        g += l / 2;
        let e = [];
        for (let n = 0; n < d - 1; n++) {
            let d = 0 === n ? new m.Atom("C", a.x, a.y) : new m.Atom("C", e[e.length - 1].x, e[e.length - 1].y);
            d.x += f * h.cos(g);
            d.y -= f * h.sin(g);
            e.push(d);
            g += h.PI + l
        }
        for (let e = 0, d = this.sketcher.molecules.length; e < d; e++) {
            a = this.sketcher.molecules[e];
            for (let e = 0, b = a.atoms.length; e < b; e++) a.atoms[e].isOverlap = !1
        }
        for (let h = 0, g = e.length; h < g; h++) {
            a = Infinity;
            let g;
            for (let b = 0, c = this.sketcher.molecules.length; b < c; b++) {
                d = this.sketcher.molecules[b];
                for (let b = 0, c = d.atoms.length; b < c; b++) f = d.atoms[b].distance(e[h]), f < a && (a = f, g = d.atoms[b])
            }
            5 > a && (e[h] = g, n && (g.isOverlap = !0))
        }
        return e
    };
    f.getOptimalRing = function(a, d) {
        var f = h.PI / 2 - h.PI / d,
            g = a.a1.distance(a.a2);
        let n = this.getRing(a.a1, d, g, a.a1.angle(a.a2) - f, !1);
        a = this.getRing(a.a2, d, g, a.a2.angle(a.a1) - f, !1);
        f = d = 0;
        for (let l = 1, e = n.length; l < e; l++)
            for (let e = 0, m = this.sketcher.molecules.length; e <
                m; e++) {
                g = this.sketcher.molecules[e];
                for (let e = 0, b = g.atoms.length; e < b; e++) {
                    let b = g.atoms[e].distance(n[l]),
                        k = g.atoms[e].distance(a[l]);
                    d += h.min(1E8, 1 / (b * b));
                    f += h.min(1E8, 1 / (k * k))
                }
            }
        return d < f ? n : a
    };
    f.innerexit = function() {
        this.removeStartAtom()
    };
    f.innerdrag = function(d) {
        function f(a, d, f) {
            var e = h.PI / a;
            f = f / 2 / h.sin(e);
            e = f * h.cos(e);
            return 1 == a % 2 ? e + f : d ? 2 * e : 2 * f
        }
        this.newMolAllowed = !1;
        this.removeStartAtom();
        if (this.sketcher.hovering instanceof m.Atom) {
            var l = 0,
                r = 0,
                n = this.numSides;
            if (-1 === n) {
                l = this.sketcher.hovering.angle(d.p);
                r = this.sketcher.styles.bondLength_2D;
                n = 3;
                for (d = this.sketcher.hovering.distance(d.p); d > f(n + 1, !1, r);) n++;
                a.ALT || (l = h.floor((l + h.PI / 12) / (h.PI / 6)) * h.PI / 6)
            } else 15 > d.p.distance(this.sketcher.hovering) ? (d = this.sketcher.getMoleculeByAtom(this.sketcher.hovering).getAngles(this.sketcher.hovering), l = 0 === d.length ? 3 * h.PI / 2 : g.angleBetweenLargest(d).angle, r = this.sketcher.styles.bondLength_2D) : (l = this.sketcher.hovering.angle(d.p), r = this.sketcher.hovering.distance(d.p), a.ALT && a.SHIFT || (a.SHIFT || (r = this.sketcher.styles.bondLength_2D),
                a.ALT || (l = h.floor((l + h.PI / 12) / (h.PI / 6)) * h.PI / 6)));
            this.sketcher.tempRing = this.getRing(this.sketcher.hovering, n, r, l, !0);
            this.sketcher.repaint()
        } else if (this.sketcher.hovering instanceof m.Bond) {
            n = g.distanceFromPointToLineInclusive(d.p, this.sketcher.hovering.a1, this.sketcher.hovering.a2);
            l = this.numSides;
            if (-1 === l) {
                l = 3;
                r = this.sketcher.hovering.getCenter().distance(d.p);
                for (var v = this.sketcher.hovering.a1.distance(this.sketcher.hovering.a2); r > f(l + 1, !0, v);) l++
            }
            if (-1 !== n && 7 >= n) l = this.getOptimalRing(this.sketcher.hovering,
                l);
            else {
                r = h.PI / 2 - h.PI / l;
                v = this.sketcher.hovering.a1.distance(this.sketcher.hovering.a2);
                n = this.getRing(this.sketcher.hovering.a1, l, v, this.sketcher.hovering.a1.angle(this.sketcher.hovering.a2) - r, !1);
                l = this.getRing(this.sketcher.hovering.a2, l, v, this.sketcher.hovering.a2.angle(this.sketcher.hovering.a1) - r, !1);
                r = new m.Point;
                v = new m.Point;
                for (let a = 1, d = n.length; a < d; a++) r.add(n[a]), v.add(l[a]);
                r.x /= n.length - 1;
                r.y /= n.length - 1;
                v.x /= l.length - 1;
                v.y /= l.length - 1;
                r = r.distance(d.p);
                d = v.distance(d.p);
                r < d && (l = n)
            }
            for (let a =
                    1, d = l.length; a < d; a++) - 1 !== this.sketcher.getAllAtoms().indexOf(l[a]) && (l[a].isOverlap = !0);
            this.sketcher.tempRing = l;
            this.sketcher.repaint()
        }
    };
    f.innerclick = function(a) {
        this.sketcher.hovering || this.sketcher.oneMolecule || !this.newMolAllowed || (this.sketcher.historyManager.pushUndo(new p.NewMoleculeAction(this.sketcher, [new m.Atom("C", a.p.x, a.p.y)], [])), this.sketcher.isMobile || this.mousemove(a), this.newMolAllowed = !1)
    };
    f.innermousedown = function(a) {
        this.newMolAllowed = !0;
        this.sketcher.hovering ? (this.sketcher.hovering.isHover = !1, this.sketcher.hovering.isSelected = !0, this.drag(a)) : this.sketcher.requireStartingAtom || this.placeRequiredAtom(a)
    };
    f.innermouseup = function(f) {
        if (this.sketcher.tempRing && this.sketcher.hovering) {
            let d = [],
                f = [],
                l = this.sketcher.getAllAtoms(),
                e = this.unsaturated || -1 === this.numSides && a.SHIFT;
            if (this.sketcher.hovering instanceof m.Atom) {
                -1 === l.indexOf(this.sketcher.tempRing[0]) && d.push(this.sketcher.tempRing[0]);
                this.sketcher.bondExists(this.sketcher.hovering, this.sketcher.tempRing[0]) || f.push(new m.Bond(this.sketcher.hovering,
                    this.sketcher.tempRing[0]));
                for (let a = 1, n = this.sketcher.tempRing.length; a < n; a++) {
                    var h = this.sketcher.tempRing[a],
                        g = this.sketcher.tempRing[a - 1]; - 1 === l.indexOf(h) && d.push(h);
                    this.sketcher.bondExists(g, h) || f.push(new m.Bond(g, h, e && 1 === a % 2 && 1 < h.getImplicitHydrogenCount() && 1 < g.getImplicitHydrogenCount() ? 2 : 1))
                }
                this.sketcher.bondExists(this.sketcher.tempRing[this.sketcher.tempRing.length - 1], this.sketcher.hovering) || f.push(new m.Bond(this.sketcher.tempRing[this.sketcher.tempRing.length - 1], this.sketcher.hovering,
                    e && 1 === this.sketcher.tempRing.length % 2 && 1 < this.sketcher.tempRing[this.sketcher.tempRing.length - 1].getImplicitHydrogenCount() && 1 < this.sketcher.hovering.getImplicitHydrogenCount() ? 2 : 1))
            } else if (this.sketcher.hovering instanceof m.Bond) {
                g = this.sketcher.hovering.a2;
                h = this.sketcher.hovering.a1;
                this.sketcher.tempRing[0] === this.sketcher.hovering.a1 && (g = this.sketcher.hovering.a1, h = this.sketcher.hovering.a2); - 1 === l.indexOf(this.sketcher.tempRing[1]) && d.push(this.sketcher.tempRing[1]);
                this.sketcher.bondExists(g,
                    this.sketcher.tempRing[1]) || f.push(new m.Bond(g, this.sketcher.tempRing[1]));
                for (let a = 2, h = this.sketcher.tempRing.length; a < h; a++) {
                    g = this.sketcher.tempRing[a];
                    let h = this.sketcher.tempRing[a - 1]; - 1 === l.indexOf(g) && d.push(g);
                    this.sketcher.bondExists(h, g) || f.push(new m.Bond(h, g, e && 0 === a % 2 && 1 < g.getImplicitHydrogenCount() && 1 < h.getImplicitHydrogenCount() ? 2 : 1))
                }
                this.sketcher.bondExists(this.sketcher.tempRing[this.sketcher.tempRing.length - 1], h) || f.push(new m.Bond(this.sketcher.tempRing[this.sketcher.tempRing.length -
                    1], h, e && 0 === this.sketcher.tempRing.length % 2 && 1 < this.sketcher.tempRing[this.sketcher.tempRing.length - 1].getImplicitHydrogenCount() && 1 < h.getImplicitHydrogenCount() ? 2 : 1))
            }
            0 === d.length && 0 === f.length || this.sketcher.historyManager.pushUndo(new p.AddAction(this.sketcher, f[0].a1, d, f));
            for (let a = 0, e = l.length; a < e; a++) l[a].isOverlap = !1
        }
        this.sketcher.tempRing = d;
        this.sketcher.isMobile || this.mousemove(f)
    };
    f.innermousemove = function(a) {
        this.sketcher.tempAtom || (this.findHoveredObject(a, !0, !0), this.sketcher.startAtom &&
            (this.sketcher.hovering ? (this.sketcher.startAtom.x = -10, this.sketcher.startAtom.y = -10) : (this.sketcher.startAtom.x = a.p.x, this.sketcher.startAtom.y = a.p.y)))
    };
    f.innermouseout = function(a) {
        this.removeStartAtom()
    }
})(ChemDoodle.math, ChemDoodle.monitor, ChemDoodle.uis.actions, ChemDoodle.uis.states, ChemDoodle.structures, Math);
(function(g, a, p, f, m, h, d, l) {
    let t = new m.JSONInterpreter;
    f.NewTemplateState = function(a) {
        this.setup(a);
        this.template = {
            a: [{
                    x: 270,
                    i: "a0",
                    y: 105
                }, {
                    x: 252.6795,
                    i: "a1",
                    y: 115
                }, {
                    x: 252.6795,
                    i: "a2",
                    y: 135
                }, {
                    x: 270,
                    i: "a3",
                    y: 145
                }, {
                    x: 287.3205,
                    i: "a4",
                    y: 135
                }, {
                    x: 287.3205,
                    i: "a5",
                    y: 115
                }, {
                    x: 270,
                    i: "a6",
                    y: 85
                }, {
                    x: 287.3205,
                    i: "a7",
                    y: 75
                }, {
                    x: 270,
                    i: "a8",
                    y: 165,
                    l: "O"
                }, {
                    x: 252.6795,
                    i: "a9",
                    y: 175
                }, {
                    x: 252.6795,
                    i: "a10",
                    y: 195
                }, {
                    x: 252.6795,
                    i: "a11",
                    y: 215
                }, {
                    x: 252.6795,
                    i: "a12",
                    y: 235,
                    l: "Si"
                }, {
                    x: 272.6795,
                    i: "a13",
                    y: 235
                }, {
                    x: 232.6795,
                    i: "a14",
                    y: 235
                },
                {
                    x: 252.6795,
                    i: "a15",
                    y: 255
                }
            ],
            b: [{
                b: 0,
                e: 1,
                i: "b0",
                o: 2
            }, {
                b: 1,
                e: 2,
                i: "b1"
            }, {
                b: 2,
                e: 3,
                i: "b2",
                o: 2
            }, {
                b: 3,
                e: 4,
                i: "b3"
            }, {
                b: 4,
                e: 5,
                i: "b4",
                o: 2
            }, {
                b: 5,
                e: 0,
                i: "b5"
            }, {
                b: 0,
                e: 6,
                i: "b6"
            }, {
                b: 6,
                e: 7,
                i: "b7",
                o: 2
            }, {
                b: 3,
                e: 8,
                i: "b8"
            }, {
                b: 8,
                e: 9,
                i: "b9"
            }, {
                b: 9,
                e: 10,
                i: "b10"
            }, {
                b: 10,
                e: 11,
                i: "b11",
                o: 3
            }, {
                b: 11,
                e: 12,
                i: "b12"
            }, {
                b: 12,
                e: 13,
                i: "b13"
            }, {
                b: 12,
                e: 14,
                i: "b14"
            }, {
                b: 12,
                e: 15,
                i: "b15"
            }]
        };
        this.attachPos = 0
    };
    f = f.NewTemplateState.prototype = new f._State;
    f.getTemplate = function(f) {
        var h = this.sketcher.hovering;
        let n = t.molFrom(this.template);
        n.scaleToAverageBondLength(this.sketcher.styles.bondLength_2D);
        let l = n.atoms[this.attachPos];
        var e = h.angle(f),
            m = !0;
        if (!a.ALT)
            if (15 > h.distance(f)) {
                var q = this.sketcher.getMoleculeByAtom(this.sketcher.hovering).getAngles(this.sketcher.hovering);
                0 === q.length ? (e = 0, m = !1) : e = 1 === q.length ? q[0] + d.PI : g.angleBetweenLargest(q).angle;
                var p = n.getAngles(l);
                e = 1 === p.length ? e - (p[0] + (1 === q.length ? d.PI / 3 : 0)) : e - (g.angleBetweenLargest(p).angle + d.PI)
            } else e = d.round(e / (d.PI / 6)) * d.PI / 6;
        q = h.x - l.x;
        p = h.y - l.y;
        for (let a = 0, e = n.atoms.length; a < e; a++) {
            var b = n.atoms[a];
            b.x += q;
            b.y += p
        }
        if (m)
            for (let b =
                    0, g = n.atoms.length; b < g; b++) m = n.atoms[b], q = m.angle(h) + e, p = l.distance(m), a.SHIFT && (p *= h.distance(f) / this.sketcher.styles.bondLength_2D), m.x = h.x - d.cos(q) * p, m.y = h.y + d.sin(q) * p;
        f = this.sketcher.getAllAtoms();
        h = this.sketcher.getAllBonds();
        for (let a = 0, d = f.length; a < d; a++) {
            e = f[a];
            e.isOverlap = !1;
            m = [];
            for (let b = 0, a = n.atoms.length; b < a; b++) 5 > e.distance(n.atoms[b]) && m.push(b);
            q = -1;
            for (let b = 0, a = m.length; b < a; b++)
                if (p = m[b], -1 === q || e.distance(n.atoms[p]) < e.distance(n.atoms[q])) q = p;
            if (-1 !== q) {
                m = n.atoms[q];
                n.atoms.splice(q,
                    1);
                if (e.x !== l.x || e.y !== l.y) e.isOverlap = !0;
                for (let a = 0, c = n.bonds.length; a < c; a++)
                    if (q = n.bonds[a], q.a1 === m ? (q.a1 = e, q.tmpreplace1 = !0) : q.a2 === m && (q.a2 = e, q.tmpreplace2 = !0), q.tmpreplace1 && q.tmpreplace2) {
                        p = !1;
                        for (let a = 0, e = h.length; a < e; a++)
                            if (b = h[a], q.a1 === b.a1 && q.a2 === b.a2 || q.a2 === b.a1 && q.a1 === b.a2) {
                                p = !0;
                                break
                            } p && (n.bonds.splice(a--, 1), c--)
                    }
            }
        }
        n.check();
        n.check(!0);
        return n
    };
    f.innerexit = function() {
        this.removeStartAtom()
    };
    f.innerdrag = function(a) {
        this.newMolAllowed = !1;
        this.removeStartAtom();
        this.sketcher.hovering &&
            (this.sketcher.tempTemplate = this.getTemplate(a.p), this.sketcher.repaint())
    };
    f.innerclick = function(a) {
        this.sketcher.hovering || this.sketcher.oneMolecule || !this.newMolAllowed || (this.sketcher.historyManager.pushUndo(new p.NewMoleculeAction(this.sketcher, [new h.Atom("C", a.p.x, a.p.y)], [])), this.sketcher.isMobile || this.mousemove(a), this.newMolAllowed = !1)
    };
    f.innermousedown = function(a) {
        this.newMolAllowed = !0;
        this.sketcher.hovering ? (this.sketcher.hovering.isHover = !1, this.sketcher.hovering.isSelected = !0, this.drag(a)) :
            this.sketcher.requireStartingAtom || this.placeRequiredAtom(a)
    };
    f.innermouseup = function(a) {
        if (this.sketcher.hovering && this.sketcher.tempTemplate) {
            0 !== this.sketcher.tempTemplate.atoms.length && this.sketcher.historyManager.pushUndo(new p.AddAction(this.sketcher, this.sketcher.hovering, this.sketcher.tempTemplate.atoms, this.sketcher.tempTemplate.bonds));
            let a = this.sketcher.getAllAtoms();
            for (let d = 0, f = a.length; d < f; d++) a[d].isOverlap = !1;
            this.sketcher.tempTemplate = l
        }
        this.sketcher.isMobile || this.mousemove(a)
    };
    f.innermousemove = function(a) {
        this.sketcher.tempAtom || (this.findHoveredObject(a, !0), this.sketcher.startAtom && (this.sketcher.hovering ? (this.sketcher.startAtom.x = -10, this.sketcher.startAtom.y = -10) : (this.sketcher.startAtom.x = a.p.x, this.sketcher.startAtom.y = a.p.y)))
    };
    f.innermouseout = function(a) {
        this.removeStartAtom()
    }
})(ChemDoodle.math, ChemDoodle.monitor, ChemDoodle.uis.actions, ChemDoodle.uis.states, ChemDoodle.io, ChemDoodle.structures, Math);
(function(g, a, p, f, m) {
    f.PusherState = function(a) {
        this.setup(a);
        this.dontTranslateOnDrag = !0
    };
    f = f.PusherState.prototype = new f._State;
    f.numElectron = 1;
    f.innermousedown = function(a) {
        this.sketcher.hovering && this.start !== this.sketcher.hovering ? this.start || (this.start = this.sketcher.hovering) : (this.end = this.start = m, this.sketcher.repaint())
    };
    f.innerdrag = function(a) {
        this.start && (this.end = new g.Point(a.p.x, a.p.y), this.findHoveredObject(a, !0, -10 != this.numElectron), this.sketcher.repaint())
    };
    f.innermouseup = function(f) {
        if (this.start &&
            this.sketcher.hovering && this.sketcher.hovering !== this.start) {
            f = !1;
            for (let h = 0, g = this.sketcher.shapes.length; h < g; h++) {
                let g = this.sketcher.shapes[h];
                if (g instanceof a.Pusher)
                    if (g.o1 === this.start && g.o2 === this.sketcher.hovering) var d = g;
                    else g.o2 === this.start && g.o1 === this.sketcher.hovering && (d = g, f = !0);
                else g instanceof a.AtomMapping && (g.o1 === this.start && g.o2 === this.sketcher.hovering || g.o2 === this.start && g.o1 === this.sketcher.hovering) && (d = g, f = !0)
            }
            d ? (f && this.sketcher.historyManager.pushUndo(new p.DeleteShapeAction(this.sketcher,
                d)), this.end = this.start = m, this.sketcher.repaint()) : (d = -10 == this.numElectron ? new a.AtomMapping(this.start, this.sketcher.hovering) : new a.Pusher(this.start, this.sketcher.hovering, this.numElectron), this.end = this.start = m, this.sketcher.historyManager.pushUndo(new p.AddShapeAction(this.sketcher, d)))
        }
    };
    f.innermousemove = function(a) {
        this.start && (this.end = new g.Point(a.p.x, a.p.y));
        this.findHoveredObject(a, !0, -10 != this.numElectron);
        this.sketcher.repaint()
    };
    f.draw = function(a, d) {
        if (this.start && this.end) {
            a.strokeStyle =
                d.colorPreview;
            a.fillStyle = d.colorPreview;
            a.lineWidth = 1;
            d = this.start instanceof g.Atom ? this.start : this.start.getCenter();
            let f = this.end;
            this.sketcher.hovering && this.sketcher.hovering !== this.start && (f = this.sketcher.hovering instanceof g.Atom ? this.sketcher.hovering : this.sketcher.hovering.getCenter());
            a.beginPath();
            a.moveTo(d.x, d.y);
            a.lineTo(f.x, f.y);
            a.setLineDash([2]);
            a.stroke();
            a.setLineDash([])
        }
    }
})(ChemDoodle.structures, ChemDoodle.structures.d2, ChemDoodle.uis.actions, ChemDoodle.uis.states);
(function(g, a, p, f, m) {
    a.QueryState = function(a) {
        this.setup(a)
    };
    g = a.QueryState.prototype = new a._State;
    g.innermouseup = function(a) {
        this.sketcher.hovering && (this.sketcher.hovering instanceof p.Atom ? (this.sketcher.dialogManager.atomQueryDialog.setAtom(this.sketcher.hovering), this.sketcher.dialogManager.atomQueryDialog.open()) : this.sketcher.hovering instanceof p.Bond && (this.sketcher.dialogManager.bondQueryDialog.setBond(this.sketcher.hovering), this.sketcher.dialogManager.bondQueryDialog.open()))
    };
    g.innermousemove =
        function(a) {
            this.findHoveredObject(a, !0, !0, !1)
        }
})(ChemDoodle.uis.actions, ChemDoodle.uis.states, ChemDoodle.structures, ChemDoodle.structures.d2);
(function(g, a, p) {
    a.RadicalState = function(a) {
        this.setup(a)
    };
    a = a.RadicalState.prototype = new a._State;
    a.delta = 1;
    a.innermouseup = function(a) {
        0 > this.delta && 1 > this.sketcher.hovering.numRadical || this.sketcher.hovering && this.sketcher.historyManager.pushUndo(new g.ChangeRadicalAction(this.sketcher.hovering, this.delta))
    };
    a.innermousemove = function(a) {
        this.findHoveredObject(a, !0, !1)
    }
})(ChemDoodle.uis.actions, ChemDoodle.uis.states);
(function(g, a, p, f, m, h, d, l) {
    function t(a, f, h, e, g, l) {
        g && d.abs(g.t) === l && (a.fillStyle = f.colorHover, a.beginPath(), 0 < g.t ? (a.moveTo(h, e), a.lineTo(h + 6, e - 6), a.lineTo(h + 12, e)) : (a.moveTo(h, e + 6), a.lineTo(h + 6, e + 12), a.lineTo(h + 12, e + 6)), a.closePath(), a.fill());
        a.strokeStyle = "blue";
        a.beginPath();
        a.moveTo(h, e);
        a.lineTo(h + 6, e - 6);
        a.lineTo(h + 12, e);
        a.moveTo(h, e + 6);
        a.lineTo(h + 6, e + 12);
        a.lineTo(h + 12, e + 6);
        a.stroke()
    }
    h.ShapeState = function(a) {
        this.setup(a);
        this.dontTranslateOnDrag = !0
    };
    let q = h.ShapeState.prototype = new h._State;
    q.shapeType = h.ShapeState.LINE;
    q.superDoubleClick = q.dblclick;
    q.dblclick = function(a) {
        this.control || this.superDoubleClick(a)
    };
    q.innerexit = function(a) {
        this.shapeType = h.ShapeState.LINE;
        this.sketcher.repaint()
    };
    q.innermousemove = function(a) {
        this.control = l;
        if (this.shapeType === h.ShapeState.BRACKET) {
            for (let h = 0, e = this.sketcher.shapes.length; h < e; h++) {
                let e = this.sketcher.shapes[h];
                if (e instanceof f.Bracket) {
                    var n = d.min(e.p1.x, e.p2.x);
                    let f = d.max(e.p1.x, e.p2.x),
                        h = d.min(e.p1.y, e.p2.y),
                        b = d.max(e.p1.y, e.p2.y),
                        c = [];
                    c.push({
                        x: f + 5,
                        y: h + 15,
                        v: 1
                    });
                    c.push({
                        x: f + 5,
                        y: b + 15,
                        v: 2
                    });
                    c.push({
                        x: n - 17,
                        y: (h + b) / 2 + 15,
                        v: 3
                    });
                    for (let b = 0, d = c.length; b < d; b++)
                        if (n = c[b], g.isBetween(a.p.x, n.x, n.x + 12) && g.isBetween(a.p.y, n.y - 6, n.y)) {
                            this.control = {
                                s: e,
                                t: n.v
                            };
                            break
                        } else if (g.isBetween(a.p.x, n.x, n.x + 12) && g.isBetween(a.p.y, n.y + 6, n.y + 12)) {
                        this.control = {
                            s: e,
                            t: -1 * n.v
                        };
                        break
                    }
                    if (this.control) break
                }
            }
            this.sketcher.repaint()
        }
    };
    q.innermousedown = function(a) {
        this.control ? (this.sketcher.historyManager.pushUndo(new m.ChangeBracketAttributeAction(this.control.s,
            this.control.t)), this.sketcher.repaint()) : this.end = this.start = new p.Point(a.p.x, a.p.y)
    };
    q.innerdrag = function(f) {
        this.end = new p.Point(f.p.x, f.p.y);
        if (this.shapeType === h.ShapeState.BRACKET) {
            if (a.SHIFT) {
                f = this.end.x - this.start.x;
                var g = this.end.y - this.start.y;
                0 > f && 0 < g ? g *= -1 : 0 < f && 0 > g && (f *= -1);
                let a = g;
                d.abs(f) < d.abs(g) && (a = f);
                this.end.x = this.start.x + a;
                this.end.y = this.start.y + a
            }
        } else a.ALT || (f = this.start.angle(this.end), g = this.start.distance(this.end), a.ALT || (f = d.floor((f + d.PI / 12) / (d.PI / 6)) * d.PI / 6), this.end.x =
            this.start.x + g * d.cos(f), this.end.y = this.start.y - g * d.sin(f));
        this.sketcher.repaint()
    };
    q.innermouseup = function(a) {
        if (this.start && this.end) {
            let a;
            5 < this.start.distance(this.end) && (this.shapeType >= h.ShapeState.LINE && this.shapeType <= h.ShapeState.ARROW_EQUILIBRIUM ? (a = new f.Line(this.start, this.end), this.shapeType === h.ShapeState.ARROW_SYNTHETIC ? a.arrowType = f.Line.ARROW_SYNTHETIC : this.shapeType === h.ShapeState.ARROW_RETROSYNTHETIC ? a.arrowType = f.Line.ARROW_RETROSYNTHETIC : this.shapeType === h.ShapeState.ARROW_RESONANCE ?
                a.arrowType = f.Line.ARROW_RESONANCE : this.shapeType === h.ShapeState.ARROW_EQUILIBRIUM && (a.arrowType = f.Line.ARROW_EQUILIBRIUM)) : this.shapeType === h.ShapeState.BRACKET && (a = new f.Bracket(this.start, this.end)));
            this.end = this.start = l;
            a && this.sketcher.historyManager.pushUndo(new m.AddShapeAction(this.sketcher, a))
        }
    };
    q.draw = function(a, g) {
        if (this.start && this.end) a.strokeStyle = g.colorPreview, a.fillStyle = g.colorPreview, a.lineWidth = 1, a.beginPath(), a.moveTo(this.start.x, this.start.y), this.shapeType === h.ShapeState.BRACKET ?
            (a.lineTo(this.end.x, this.start.y), a.lineTo(this.end.x, this.end.y), a.lineTo(this.start.x, this.end.y), a.lineTo(this.start.x, this.start.y)) : a.lineTo(this.end.x, this.end.y), a.setLineDash([2]), a.stroke(), a.setLineDash([]);
        else if (this.shapeType === h.ShapeState.BRACKET) {
            a.lineWidth = 2;
            a.lineJoin = "miter";
            a.lineCap = "butt";
            for (let e = 0, h = this.sketcher.shapes.length; e < h; e++) {
                var n = this.sketcher.shapes[e];
                if (n instanceof f.Bracket) {
                    let e = d.min(n.p1.x, n.p2.x),
                        f = d.max(n.p1.x, n.p2.x),
                        b = d.min(n.p1.y, n.p2.y),
                        c = d.max(n.p1.y,
                            n.p2.y);
                    n = this.control && this.control.s === n ? this.control : l;
                    t(a, g, f + 5, b + 15, n, 1);
                    t(a, g, f + 5, c + 15, n, 2);
                    t(a, g, e - 17, (b + c) / 2 + 15, n, 3)
                }
            }
        }
    };
    h.ShapeState.LINE = 1;
    h.ShapeState.ARROW_SYNTHETIC = 2;
    h.ShapeState.ARROW_RETROSYNTHETIC = 3;
    h.ShapeState.ARROW_RESONANCE = 4;
    h.ShapeState.ARROW_EQUILIBRIUM = 5;
    h.ShapeState.BRACKET = 10
})(ChemDoodle.math, ChemDoodle.monitor, ChemDoodle.structures, ChemDoodle.structures.d2, ChemDoodle.uis.actions, ChemDoodle.uis.states, Math);
(function(g, a, p, f, m, h) {
    m.VAPState = function(a) {
        this.setup(a);
        this.dontTranslateOnDrag = !0
    };
    m = m.VAPState.prototype = new m._State;
    m.innermousedown = function(a) {
        if (this.sketcher.hovering || this.start && this.start instanceof p.VAP)
            if (this.sketcher.hovering && this.start !== this.sketcher.hovering)
                if (this.sketcher.hovering.hoverBond)
                    if (a = this.sketcher.hovering, a.hoverBond === a.substituent) {
                        var d = 1;
                        1 === a.bondType || 2 === a.bondType ? d = a.bondType + 1 : 3 === a.bondType && (d = .5);
                        this.sketcher.historyManager.pushUndo(new f.ChangeVAPOrderAction(a,
                            d))
                    } else this.sketcher.historyManager.pushUndo(new f.ChangeVAPSubstituentAction(a, this.sketcher.hovering.hoverBond));
        else this.start || (this.start = this.sketcher.hovering);
        else this.end = this.start = h, this.sketcher.repaint();
        else {
            d = !0;
            for (let f = 0, h = this.sketcher.shapes.length; f < h; f++) {
                let h = this.sketcher.shapes[f];
                h instanceof p.VAP && 30 > h.asterisk.distance(a.p) && (d = !1)
            }
            d && (a = new p.VAP(a.p.x, a.p.y), this.sketcher.isMobile || (a.isHover = !0, this.sketcher.hovering = a), this.sketcher.historyManager.pushUndo(new f.AddShapeAction(this.sketcher,
                a)))
        }
    };
    m.innerdrag = function(d) {
        this.start && (this.end = new a.Point(d.p.x, d.p.y), this.findHoveredObject(d, this.start instanceof p.VAP, !1, this.start instanceof a.Atom), this.sketcher.repaint())
    };
    m.innermouseup = function(a) {
        if (this.start && this.sketcher.hovering && this.sketcher.hovering !== this.start) {
            a = this.sketcher.hovering;
            let d = this.start;
            if (d instanceof p.VAP) {
                let f = a;
                a = d;
                d = f
            }
            a.substituent !== d && -1 === a.attachments.indexOf(d) && this.sketcher.historyManager.pushUndo(new f.AddVAPAttachementAction(a, d, a.substituent ===
                h));
            this.end = this.start = h;
            this.sketcher.repaint()
        }
    };
    m.innermousemove = function(d) {
        this.start ? (this.end = new a.Point(d.p.x, d.p.y), this.findHoveredObject(d, this.start instanceof p.VAP, !1, this.start instanceof a.Atom)) : this.findHoveredObject(d, !0, !0, !0);
        this.sketcher.repaint()
    };
    m.draw = function(a, f) {
        if (this.start && this.end) {
            a.strokeStyle = f.colorPreview;
            a.fillStyle = f.colorPreview;
            a.lineWidth = 1;
            f = this.start;
            let d = this.end;
            this.sketcher.hovering && (d = this.sketcher.hovering);
            f instanceof p.VAP && (f = f.asterisk);
            d instanceof p.VAP && (d = d.asterisk);
            a.beginPath();
            a.moveTo(f.x, f.y);
            a.lineTo(d.x, d.y);
            a.setLineDash([2]);
            a.stroke();
            a.setLineDash([])
        }
    };
    m.findHoveredObject = function(a, f, m, q) {
        this.clearHover();
        let d = Infinity,
            n, l = 10;
        this.sketcher.isMobile || (l /= this.sketcher.styles.scale);
        if (f)
            for (let h = 0, g = this.sketcher.molecules.length; h < g; h++) {
                f = this.sketcher.molecules[h];
                for (let h = 0, b = f.atoms.length; h < b; h++) {
                    var e = f.atoms[h];
                    e.isHover = !1;
                    let b = a.p.distance(e);
                    b < l && b < d && (d = b, n = e)
                }
            }
        if (m)
            for (let q = 0, r = this.sketcher.shapes.length; q <
                r; q++)
                if (m = this.sketcher.shapes[q], m instanceof p.VAP) {
                    m.hoverBond = h;
                    m.substituent && (f = m.substituent, e = g.distanceFromPointToLineInclusive(a.p, m.asterisk, f, l / 2), -1 !== e && e < l && e < d && (d = e, m.hoverBond = f, n = m));
                    for (let h = 0, b = m.attachments.length; h < b; h++) f = m.attachments[h], e = g.distanceFromPointToLineInclusive(a.p, m.asterisk, f, l / 2), -1 !== e && e < l && e < d && (d = e, m.hoverBond = f, n = m)
                } if (q)
            for (let e = 0, f = this.sketcher.shapes.length; e < f; e++) q = this.sketcher.shapes[e], q instanceof p.VAP && (q.isHover = !1, m = a.p.distance(q.asterisk),
                m < l && m < d && (d = m, n = q));
        n && (n.isHover = !0, this.sketcher.hovering = n)
    }
})(ChemDoodle.math, ChemDoodle.structures, ChemDoodle.structures.d2, ChemDoodle.uis.actions, ChemDoodle.uis.states);
(function(g, a, p) {
    g.StateManager = function(f) {
        this.STATE_NEW_BOND = new g.NewBondState(f);
        this.STATE_NEW_RING = new g.NewRingState(f);
        this.STATE_NEW_CHAIN = new g.NewChainState(f);
        this.STATE_NEW_TEMPLATE = new g.NewTemplateState(f);
        g.TextInputState && (this.STATE_TEXT_INPUT = new g.TextInputState(f));
        this.STATE_CHARGE = new g.ChargeState(f);
        this.STATE_LONE_PAIR = new g.LonePairState(f);
        this.STATE_RADICAL = new g.RadicalState(f);
        this.STATE_ISOTOPE = new g.IsotopeState(f);
        this.STATE_MOVE = new g.MoveState(f);
        this.STATE_ERASE =
            new g.EraseState(f);
        this.STATE_LABEL = new g.LabelState(f);
        this.STATE_LASSO = new g.LassoState(f);
        this.STATE_SHAPE = new g.ShapeState(f);
        this.STATE_PUSHER = new g.PusherState(f);
        this.STATE_REPEAT_UNIT = new g.RepeatUnitState(f);
        this.STATE_VAP = new g.VAPState(f);
        this.STATE_QUERY = new g.QueryState(f);
        let m = this.STATE_NEW_BOND;
        m.enter();
        this.setState = function(h) {
            h !== m && (m.exit(), m = h, m.enter());
            f.openTray && "false" === a("#" + f.openTray.dummy.id + "_label").attr("aria-pressed") && f.openTray.close()
        };
        this.getCurrentState =
            function() {
                return m
            }
    }
})(ChemDoodle.uis.states, ChemDoodle.lib.jQuery);
ChemDoodle.uis.gui.imageDepot = function(g, a) {
    return {
        getURI: function(a) {
            return "data:image/svg+xml;base64," + a
        },
        ADD_LONE_PAIR: "PHN2ZyBmaWxsLW9wYWNpdHk9IjEiIHhtbG5zOnhsaW5rPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5L3hsaW5rIiBjb2xvci1yZW5kZXJpbmc9ImF1dG8iIGNvbG9yLWludGVycG9sYXRpb249ImF1dG8iIHRleHQtcmVuZGVyaW5nPSJhdXRvIiBzdHJva2U9ImJsYWNrIiBzdHJva2UtbGluZWNhcD0ic3F1YXJlIiB3aWR0aD0iMjAiIHN0cm9rZS1taXRlcmxpbWl0PSIxMCIgc2hhcGUtcmVuZGVyaW5nPSJhdXRvIiBzdHJva2Utb3BhY2l0eT0iMSIgZmlsbD0iYmxhY2siIHN0cm9rZS1kYXNoYXJyYXk9Im5vbmUiIGZvbnQtd2VpZ2h0PSJub3JtYWwiIHN0cm9rZS13aWR0aD0iMSIgdmlld0JveD0iMCAwIDIwLjAgMjAuMCIgaGVpZ2h0PSIyMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIiBmb250LWZhbWlseT0iJmFwb3M7RGlhbG9nJmFwb3M7IiBmb250LXN0eWxlPSJub3JtYWwiIHN0cm9rZS1saW5lam9pbj0ibWl0ZXIiIGZvbnQtc2l6ZT0iMTIiIHN0cm9rZS1kYXNob2Zmc2V0PSIwIiBpbWFnZS1yZW5kZXJpbmc9ImF1dG8iPjxkZWZzIGlkPSJnZW5lcmljRGVmcyIgIC8+PGcgID48ZyB0ZXh0LXJlbmRlcmluZz0iZ2VvbWV0cmljUHJlY2lzaW9uIiBjb2xvci1yZW5kZXJpbmc9Im9wdGltaXplUXVhbGl0eSIgY29sb3ItaW50ZXJwb2xhdGlvbj0ibGluZWFyUkdCIiBpbWFnZS1yZW5kZXJpbmc9Im9wdGltaXplU3BlZWQiICAgID48Y2lyY2xlIHI9IjIiIGN4PSI2IiBjeT0iMTAiIHN0cm9rZT0ibm9uZSIgICAgICAvPjxjaXJjbGUgcj0iMiIgY3g9IjE0IiBjeT0iMTAiIHN0cm9rZT0ibm9uZSIgICAgLz48L2cgID48L2c+PC9zdmc+",
        ADD_RADICAL: "PHN2ZyBmaWxsLW9wYWNpdHk9IjEiIHhtbG5zOnhsaW5rPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5L3hsaW5rIiBjb2xvci1yZW5kZXJpbmc9ImF1dG8iIGNvbG9yLWludGVycG9sYXRpb249ImF1dG8iIHRleHQtcmVuZGVyaW5nPSJhdXRvIiBzdHJva2U9ImJsYWNrIiBzdHJva2UtbGluZWNhcD0ic3F1YXJlIiB3aWR0aD0iMjAiIHN0cm9rZS1taXRlcmxpbWl0PSIxMCIgc2hhcGUtcmVuZGVyaW5nPSJhdXRvIiBzdHJva2Utb3BhY2l0eT0iMSIgZmlsbD0iYmxhY2siIHN0cm9rZS1kYXNoYXJyYXk9Im5vbmUiIGZvbnQtd2VpZ2h0PSJub3JtYWwiIHN0cm9rZS13aWR0aD0iMSIgdmlld0JveD0iMCAwIDIwLjAgMjAuMCIgaGVpZ2h0PSIyMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIiBmb250LWZhbWlseT0iJmFwb3M7RGlhbG9nJmFwb3M7IiBmb250LXN0eWxlPSJub3JtYWwiIHN0cm9rZS1saW5lam9pbj0ibWl0ZXIiIGZvbnQtc2l6ZT0iMTIiIHN0cm9rZS1kYXNob2Zmc2V0PSIwIiBpbWFnZS1yZW5kZXJpbmc9ImF1dG8iPjxkZWZzIGlkPSJnZW5lcmljRGVmcyIgIC8+PGcgID48ZyB0ZXh0LXJlbmRlcmluZz0iZ2VvbWV0cmljUHJlY2lzaW9uIiBjb2xvci1yZW5kZXJpbmc9Im9wdGltaXplUXVhbGl0eSIgY29sb3ItaW50ZXJwb2xhdGlvbj0ibGluZWFyUkdCIiBpbWFnZS1yZW5kZXJpbmc9Im9wdGltaXplU3BlZWQiICAgID48Y2lyY2xlIHI9IjIiIGN4PSIxMCIgY3k9IjEwIiBzdHJva2U9Im5vbmUiICAgIC8+PC9nICA+PC9nPjwvc3ZnPg\x3d\x3d",
        ARROW_DOWN: "PHN2ZyB2ZXJzaW9uPSIxLjEiIGlkPSJMYXllcl8xIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHhtbG5zOnhsaW5rPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5L3hsaW5rIiB4PSIwcHgiIHk9IjBweCIJIHZpZXdCb3g9IjAgMCA5IDIwIiBzdHlsZT0iZW5hYmxlLWJhY2tncm91bmQ6bmV3IDAgMCA5IDIwOyIgeG1sOnNwYWNlPSJwcmVzZXJ2ZSI+PHBvbHlnb24gc3R5bGU9InN0cm9rZTojMDAwMDAwO3N0cm9rZS1taXRlcmxpbWl0OjEwOyIgcG9pbnRzPSIxLjI3OCw3LjY5NSA3LjcyMiw3LjY5NSA0LjYwNSwxMi4zMDUgIi8+PC9zdmc+",
        BENZENE: "PHN2ZyBmaWxsLW9wYWNpdHk9IjEiIHhtbG5zOnhsaW5rPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5L3hsaW5rIiBjb2xvci1yZW5kZXJpbmc9ImF1dG8iIGNvbG9yLWludGVycG9sYXRpb249ImF1dG8iIHRleHQtcmVuZGVyaW5nPSJhdXRvIiBzdHJva2U9ImJsYWNrIiBzdHJva2UtbGluZWNhcD0ic3F1YXJlIiB3aWR0aD0iMjAiIHN0cm9rZS1taXRlcmxpbWl0PSIxMCIgc2hhcGUtcmVuZGVyaW5nPSJhdXRvIiBzdHJva2Utb3BhY2l0eT0iMSIgZmlsbD0iYmxhY2siIHN0cm9rZS1kYXNoYXJyYXk9Im5vbmUiIGZvbnQtd2VpZ2h0PSJub3JtYWwiIHN0cm9rZS13aWR0aD0iMSIgdmlld0JveD0iMCAwIDIwLjAgMjAuMCIgaGVpZ2h0PSIyMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIiBmb250LWZhbWlseT0iJmFwb3M7RGlhbG9nJmFwb3M7IiBmb250LXN0eWxlPSJub3JtYWwiIHN0cm9rZS1saW5lam9pbj0ibWl0ZXIiIGZvbnQtc2l6ZT0iMTIiIHN0cm9rZS1kYXNob2Zmc2V0PSIwIiBpbWFnZS1yZW5kZXJpbmc9ImF1dG8iPjxkZWZzIGlkPSJnZW5lcmljRGVmcyIgIC8+PGcgID48ZyB0ZXh0LXJlbmRlcmluZz0iZ2VvbWV0cmljUHJlY2lzaW9uIiB0cmFuc2Zvcm09InRyYW5zbGF0ZSgxMCwxMCkiIGNvbG9yLXJlbmRlcmluZz0ib3B0aW1pemVRdWFsaXR5IiBjb2xvci1pbnRlcnBvbGF0aW9uPSJsaW5lYXJSR0IiIGltYWdlLXJlbmRlcmluZz0ib3B0aW1pemVTcGVlZCIgICAgPjxsaW5lIHkyPSI1LjUiIGZpbGw9Im5vbmUiIHgxPSItNC43NjMxIiB4Mj0iLTAiIHkxPSIyLjc1IiAgICAgIC8+PGxpbmUgeTI9Ii0yLjc1IiBmaWxsPSJub25lIiB4MT0iNC43NjMxIiB4Mj0iNC43NjMxIiB5MT0iMi43NSIgICAgICAvPjxsaW5lIHkyPSItMi43NSIgZmlsbD0ibm9uZSIgeDE9IjAiIHgyPSItNC43NjMxIiB5MT0iLTUuNSIgICAgICAvPjxsaW5lIHkyPSI4LjUiIGZpbGw9Im5vbmUiIHgxPSItNy4zNjEyIiB4Mj0iLTAiIHkxPSI0LjI1IiAgICAgIC8+PGxpbmUgeTI9IjQuMjUiIGZpbGw9Im5vbmUiIHgxPSItMCIgeDI9IjcuMzYxMiIgeTE9IjguNSIgICAgICAvPjxsaW5lIHkyPSItNC4yNSIgZmlsbD0ibm9uZSIgeDE9IjcuMzYxMiIgeDI9IjcuMzYxMiIgeTE9IjQuMjUiICAgICAgLz48bGluZSB5Mj0iLTguNSIgZmlsbD0ibm9uZSIgeDE9IjcuMzYxMiIgeDI9IjAiIHkxPSItNC4yNSIgICAgICAvPjxsaW5lIHkyPSItNC4yNSIgZmlsbD0ibm9uZSIgeDE9IjAiIHgyPSItNy4zNjEyIiB5MT0iLTguNSIgICAgICAvPjxsaW5lIHkyPSI0LjI1IiBmaWxsPSJub25lIiB4MT0iLTcuMzYxMiIgeDI9Ii03LjM2MTIiIHkxPSItNC4yNSIgICAgLz48L2cgID48L2c+PC9zdmc+",
        BOND_ANY: "PHN2ZyBmaWxsLW9wYWNpdHk9IjEiIHhtbG5zOnhsaW5rPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5L3hsaW5rIiBjb2xvci1yZW5kZXJpbmc9ImF1dG8iIGNvbG9yLWludGVycG9sYXRpb249ImF1dG8iIHRleHQtcmVuZGVyaW5nPSJhdXRvIiBzdHJva2U9ImJsYWNrIiBzdHJva2UtbGluZWNhcD0ic3F1YXJlIiB3aWR0aD0iMjAiIHN0cm9rZS1taXRlcmxpbWl0PSIxMCIgc2hhcGUtcmVuZGVyaW5nPSJhdXRvIiBzdHJva2Utb3BhY2l0eT0iMSIgZmlsbD0iYmxhY2siIHN0cm9rZS1kYXNoYXJyYXk9Im5vbmUiIGZvbnQtd2VpZ2h0PSJub3JtYWwiIHN0cm9rZS13aWR0aD0iMSIgdmlld0JveD0iMCAwIDIwLjAgMjAuMCIgaGVpZ2h0PSIyMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIiBmb250LWZhbWlseT0iJmFwb3M7RGlhbG9nJmFwb3M7IiBmb250LXN0eWxlPSJub3JtYWwiIHN0cm9rZS1saW5lam9pbj0ibWl0ZXIiIGZvbnQtc2l6ZT0iMTIiIHN0cm9rZS1kYXNob2Zmc2V0PSIwIiBpbWFnZS1yZW5kZXJpbmc9ImF1dG8iPjxkZWZzIGlkPSJnZW5lcmljRGVmcyIgIC8+PGcgID48ZGVmcyBpZD0iZGVmczEiICAgID48Y2xpcFBhdGggY2xpcFBhdGhVbml0cz0idXNlclNwYWNlT25Vc2UiIGlkPSJjbGlwUGF0aDEiICAgICAgPjxwYXRoIGQ9Ik0wIDAgTDAgMjAgTDIwIDIwIEwyMCAxNCBMMSAxNCBMMSA3IEwyMCA3IEwyMCAwIFoiICAgICAgLz48L2NsaXBQYXRoICAgICAgPjxjbGlwUGF0aCBjbGlwUGF0aFVuaXRzPSJ1c2VyU3BhY2VPblVzZSIgaWQ9ImNsaXBQYXRoMiIgICAgICA+PHBhdGggZD0iTTAgMCBMMjAgMCBMMjAgMjAgTDAgMjAgTDAgMCBaIiAgICAgIC8+PC9jbGlwUGF0aCAgICA+PC9kZWZzICAgID48ZyB0ZXh0LXJlbmRlcmluZz0iZ2VvbWV0cmljUHJlY2lzaW9uIiBmb250LXNpemU9IjgiIGZvbnQtZmFtaWx5PSImYXBvcztMdWNpZGEgR3JhbmRlJmFwb3M7IiBjb2xvci1pbnRlcnBvbGF0aW9uPSJsaW5lYXJSR0IiIGNvbG9yLXJlbmRlcmluZz0ib3B0aW1pemVRdWFsaXR5IiBpbWFnZS1yZW5kZXJpbmc9Im9wdGltaXplU3BlZWQiICAgID48bGluZSB5Mj0iMiIgZmlsbD0ibm9uZSIgeDE9IjIiIGNsaXAtcGF0aD0idXJsKCNjbGlwUGF0aDEpIiB4Mj0iMTgiIHkxPSIxOCIgICAgICAvPjxwYXRoIGQ9Ik01LjY3NTggMTEuNzg5MSBMNC42OTE0IDkuMjk2OSBMMy43MDMxIDExLjc4OTEgWk02LjU0MyAxNCBMNS45MTQxIDEyLjM5ODQgTDMuNDY0OCAxMi4zOTg0IEwyLjgyODEgMTQgTDIuMDY2NCAxNCBMNC4zNTk0IDguMjE4OCBMNS4xNzE5IDguMjE4OCBMNy40Mjk3IDE0IFpNOC43NDYxIDE0IEw4Ljc0NjEgOC4yMTg4IEw5LjU1MDggOC4yMTg4IEwxMi40NjA5IDEyLjY4MzYgTDEyLjQ2MDkgOC4yMTg4IEwxMy4xNjQxIDguMjE4OCBMMTMuMTY0MSAxNCBMMTIuMzYzMyAxNCBMOS40NDkyIDkuNTM1MiBMOS40NDkyIDE0IFpNMTUuOTk2MSAxNCBMMTUuOTk2MSAxMS41ODU5IEwxNC4wNjY0IDguMjE4OCBMMTUuMDAzOSA4LjIxODggTDE2LjUwMzkgMTAuODI4MSBMMTguMTIxMSA4LjIxODggTDE4Ljg4MjggOC4yMTg4IEwxNi44MTY0IDExLjU3MDMgTDE2LjgxNjQgMTQgWiIgY2xpcC1wYXRoPSJ1cmwoI2NsaXBQYXRoMikiIHN0cm9rZT0ibm9uZSIgICAgLz48L2cgID48L2c+PC9zdmc+",
        BOND_COVALENT: "PHN2ZyBmaWxsLW9wYWNpdHk9IjEiIHhtbG5zOnhsaW5rPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5L3hsaW5rIiBjb2xvci1yZW5kZXJpbmc9ImF1dG8iIGNvbG9yLWludGVycG9sYXRpb249ImF1dG8iIHRleHQtcmVuZGVyaW5nPSJhdXRvIiBzdHJva2U9ImJsYWNrIiBzdHJva2UtbGluZWNhcD0ic3F1YXJlIiB3aWR0aD0iMjAiIHN0cm9rZS1taXRlcmxpbWl0PSIxMCIgc2hhcGUtcmVuZGVyaW5nPSJhdXRvIiBzdHJva2Utb3BhY2l0eT0iMSIgZmlsbD0iYmxhY2siIHN0cm9rZS1kYXNoYXJyYXk9Im5vbmUiIGZvbnQtd2VpZ2h0PSJub3JtYWwiIHN0cm9rZS13aWR0aD0iMSIgdmlld0JveD0iMCAwIDIwLjAgMjAuMCIgaGVpZ2h0PSIyMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIiBmb250LWZhbWlseT0iJ0RpYWxvZyciIGZvbnQtc3R5bGU9Im5vcm1hbCIgc3Ryb2tlLWxpbmVqb2luPSJtaXRlciIgZm9udC1zaXplPSIxMnB4IiBzdHJva2UtZGFzaG9mZnNldD0iMCIgaW1hZ2UtcmVuZGVyaW5nPSJhdXRvIj48ZGVmcyBpZD0iZ2VuZXJpY0RlZnMiICAvPjxnICA+PGcgdGV4dC1yZW5kZXJpbmc9Imdlb21ldHJpY1ByZWNpc2lvbiIgY29sb3ItcmVuZGVyaW5nPSJvcHRpbWl6ZVF1YWxpdHkiIGNvbG9yLWludGVycG9sYXRpb249ImxpbmVhclJHQiIgaW1hZ2UtcmVuZGVyaW5nPSJvcHRpbWl6ZVNwZWVkIiAgICA+PGxpbmUgeTI9IjIiIGZpbGw9Im5vbmUiIHgxPSIyIiB4Mj0iMTgiIHkxPSIxOCIgICAgICAvPjxwb2x5Z29uIHBvaW50cz0iIDE4IDIgMTIgNSAxNiA4IiBzdHJva2U9Im5vbmUiICAgIC8+PC9nICA+PC9nPjwvc3ZnPg\x3d\x3d",
        BOND_DOUBLE: "PHN2ZyBmaWxsLW9wYWNpdHk9IjEiIHhtbG5zOnhsaW5rPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5L3hsaW5rIiBjb2xvci1yZW5kZXJpbmc9ImF1dG8iIGNvbG9yLWludGVycG9sYXRpb249ImF1dG8iIHRleHQtcmVuZGVyaW5nPSJhdXRvIiBzdHJva2U9ImJsYWNrIiBzdHJva2UtbGluZWNhcD0ic3F1YXJlIiB3aWR0aD0iMjAiIHN0cm9rZS1taXRlcmxpbWl0PSIxMCIgc2hhcGUtcmVuZGVyaW5nPSJhdXRvIiBzdHJva2Utb3BhY2l0eT0iMSIgZmlsbD0iYmxhY2siIHN0cm9rZS1kYXNoYXJyYXk9Im5vbmUiIGZvbnQtd2VpZ2h0PSJub3JtYWwiIHN0cm9rZS13aWR0aD0iMSIgdmlld0JveD0iMCAwIDIwLjAgMjAuMCIgaGVpZ2h0PSIyMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIiBmb250LWZhbWlseT0iJmFwb3M7RGlhbG9nJmFwb3M7IiBmb250LXN0eWxlPSJub3JtYWwiIHN0cm9rZS1saW5lam9pbj0ibWl0ZXIiIGZvbnQtc2l6ZT0iMTIiIHN0cm9rZS1kYXNob2Zmc2V0PSIwIiBpbWFnZS1yZW5kZXJpbmc9ImF1dG8iPjxkZWZzIGlkPSJnZW5lcmljRGVmcyIgIC8+PGcgID48ZyB0ZXh0LXJlbmRlcmluZz0iZ2VvbWV0cmljUHJlY2lzaW9uIiBjb2xvci1yZW5kZXJpbmc9Im9wdGltaXplUXVhbGl0eSIgY29sb3ItaW50ZXJwb2xhdGlvbj0ibGluZWFyUkdCIiBpbWFnZS1yZW5kZXJpbmc9Im9wdGltaXplU3BlZWQiICAgID48bGluZSB5Mj0iMSIgZmlsbD0ibm9uZSIgeDE9IjEiIHgyPSIxNyIgeTE9IjE3IiAgICAgIC8+PGxpbmUgeTI9IjMiIGZpbGw9Im5vbmUiIHgxPSIzIiB4Mj0iMTkiIHkxPSIxOSIgICAgLz48L2cgID48L2c+PC9zdmc+",
        BOND_DOUBLE_AMBIGUOUS: "PHN2ZyBmaWxsLW9wYWNpdHk9IjEiIHhtbG5zOnhsaW5rPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5L3hsaW5rIiBjb2xvci1yZW5kZXJpbmc9ImF1dG8iIGNvbG9yLWludGVycG9sYXRpb249ImF1dG8iIHRleHQtcmVuZGVyaW5nPSJhdXRvIiBzdHJva2U9ImJsYWNrIiBzdHJva2UtbGluZWNhcD0ic3F1YXJlIiB3aWR0aD0iMjAiIHN0cm9rZS1taXRlcmxpbWl0PSIxMCIgc2hhcGUtcmVuZGVyaW5nPSJhdXRvIiBzdHJva2Utb3BhY2l0eT0iMSIgZmlsbD0iYmxhY2siIHN0cm9rZS1kYXNoYXJyYXk9Im5vbmUiIGZvbnQtd2VpZ2h0PSJub3JtYWwiIHN0cm9rZS13aWR0aD0iMSIgdmlld0JveD0iMCAwIDIwLjAgMjAuMCIgaGVpZ2h0PSIyMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIiBmb250LWZhbWlseT0iJmFwb3M7RGlhbG9nJmFwb3M7IiBmb250LXN0eWxlPSJub3JtYWwiIHN0cm9rZS1saW5lam9pbj0ibWl0ZXIiIGZvbnQtc2l6ZT0iMTIiIHN0cm9rZS1kYXNob2Zmc2V0PSIwIiBpbWFnZS1yZW5kZXJpbmc9ImF1dG8iPjxkZWZzIGlkPSJnZW5lcmljRGVmcyIgIC8+PGcgID48ZyB0ZXh0LXJlbmRlcmluZz0iZ2VvbWV0cmljUHJlY2lzaW9uIiBjb2xvci1yZW5kZXJpbmc9Im9wdGltaXplUXVhbGl0eSIgY29sb3ItaW50ZXJwb2xhdGlvbj0ibGluZWFyUkdCIiBpbWFnZS1yZW5kZXJpbmc9Im9wdGltaXplU3BlZWQiICAgID48bGluZSB5Mj0iMyIgZmlsbD0ibm9uZSIgeDE9IjEiIHgyPSIxOSIgeTE9IjE3IiAgICAgIC8+PGxpbmUgeTI9IjEiIGZpbGw9Im5vbmUiIHgxPSIzIiB4Mj0iMTciIHkxPSIxOSIgICAgLz48L2cgID48L2c+PC9zdmc+",
        BOND_HALF: "PHN2ZyBmaWxsLW9wYWNpdHk9IjEiIHhtbG5zOnhsaW5rPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5L3hsaW5rIiBjb2xvci1yZW5kZXJpbmc9ImF1dG8iIGNvbG9yLWludGVycG9sYXRpb249ImF1dG8iIHRleHQtcmVuZGVyaW5nPSJhdXRvIiBzdHJva2U9ImJsYWNrIiBzdHJva2UtbGluZWNhcD0ic3F1YXJlIiB3aWR0aD0iMjAiIHN0cm9rZS1taXRlcmxpbWl0PSIxMCIgc2hhcGUtcmVuZGVyaW5nPSJhdXRvIiBzdHJva2Utb3BhY2l0eT0iMSIgZmlsbD0iYmxhY2siIHN0cm9rZS1kYXNoYXJyYXk9Im5vbmUiIGZvbnQtd2VpZ2h0PSJub3JtYWwiIHN0cm9rZS13aWR0aD0iMSIgdmlld0JveD0iMCAwIDIwLjAgMjAuMCIgaGVpZ2h0PSIyMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIiBmb250LWZhbWlseT0iJmFwb3M7RGlhbG9nJmFwb3M7IiBmb250LXN0eWxlPSJub3JtYWwiIHN0cm9rZS1saW5lam9pbj0ibWl0ZXIiIGZvbnQtc2l6ZT0iMTIiIHN0cm9rZS1kYXNob2Zmc2V0PSIwIiBpbWFnZS1yZW5kZXJpbmc9ImF1dG8iPjxkZWZzIGlkPSJnZW5lcmljRGVmcyIgIC8+PGcgID48ZyBzdHJva2UtZGFzaG9mZnNldD0iMSIgdGV4dC1yZW5kZXJpbmc9Imdlb21ldHJpY1ByZWNpc2lvbiIgaW1hZ2UtcmVuZGVyaW5nPSJvcHRpbWl6ZVNwZWVkIiBjb2xvci1yZW5kZXJpbmc9Im9wdGltaXplUXVhbGl0eSIgc3Ryb2tlLWxpbmVqb2luPSJiZXZlbCIgc3Ryb2tlLWRhc2hhcnJheT0iMSwxLDQsNCw0LDQsNCw0LDQsMSIgY29sb3ItaW50ZXJwb2xhdGlvbj0ibGluZWFyUkdCIiBzdHJva2UtbWl0ZXJsaW1pdD0iMSIgICAgPjxsaW5lIHkyPSIyIiBmaWxsPSJub25lIiB4MT0iMiIgeDI9IjE4IiB5MT0iMTgiICAgIC8+PC9nICA+PC9nPjwvc3ZnPg\x3d\x3d",
        BOND_PROTRUDING: "PHN2ZyBmaWxsLW9wYWNpdHk9IjEiIHhtbG5zOnhsaW5rPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5L3hsaW5rIiBjb2xvci1yZW5kZXJpbmc9ImF1dG8iIGNvbG9yLWludGVycG9sYXRpb249ImF1dG8iIHRleHQtcmVuZGVyaW5nPSJhdXRvIiBzdHJva2U9ImJsYWNrIiBzdHJva2UtbGluZWNhcD0ic3F1YXJlIiB3aWR0aD0iMjAiIHN0cm9rZS1taXRlcmxpbWl0PSIxMCIgc2hhcGUtcmVuZGVyaW5nPSJhdXRvIiBzdHJva2Utb3BhY2l0eT0iMSIgZmlsbD0iYmxhY2siIHN0cm9rZS1kYXNoYXJyYXk9Im5vbmUiIGZvbnQtd2VpZ2h0PSJub3JtYWwiIHN0cm9rZS13aWR0aD0iMSIgdmlld0JveD0iMCAwIDIwLjAgMjAuMCIgaGVpZ2h0PSIyMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIiBmb250LWZhbWlseT0iJmFwb3M7RGlhbG9nJmFwb3M7IiBmb250LXN0eWxlPSJub3JtYWwiIHN0cm9rZS1saW5lam9pbj0ibWl0ZXIiIGZvbnQtc2l6ZT0iMTIiIHN0cm9rZS1kYXNob2Zmc2V0PSIwIiBpbWFnZS1yZW5kZXJpbmc9ImF1dG8iPjxkZWZzIGlkPSJnZW5lcmljRGVmcyIgIC8+PGcgID48ZyB0ZXh0LXJlbmRlcmluZz0iZ2VvbWV0cmljUHJlY2lzaW9uIiBjb2xvci1yZW5kZXJpbmc9Im9wdGltaXplUXVhbGl0eSIgY29sb3ItaW50ZXJwb2xhdGlvbj0ibGluZWFyUkdCIiBpbWFnZS1yZW5kZXJpbmc9Im9wdGltaXplU3BlZWQiICAgID48cG9seWdvbiBwb2ludHM9IiAyIDE4IDE2IDAgMjAgNCIgc3Ryb2tlPSJub25lIiAgICAvPjwvZyAgPjwvZz48L3N2Zz4\x3d",
        BOND_RECESSED: "PHN2ZyBmaWxsLW9wYWNpdHk9IjEiIHhtbG5zOnhsaW5rPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5L3hsaW5rIiBjb2xvci1yZW5kZXJpbmc9ImF1dG8iIGNvbG9yLWludGVycG9sYXRpb249ImF1dG8iIHRleHQtcmVuZGVyaW5nPSJhdXRvIiBzdHJva2U9ImJsYWNrIiBzdHJva2UtbGluZWNhcD0ic3F1YXJlIiB3aWR0aD0iMjAiIHN0cm9rZS1taXRlcmxpbWl0PSIxMCIgc2hhcGUtcmVuZGVyaW5nPSJhdXRvIiBzdHJva2Utb3BhY2l0eT0iMSIgZmlsbD0iYmxhY2siIHN0cm9rZS1kYXNoYXJyYXk9Im5vbmUiIGZvbnQtd2VpZ2h0PSJub3JtYWwiIHN0cm9rZS13aWR0aD0iMSIgdmlld0JveD0iMCAwIDIwLjAgMjAuMCIgaGVpZ2h0PSIyMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIiBmb250LWZhbWlseT0iJmFwb3M7RGlhbG9nJmFwb3M7IiBmb250LXN0eWxlPSJub3JtYWwiIHN0cm9rZS1saW5lam9pbj0ibWl0ZXIiIGZvbnQtc2l6ZT0iMTIiIHN0cm9rZS1kYXNob2Zmc2V0PSIwIiBpbWFnZS1yZW5kZXJpbmc9ImF1dG8iPjxkZWZzIGlkPSJnZW5lcmljRGVmcyIgIC8+PGcgID48ZGVmcyBpZD0iZGVmczEiICAgID48Y2xpcFBhdGggY2xpcFBhdGhVbml0cz0idXNlclNwYWNlT25Vc2UiIGlkPSJjbGlwUGF0aDEiICAgICAgPjxwYXRoIGQ9Ik0yIDE4IEwxNiAwIEwyMCA0IFoiIGZpbGwtcnVsZT0iZXZlbm9kZCIgICAgICAvPjwvY2xpcFBhdGggICAgPjwvZGVmcyAgICA+PGcgc3Ryb2tlLWxpbmVjYXA9ImJ1dHQiIHN0cm9rZS1kYXNob2Zmc2V0PSIxLjIxIiB0ZXh0LXJlbmRlcmluZz0iZ2VvbWV0cmljUHJlY2lzaW9uIiBpbWFnZS1yZW5kZXJpbmc9Im9wdGltaXplU3BlZWQiIGNvbG9yLXJlbmRlcmluZz0ib3B0aW1pemVRdWFsaXR5IiBzdHJva2UtbGluZWpvaW49ImJldmVsIiBzdHJva2UtZGFzaGFycmF5PSIxLjIxLDMiIGNvbG9yLWludGVycG9sYXRpb249ImxpbmVhclJHQiIgc3Ryb2tlLXdpZHRoPSI2LjIiIHN0cm9rZS1taXRlcmxpbWl0PSIxIiAgICA+PGxpbmUgeTI9IjIiIGZpbGw9Im5vbmUiIHgxPSIyIiBjbGlwLXBhdGg9InVybCgjY2xpcFBhdGgxKSIgeDI9IjE4IiB5MT0iMTgiICAgIC8+PC9nICA+PC9nPjwvc3ZnPg\x3d\x3d",
        BOND_RESONANCE: "PHN2ZyBmaWxsLW9wYWNpdHk9IjEiIHhtbG5zOnhsaW5rPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5L3hsaW5rIiBjb2xvci1yZW5kZXJpbmc9ImF1dG8iIGNvbG9yLWludGVycG9sYXRpb249ImF1dG8iIHRleHQtcmVuZGVyaW5nPSJhdXRvIiBzdHJva2U9ImJsYWNrIiBzdHJva2UtbGluZWNhcD0ic3F1YXJlIiB3aWR0aD0iMjAiIHN0cm9rZS1taXRlcmxpbWl0PSIxMCIgc2hhcGUtcmVuZGVyaW5nPSJhdXRvIiBzdHJva2Utb3BhY2l0eT0iMSIgZmlsbD0iYmxhY2siIHN0cm9rZS1kYXNoYXJyYXk9Im5vbmUiIGZvbnQtd2VpZ2h0PSJub3JtYWwiIHN0cm9rZS13aWR0aD0iMSIgdmlld0JveD0iMCAwIDIwLjAgMjAuMCIgaGVpZ2h0PSIyMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIiBmb250LWZhbWlseT0iJmFwb3M7RGlhbG9nJmFwb3M7IiBmb250LXN0eWxlPSJub3JtYWwiIHN0cm9rZS1saW5lam9pbj0ibWl0ZXIiIGZvbnQtc2l6ZT0iMTIiIHN0cm9rZS1kYXNob2Zmc2V0PSIwIiBpbWFnZS1yZW5kZXJpbmc9ImF1dG8iPjxkZWZzIGlkPSJnZW5lcmljRGVmcyIgIC8+PGcgID48ZyB0ZXh0LXJlbmRlcmluZz0iZ2VvbWV0cmljUHJlY2lzaW9uIiBjb2xvci1yZW5kZXJpbmc9Im9wdGltaXplUXVhbGl0eSIgY29sb3ItaW50ZXJwb2xhdGlvbj0ibGluZWFyUkdCIiBpbWFnZS1yZW5kZXJpbmc9Im9wdGltaXplU3BlZWQiICAgID48bGluZSB5Mj0iMSIgZmlsbD0ibm9uZSIgeDE9IjEiIHgyPSIxNyIgeTE9IjE3IiAgICAvPjwvZyAgICA+PGcgc3Ryb2tlLWRhc2hvZmZzZXQ9IjEiIHRleHQtcmVuZGVyaW5nPSJnZW9tZXRyaWNQcmVjaXNpb24iIGltYWdlLXJlbmRlcmluZz0ib3B0aW1pemVTcGVlZCIgY29sb3ItcmVuZGVyaW5nPSJvcHRpbWl6ZVF1YWxpdHkiIHN0cm9rZS1saW5lam9pbj0iYmV2ZWwiIHN0cm9rZS1kYXNoYXJyYXk9IjEsMSw0LDQsNCw0LDQsNCw0LDEiIGNvbG9yLWludGVycG9sYXRpb249ImxpbmVhclJHQiIgc3Ryb2tlLW1pdGVybGltaXQ9IjEiICAgID48bGluZSB5Mj0iMyIgZmlsbD0ibm9uZSIgeDE9IjMiIHgyPSIxOSIgeTE9IjE5IiAgICAvPjwvZyAgPjwvZz48L3N2Zz4\x3d",
        BOND_SINGLE: "PHN2ZyBmaWxsLW9wYWNpdHk9IjEiIHhtbG5zOnhsaW5rPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5L3hsaW5rIiBjb2xvci1yZW5kZXJpbmc9ImF1dG8iIGNvbG9yLWludGVycG9sYXRpb249ImF1dG8iIHRleHQtcmVuZGVyaW5nPSJhdXRvIiBzdHJva2U9ImJsYWNrIiBzdHJva2UtbGluZWNhcD0ic3F1YXJlIiB3aWR0aD0iMjAiIHN0cm9rZS1taXRlcmxpbWl0PSIxMCIgc2hhcGUtcmVuZGVyaW5nPSJhdXRvIiBzdHJva2Utb3BhY2l0eT0iMSIgZmlsbD0iYmxhY2siIHN0cm9rZS1kYXNoYXJyYXk9Im5vbmUiIGZvbnQtd2VpZ2h0PSJub3JtYWwiIHN0cm9rZS13aWR0aD0iMSIgdmlld0JveD0iMCAwIDIwLjAgMjAuMCIgaGVpZ2h0PSIyMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIiBmb250LWZhbWlseT0iJmFwb3M7RGlhbG9nJmFwb3M7IiBmb250LXN0eWxlPSJub3JtYWwiIHN0cm9rZS1saW5lam9pbj0ibWl0ZXIiIGZvbnQtc2l6ZT0iMTIiIHN0cm9rZS1kYXNob2Zmc2V0PSIwIiBpbWFnZS1yZW5kZXJpbmc9ImF1dG8iPjxkZWZzIGlkPSJnZW5lcmljRGVmcyIgIC8+PGcgID48ZyB0ZXh0LXJlbmRlcmluZz0iZ2VvbWV0cmljUHJlY2lzaW9uIiBjb2xvci1yZW5kZXJpbmc9Im9wdGltaXplUXVhbGl0eSIgY29sb3ItaW50ZXJwb2xhdGlvbj0ibGluZWFyUkdCIiBpbWFnZS1yZW5kZXJpbmc9Im9wdGltaXplU3BlZWQiICAgID48bGluZSB5Mj0iMiIgZmlsbD0ibm9uZSIgeDE9IjIiIHgyPSIxOCIgeTE9IjE4IiAgICAvPjwvZyAgPjwvZz48L3N2Zz4\x3d",
        BOND_TRIPLE: "PHN2ZyBmaWxsLW9wYWNpdHk9IjEiIHhtbG5zOnhsaW5rPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5L3hsaW5rIiBjb2xvci1yZW5kZXJpbmc9ImF1dG8iIGNvbG9yLWludGVycG9sYXRpb249ImF1dG8iIHRleHQtcmVuZGVyaW5nPSJhdXRvIiBzdHJva2U9ImJsYWNrIiBzdHJva2UtbGluZWNhcD0ic3F1YXJlIiB3aWR0aD0iMjAiIHN0cm9rZS1taXRlcmxpbWl0PSIxMCIgc2hhcGUtcmVuZGVyaW5nPSJhdXRvIiBzdHJva2Utb3BhY2l0eT0iMSIgZmlsbD0iYmxhY2siIHN0cm9rZS1kYXNoYXJyYXk9Im5vbmUiIGZvbnQtd2VpZ2h0PSJub3JtYWwiIHN0cm9rZS13aWR0aD0iMSIgdmlld0JveD0iMCAwIDIwLjAgMjAuMCIgaGVpZ2h0PSIyMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIiBmb250LWZhbWlseT0iJmFwb3M7RGlhbG9nJmFwb3M7IiBmb250LXN0eWxlPSJub3JtYWwiIHN0cm9rZS1saW5lam9pbj0ibWl0ZXIiIGZvbnQtc2l6ZT0iMTIiIHN0cm9rZS1kYXNob2Zmc2V0PSIwIiBpbWFnZS1yZW5kZXJpbmc9ImF1dG8iPjxkZWZzIGlkPSJnZW5lcmljRGVmcyIgIC8+PGcgID48ZyB0ZXh0LXJlbmRlcmluZz0iZ2VvbWV0cmljUHJlY2lzaW9uIiBjb2xvci1yZW5kZXJpbmc9Im9wdGltaXplUXVhbGl0eSIgY29sb3ItaW50ZXJwb2xhdGlvbj0ibGluZWFyUkdCIiBpbWFnZS1yZW5kZXJpbmc9Im9wdGltaXplU3BlZWQiICAgID48bGluZSB5Mj0iMSIgZmlsbD0ibm9uZSIgeDE9IjEiIHgyPSIxNSIgeTE9IjE1IiAgICAgIC8+PGxpbmUgeTI9IjMiIGZpbGw9Im5vbmUiIHgxPSIzIiB4Mj0iMTciIHkxPSIxNyIgICAgICAvPjxsaW5lIHkyPSI1IiBmaWxsPSJub25lIiB4MT0iNSIgeDI9IjE5IiB5MT0iMTkiICAgIC8+PC9nICA+PC9nPjwvc3ZnPg\x3d\x3d",
        BOND_WAVY: "PHN2ZyBmaWxsLW9wYWNpdHk9IjEiIHhtbG5zOnhsaW5rPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5L3hsaW5rIiBjb2xvci1yZW5kZXJpbmc9ImF1dG8iIGNvbG9yLWludGVycG9sYXRpb249ImF1dG8iIHRleHQtcmVuZGVyaW5nPSJhdXRvIiBzdHJva2U9ImJsYWNrIiBzdHJva2UtbGluZWNhcD0ic3F1YXJlIiB3aWR0aD0iMjAiIHN0cm9rZS1taXRlcmxpbWl0PSIxMCIgc2hhcGUtcmVuZGVyaW5nPSJhdXRvIiBzdHJva2Utb3BhY2l0eT0iMSIgZmlsbD0iYmxhY2siIHN0cm9rZS1kYXNoYXJyYXk9Im5vbmUiIGZvbnQtd2VpZ2h0PSJub3JtYWwiIHN0cm9rZS13aWR0aD0iMSIgdmlld0JveD0iMCAwIDIwLjAgMjAuMCIgaGVpZ2h0PSIyMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIiBmb250LWZhbWlseT0iJmFwb3M7RGlhbG9nJmFwb3M7IiBmb250LXN0eWxlPSJub3JtYWwiIHN0cm9rZS1saW5lam9pbj0ibWl0ZXIiIGZvbnQtc2l6ZT0iMTIiIHN0cm9rZS1kYXNob2Zmc2V0PSIwIiBpbWFnZS1yZW5kZXJpbmc9ImF1dG8iPjxkZWZzIGlkPSJnZW5lcmljRGVmcyIgIC8+PGcgID48ZyB0ZXh0LXJlbmRlcmluZz0iZ2VvbWV0cmljUHJlY2lzaW9uIiBjb2xvci1yZW5kZXJpbmc9Im9wdGltaXplUXVhbGl0eSIgY29sb3ItaW50ZXJwb2xhdGlvbj0ibGluZWFyUkdCIiBpbWFnZS1yZW5kZXJpbmc9Im9wdGltaXplU3BlZWQiICAgID48cGF0aCBmaWxsPSJub25lIiBkPSJNMiAxOCBRNy4zMDMzIDE5Ljc2NzggNS41MzU1IDE0LjQ2NDUgUTMuNzY3OCA5LjE2MTIgOS4wNzExIDEwLjkyODkgUTE0LjM3NDQgMTIuNjk2NyAxMi42MDY2IDcuMzkzNCBRMTAuODM4OCAyLjA5MDEgMTYuMTQyMSAzLjg1NzkiICAgIC8+PC9nICA+PC9nPjwvc3ZnPg\x3d\x3d",
        BOND_ZERO: "PHN2ZyBmaWxsLW9wYWNpdHk9IjEiIHhtbG5zOnhsaW5rPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5L3hsaW5rIiBjb2xvci1yZW5kZXJpbmc9ImF1dG8iIGNvbG9yLWludGVycG9sYXRpb249ImF1dG8iIHRleHQtcmVuZGVyaW5nPSJhdXRvIiBzdHJva2U9ImJsYWNrIiBzdHJva2UtbGluZWNhcD0ic3F1YXJlIiB3aWR0aD0iMjAiIHN0cm9rZS1taXRlcmxpbWl0PSIxMCIgc2hhcGUtcmVuZGVyaW5nPSJhdXRvIiBzdHJva2Utb3BhY2l0eT0iMSIgZmlsbD0iYmxhY2siIHN0cm9rZS1kYXNoYXJyYXk9Im5vbmUiIGZvbnQtd2VpZ2h0PSJub3JtYWwiIHN0cm9rZS13aWR0aD0iMSIgdmlld0JveD0iMCAwIDIwLjAgMjAuMCIgaGVpZ2h0PSIyMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIiBmb250LWZhbWlseT0iJmFwb3M7RGlhbG9nJmFwb3M7IiBmb250LXN0eWxlPSJub3JtYWwiIHN0cm9rZS1saW5lam9pbj0ibWl0ZXIiIGZvbnQtc2l6ZT0iMTIiIHN0cm9rZS1kYXNob2Zmc2V0PSIwIiBpbWFnZS1yZW5kZXJpbmc9ImF1dG8iPjxkZWZzIGlkPSJnZW5lcmljRGVmcyIgIC8+PGcgID48ZyB0ZXh0LXJlbmRlcmluZz0iZ2VvbWV0cmljUHJlY2lzaW9uIiBjb2xvci1yZW5kZXJpbmc9Im9wdGltaXplUXVhbGl0eSIgY29sb3ItaW50ZXJwb2xhdGlvbj0ibGluZWFyUkdCIiBpbWFnZS1yZW5kZXJpbmc9Im9wdGltaXplU3BlZWQiICAgID48Y2lyY2xlIHI9IjEiIGN4PSI1IiBjeT0iMTYiIHN0cm9rZT0ibm9uZSIgICAgICAvPjxjaXJjbGUgcj0iMSIgY3g9IjkiIGN5PSIxMiIgc3Ryb2tlPSJub25lIiAgICAgIC8+PGNpcmNsZSByPSIxIiBjeD0iMTMiIGN5PSI4IiBzdHJva2U9Im5vbmUiICAgICAgLz48Y2lyY2xlIHI9IjEiIGN4PSIxNyIgY3k9IjQiIHN0cm9rZT0ibm9uZSIgICAgLz48L2cgID48L2c+PC9zdmc+",
        BROMINE: "PHN2ZyBmaWxsLW9wYWNpdHk9IjEiIHhtbG5zOnhsaW5rPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5L3hsaW5rIiBjb2xvci1yZW5kZXJpbmc9ImF1dG8iIGNvbG9yLWludGVycG9sYXRpb249ImF1dG8iIHRleHQtcmVuZGVyaW5nPSJhdXRvIiBzdHJva2U9ImJsYWNrIiBzdHJva2UtbGluZWNhcD0ic3F1YXJlIiB3aWR0aD0iMjAiIHN0cm9rZS1taXRlcmxpbWl0PSIxMCIgc2hhcGUtcmVuZGVyaW5nPSJhdXRvIiBzdHJva2Utb3BhY2l0eT0iMSIgZmlsbD0iYmxhY2siIHN0cm9rZS1kYXNoYXJyYXk9Im5vbmUiIGZvbnQtd2VpZ2h0PSJub3JtYWwiIHN0cm9rZS13aWR0aD0iMSIgdmlld0JveD0iMCAwIDIwLjAgMjAuMCIgaGVpZ2h0PSIyMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIiBmb250LWZhbWlseT0iJmFwb3M7RGlhbG9nJmFwb3M7IiBmb250LXN0eWxlPSJub3JtYWwiIHN0cm9rZS1saW5lam9pbj0ibWl0ZXIiIGZvbnQtc2l6ZT0iMTIiIHN0cm9rZS1kYXNob2Zmc2V0PSIwIiBpbWFnZS1yZW5kZXJpbmc9ImF1dG8iPjxkZWZzIGlkPSJnZW5lcmljRGVmcyIgIC8+PGcgID48ZyBmb250LXNpemU9IjE0IiBmaWxsPSJyZ2IoMTY2LDQxLDQxKSIgdGV4dC1yZW5kZXJpbmc9Imdlb21ldHJpY1ByZWNpc2lvbiIgaW1hZ2UtcmVuZGVyaW5nPSJvcHRpbWl6ZVNwZWVkIiBjb2xvci1yZW5kZXJpbmc9Im9wdGltaXplUXVhbGl0eSIgZm9udC1mYW1pbHk9IiZhcG9zO0x1Y2lkYSBHcmFuZGUmYXBvczsiIHN0cm9rZT0icmdiKDE2Niw0MSw0MSkiIGNvbG9yLWludGVycG9sYXRpb249ImxpbmVhclJHQiIgICAgPjxwYXRoIGQ9Ik00LjMwNTcgMTUgTDQuMzA1NyA0Ljg4MjggTDYuOTMwNyA0Ljg4MjggUTguNDQ4MiA0Ljg4MjggOS4yNTgzIDUuNDU3IFExMC4wNjg0IDYuMDMxMiAxMC4wNjg0IDcuMTExMyBRMTAuMDY4NCA4Ljk1MDIgNy45OTAyIDkuNzI5NSBRMTAuNDcxNyAxMC40ODgzIDEwLjQ3MTcgMTIuNDcwNyBRMTAuNDcxNyAxMy43MDEyIDkuNjUxNCAxNC4zNTA2IFE4LjgzMTEgMTUgNy4yODYxIDE1IFpNNS43Mjc1IDEzLjkyNjggTDYuMDIxNSAxMy45MjY4IFE3LjYwMDYgMTMuOTI2OCA4LjA2NTQgMTMuNzI4NSBROC45NTQxIDEzLjM1MjUgOC45NTQxIDEyLjMzNCBROC45NTQxIDExLjQzMTYgOC4xNDc1IDEwLjgzMzUgUTcuMzQwOCAxMC4yMzU0IDYuMTMwOSAxMC4yMzU0IEw1LjcyNzUgMTAuMjM1NCBaTTUuNzI3NSA5LjMyNjIgTDYuMTg1NSA5LjMyNjIgUTcuMzM0IDkuMzI2MiA3Ljk2NjMgOC44MzQgUTguNTk4NiA4LjM0MTggOC41OTg2IDcuNDQ2MyBROC41OTg2IDUuOTU2MSA2LjI4ODEgNS45NTYxIEw1LjcyNzUgNS45NTYxIFpNMTIuMzQ2NyAxNSBMMTIuMzQ2NyA3LjU3NjIgTDEzLjY5MzQgNy41NzYyIEwxMy42OTM0IDguOTcwNyBRMTQuNDkzMiA3LjQxMjEgMTYuMDE3NiA3LjQxMjEgUTE2LjIyMjcgNy40MTIxIDE2LjQ0ODIgNy40NDYzIEwxNi40NDgyIDguNzA0MSBRMTYuMDk5NiA4LjU4NzkgMTUuODMzIDguNTg3OSBRMTQuNTU0NyA4LjU4NzkgMTMuNjkzNCAxMC4xMDU1IEwxMy42OTM0IDE1IFoiIHN0cm9rZT0ibm9uZSIgICAgLz48L2cgID48L2c+PC9zdmc+",
        CARBON: "PHN2ZyBmaWxsLW9wYWNpdHk9IjEiIHhtbG5zOnhsaW5rPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5L3hsaW5rIiBjb2xvci1yZW5kZXJpbmc9ImF1dG8iIGNvbG9yLWludGVycG9sYXRpb249ImF1dG8iIHRleHQtcmVuZGVyaW5nPSJhdXRvIiBzdHJva2U9ImJsYWNrIiBzdHJva2UtbGluZWNhcD0ic3F1YXJlIiB3aWR0aD0iMjAiIHN0cm9rZS1taXRlcmxpbWl0PSIxMCIgc2hhcGUtcmVuZGVyaW5nPSJhdXRvIiBzdHJva2Utb3BhY2l0eT0iMSIgZmlsbD0iYmxhY2siIHN0cm9rZS1kYXNoYXJyYXk9Im5vbmUiIGZvbnQtd2VpZ2h0PSJub3JtYWwiIHN0cm9rZS13aWR0aD0iMSIgdmlld0JveD0iMCAwIDIwLjAgMjAuMCIgaGVpZ2h0PSIyMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIiBmb250LWZhbWlseT0iJmFwb3M7RGlhbG9nJmFwb3M7IiBmb250LXN0eWxlPSJub3JtYWwiIHN0cm9rZS1saW5lam9pbj0ibWl0ZXIiIGZvbnQtc2l6ZT0iMTIiIHN0cm9rZS1kYXNob2Zmc2V0PSIwIiBpbWFnZS1yZW5kZXJpbmc9ImF1dG8iPjxkZWZzIGlkPSJnZW5lcmljRGVmcyIgIC8+PGcgID48ZyBmb250LXNpemU9IjE0IiBmaWxsPSJyZ2IoMTQ0LDE0NCwxNDQpIiB0ZXh0LXJlbmRlcmluZz0iZ2VvbWV0cmljUHJlY2lzaW9uIiBpbWFnZS1yZW5kZXJpbmc9Im9wdGltaXplU3BlZWQiIGNvbG9yLXJlbmRlcmluZz0ib3B0aW1pemVRdWFsaXR5IiBmb250LWZhbWlseT0iJmFwb3M7THVjaWRhIEdyYW5kZSZhcG9zOyIgc3Ryb2tlPSJyZ2IoMTQ0LDE0NCwxNDQpIiBjb2xvci1pbnRlcnBvbGF0aW9uPSJsaW5lYXJSR0IiICAgID48cGF0aCBkPSJNMTAuNjM5NiAxNS4yNTI5IFE4LjI4MTIgMTUuMjUyOSA2Ljk5NjEgMTMuODY4NyBRNS43MTA5IDEyLjQ4NDQgNS43MTA5IDkuOTQ4MiBRNS43MTA5IDcuNDE4OSA3LjAyIDYuMDI0NCBROC4zMjkxIDQuNjI5OSAxMC43MDggNC42Mjk5IFExMi4wNjg0IDQuNjI5OSAxMy44OTM2IDUuMDc0MiBMMTMuODkzNiA2LjQyMDkgUTExLjgxNTQgNS43MDMxIDEwLjY4NzUgNS43MDMxIFE5LjA0IDUuNzAzMSA4LjEzNzcgNi44MTc0IFE3LjIzNTQgNy45MzE2IDcuMjM1NCA5Ljk2MTkgUTcuMjM1NCAxMS44OTY1IDguMTk5MiAxMy4wMTQyIFE5LjE2MzEgMTQuMTMxOCAxMC44MzExIDE0LjEzMTggUTEyLjI2NjYgMTQuMTMxOCAxMy45MDcyIDEzLjI1IEwxMy45MDcyIDE0LjQ4MDUgUTEyLjQxMDIgMTUuMjUyOSAxMC42Mzk2IDE1LjI1MjkgWiIgc3Ryb2tlPSJub25lIiAgICAvPjwvZyAgPjwvZz48L3N2Zz4\x3d",
        CENTER: "PHN2ZyB2ZXJzaW9uPSIxLjEiIGlkPSJMYXllcl8xIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHhtbG5zOnhsaW5rPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5L3hsaW5rIiB4PSIwcHgiIHk9IjBweCIJIHZpZXdCb3g9IjAgMCAxMDAgMTAwIiBzdHlsZT0iZW5hYmxlLWJhY2tncm91bmQ6bmV3IDAgMCAxMDAgMTAwOyIgeG1sOnNwYWNlPSJwcmVzZXJ2ZSI+PGc+CTxnPgkJPGc+CQkJPGc+CQkJCTxyYWRpYWxHcmFkaWVudCBpZD0iU1ZHSURfMV8iIGN4PSI1MC4wMjczIiBjeT0iNTAuMDQ0MiIgcj0iNDkuMjQxNiIgZ3JhZGllbnRVbml0cz0idXNlclNwYWNlT25Vc2UiPgkJCQkJPHN0b3AgIG9mZnNldD0iMC42NTAzIiBzdHlsZT0ic3RvcC1jb2xvcjojMTVFMEVGIi8+CQkJCQk8c3RvcCAgb2Zmc2V0PSIwLjgwOTgiIHN0eWxlPSJzdG9wLWNvbG9yOiMwREIyREIiLz4JCQkJCTxzdG9wICBvZmZzZXQ9IjAuODUwOCIgc3R5bGU9InN0b3AtY29sb3I6IzBDQTdENSIvPgkJCQkJPHN0b3AgIG9mZnNldD0iMC45MjM3IiBzdHlsZT0ic3RvcC1jb2xvcjojMDg4OEM1Ii8+CQkJCQk8c3RvcCAgb2Zmc2V0PSIxIiBzdHlsZT0ic3RvcC1jb2xvcjojMDQ2MkIxIi8+CQkJCTwvcmFkaWFsR3JhZGllbnQ+CQkJCTxwYXRoIHN0eWxlPSJmaWxsOnVybCgjU1ZHSURfMV8pOyIgZD0iTTUwLjAyOCwwLjgwM2MtMjcuMTk3LDAtNDkuMjQzLDIyLjA0Ny00OS4yNDMsNDkuMjQJCQkJCWMwLDI3LjE5NSwyMi4wNDYsNDkuMjQyLDQ5LjI0Myw0OS4yNDJjMjcuMTkzLDAsNDkuMjQxLTIyLjA0Nyw0OS4yNDEtNDkuMjQyQzk5LjI3LDIyLjg1LDc3LjIyMiwwLjgwMyw1MC4wMjgsMC44MDN6CQkJCQkgTTUwLjAyOCw5Mi4zOTFjLTIzLjM5LDAtNDIuMzUtMTguOTU5LTQyLjM1LTQyLjM0N2MwLTIzLjM4NywxOC45NTktNDIuMzQ2LDQyLjM1LTQyLjM0NmMyMy4zODcsMCw0Mi4zNDYsMTguOTU5LDQyLjM0Niw0Mi4zNDYJCQkJCUM5Mi4zNzQsNzMuNDMyLDczLjQxNSw5Mi4zOTEsNTAuMDI4LDkyLjM5MXoiLz4JCQk8L2c+CQkJPHJhZGlhbEdyYWRpZW50IGlkPSJTVkdJRF8yXyIgY3g9IjUwLjExMzUiIGN5PSI1MC4yNTkiIHI9IjcuNjIzOCIgZ3JhZGllbnRVbml0cz0idXNlclNwYWNlT25Vc2UiPgkJCQk8c3RvcCAgb2Zmc2V0PSIwIiBzdHlsZT0ic3RvcC1jb2xvcjojRkY4Njc1Ii8+CQkJCTxzdG9wICBvZmZzZXQ9IjAuNDk2OSIgc3R5bGU9InN0b3AtY29sb3I6I0VFNDAzNiIvPgkJCQk8c3RvcCAgb2Zmc2V0PSIwLjY1ODkiIHN0eWxlPSJzdG9wLWNvbG9yOiNFMzM4MzQiLz4JCQkJPHN0b3AgIG9mZnNldD0iMC45NDYxIiBzdHlsZT0ic3RvcC1jb2xvcjojQzQyMzJFIi8+CQkJCTxzdG9wICBvZmZzZXQ9IjEiIHN0eWxlPSJzdG9wLWNvbG9yOiNCRTFFMkQiLz4JCQk8L3JhZGlhbEdyYWRpZW50PgkJCTxwYXRoIHN0eWxlPSJmaWxsOnVybCgjU1ZHSURfMl8pOyIgZD0iTTUwLjExNSw1Ny44ODNjLTQuMjExLDAtNy42MjUtMy40MTItNy42MjUtNy42MjRjMC00LjIxLDMuNDE0LTcuNjI0LDcuNjI1LTcuNjI0CQkJCWM0LjIxLDAsNy42MjMsMy40MTQsNy42MjMsNy42MjRDNTcuNzM3LDU0LjQ3MSw1NC4zMjUsNTcuODgzLDUwLjExNSw1Ny44ODN6Ii8+CQkJPGc+CQkJCTxwYXRoIHN0eWxlPSJmaWxsOm5vbmU7c3Ryb2tlOiMxNTVEOTQ7c3Ryb2tlLXdpZHRoOjEuMDE1NzsiIGQ9Ik01MC4wMjgsMC44MDNjLTI3LjE5NywwLTQ5LjI0MywyMi4wNDctNDkuMjQzLDQ5LjI0CQkJCQljMCwyNy4xOTUsMjIuMDQ2LDQ5LjI0Miw0OS4yNDMsNDkuMjQyYzI3LjE5MywwLDQ5LjI0MS0yMi4wNDcsNDkuMjQxLTQ5LjI0MkM5OS4yNywyMi44NSw3Ny4yMjIsMC44MDMsNTAuMDI4LDAuODAzegkJCQkJIE01MC4wMjgsOTMuMDU3Yy0yMy43NTgsMC00My4wMTYtMTkuMjU4LTQzLjAxNi00My4wMTNjMC0yMy43NTUsMTkuMjU4LTQzLjAxMyw0My4wMTYtNDMuMDEzCQkJCQljMjMuNzU0LDAsNDMuMDEyLDE5LjI1OCw0My4wMTIsNDMuMDEzQzkzLjA0LDczLjc5OSw3My43ODIsOTMuMDU3LDUwLjAyOCw5My4wNTd6Ii8+CQkJPC9nPgkJPC9nPgkJPHBhdGggc3R5bGU9ImZpbGw6bm9uZTtzdHJva2U6Izg2MUUyRDsiIGQ9Ik00OS43MjcsNTcuODgzYy00LjIxMSwwLTcuNjI1LTMuNDEyLTcuNjI1LTcuNjI0YzAtNC4yMSwzLjQxNC03LjYyNCw3LjYyNS03LjYyNAkJCWM0LjIxMSwwLDcuNjIxLDMuNDE0LDcuNjIxLDcuNjI0QzU3LjM0OSw1NC40NzEsNTMuOTM4LDU3Ljg4Myw0OS43MjcsNTcuODgzeiIvPgk8L2c+CTxsaW5lIHN0eWxlPSJmaWxsOm5vbmU7c3Ryb2tlOiMwMDY4Mzg7c3Ryb2tlLXdpZHRoOjU7IiB4MT0iNjIuODEzIiB5MT0iNDkuOTM0IiB4Mj0iOTAuMDYiIHkyPSI0OS45MzQiLz4JPHBvbHlsaW5lIHN0eWxlPSJmaWxsOm5vbmU7c3Ryb2tlOiMwMDY4Mzg7c3Ryb2tlLXdpZHRoOjU7IiBwb2ludHM9Ijc5LjU3LDYzLjQ4MiA2My4xMDksNDkuNjk3IDc5LjU3LDM1LjkxMSAJIi8+CTxsaW5lIHN0eWxlPSJmaWxsOm5vbmU7c3Ryb2tlOiMwMDY4Mzg7c3Ryb2tlLXdpZHRoOjU7IiB4MT0iMzYuNzQ5IiB5MT0iNDkuNDU4IiB4Mj0iOS41MDIiIHkyPSI0OS40NTgiLz4JPHBvbHlsaW5lIHN0eWxlPSJmaWxsOm5vbmU7c3Ryb2tlOiMwMDY4Mzg7c3Ryb2tlLXdpZHRoOjU7IiBwb2ludHM9IjE5Ljk5MiwzNS45MSAzNi40NTMsNDkuNjk1IDE5Ljk5Miw2My40OCAJIi8+CTxsaW5lIHN0eWxlPSJmaWxsOm5vbmU7c3Ryb2tlOiMwMDY4Mzg7c3Ryb2tlLXdpZHRoOjU7IiB4MT0iNDkuOTUiIHkxPSIzNy4zMzYiIHgyPSI0OS45NSIgeTI9IjEwLjA5Ii8+CTxwb2x5bGluZSBzdHlsZT0iZmlsbDpub25lO3N0cm9rZTojMDA2ODM4O3N0cm9rZS13aWR0aDo1OyIgcG9pbnRzPSI2My40OTcsMjAuNTggNDkuNzEyLDM3LjA0MSAzNS45MjYsMjAuNTggCSIvPgk8bGluZSBzdHlsZT0iZmlsbDpub25lO3N0cm9rZTojMDA2ODM4O3N0cm9rZS13aWR0aDo1OyIgeDE9IjQ5LjQ3MyIgeTE9IjYzLjQiIHgyPSI0OS40NzMiIHkyPSI5MC42NDYiLz4JPHBvbHlsaW5lIHN0eWxlPSJmaWxsOm5vbmU7c3Ryb2tlOiMwMDY4Mzg7c3Ryb2tlLXdpZHRoOjU7IiBwb2ludHM9IjM1LjkyNSw4MC4xNTggNDkuNzEsNjMuNjk3IDYzLjQ5Nyw4MC4xNTggCSIvPjwvZz48L3N2Zz4\x3d",
        CHAIN_CARBON: "PHN2ZyBmaWxsLW9wYWNpdHk9IjEiIHhtbG5zOnhsaW5rPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5L3hsaW5rIiBjb2xvci1yZW5kZXJpbmc9ImF1dG8iIGNvbG9yLWludGVycG9sYXRpb249ImF1dG8iIHRleHQtcmVuZGVyaW5nPSJhdXRvIiBzdHJva2U9ImJsYWNrIiBzdHJva2UtbGluZWNhcD0ic3F1YXJlIiB3aWR0aD0iMjAiIHN0cm9rZS1taXRlcmxpbWl0PSIxMCIgc2hhcGUtcmVuZGVyaW5nPSJhdXRvIiBzdHJva2Utb3BhY2l0eT0iMSIgZmlsbD0iYmxhY2siIHN0cm9rZS1kYXNoYXJyYXk9Im5vbmUiIGZvbnQtd2VpZ2h0PSJub3JtYWwiIHN0cm9rZS13aWR0aD0iMSIgdmlld0JveD0iMCAwIDIwLjAgMjAuMCIgaGVpZ2h0PSIyMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIiBmb250LWZhbWlseT0iJmFwb3M7RGlhbG9nJmFwb3M7IiBmb250LXN0eWxlPSJub3JtYWwiIHN0cm9rZS1saW5lam9pbj0ibWl0ZXIiIGZvbnQtc2l6ZT0iMTIiIHN0cm9rZS1kYXNob2Zmc2V0PSIwIiBpbWFnZS1yZW5kZXJpbmc9ImF1dG8iPjxkZWZzIGlkPSJnZW5lcmljRGVmcyIgIC8+PGcgID48ZGVmcyBpZD0iZGVmczEiICAgID48bGluZWFyR3JhZGllbnQgeDE9IjE1IiBncmFkaWVudFVuaXRzPSJ1c2VyU3BhY2VPblVzZSIgeDI9IjIwIiB5MT0iMTUiIHkyPSIyMCIgaWQ9ImxpbmVhckdyYWRpZW50MSIgc3ByZWFkTWV0aG9kPSJwYWQiICAgICAgPjxzdG9wIHN0b3Atb3BhY2l0eT0iMSIgc3RvcC1jb2xvcj0iYmx1ZSIgb2Zmc2V0PSIwJSIgICAgICAgIC8+PHN0b3Agc3RvcC1vcGFjaXR5PSIxIiBzdG9wLWNvbG9yPSJibGFjayIgb2Zmc2V0PSIxMDAlIiAgICAgIC8+PC9saW5lYXJHcmFkaWVudCAgICA+PC9kZWZzICAgID48ZyB0ZXh0LXJlbmRlcmluZz0iZ2VvbWV0cmljUHJlY2lzaW9uIiBjb2xvci1yZW5kZXJpbmc9Im9wdGltaXplUXVhbGl0eSIgY29sb3ItaW50ZXJwb2xhdGlvbj0ibGluZWFyUkdCIiBpbWFnZS1yZW5kZXJpbmc9Im9wdGltaXplU3BlZWQiICAgID48cGF0aCBmaWxsPSJub25lIiBkPSJNMCAxOSBMNSAxNiBMNSAxMSBMOSA4IEw5IDMgTDEzIDAiICAgIC8+PC9nICAgID48ZyBmb250LXNpemU9IjE1IiBmaWxsPSJ1cmwoI2xpbmVhckdyYWRpZW50MSkiIHRleHQtcmVuZGVyaW5nPSJnZW9tZXRyaWNQcmVjaXNpb24iIGltYWdlLXJlbmRlcmluZz0ib3B0aW1pemVTcGVlZCIgY29sb3ItcmVuZGVyaW5nPSJvcHRpbWl6ZVF1YWxpdHkiIGZvbnQtZmFtaWx5PSJzZXJpZiIgc3Ryb2tlPSJ1cmwoI2xpbmVhckdyYWRpZW50MSkiIGNvbG9yLWludGVycG9sYXRpb249ImxpbmVhclJHQiIgZm9udC13ZWlnaHQ9ImJvbGQiICAgID48cGF0aCBkPSJNMTIuMjQxNyAxNy42NDExIFExMi42NTE5IDE3LjU4OTggMTIuODQ1OSAxNy40MTc3IFExMy4wNCAxNy4yNDU2IDEzLjA0IDE2LjczMjkgTDEzLjA0IDEyLjMyMzcgUTEzLjA0IDExLjg2OTYgMTIuODgyNiAxMS42OTM4IFExMi43MjUxIDExLjUxODEgMTIuMjQxNyAxMS40NTk1IEwxMi4yNDE3IDExLjA5MzMgTDE1LjA4MzUgMTEuMDkzMyBMMTUuMDgzNSAxMi4xNjk5IFExNS40NDI0IDExLjYyNzkgMTUuOTk1NCAxMS4yNzI3IFExNi41NDgzIDEwLjkxNzUgMTcuMjIyMiAxMC45MTc1IFExOC4xODkgMTAuOTE3NSAxOC43MiAxMS40MTU1IFExOS4yNTEgMTEuOTEzNiAxOS4yNTEgMTMuMTY2IEwxOS4yNTEgMTYuNzkxNSBRMTkuMjUxIDE3LjI5NjkgMTkuNDIzMSAxNy40NDM0IFExOS41OTUyIDE3LjU4OTggMTkuOTk4IDE3LjY0MTEgTDE5Ljk5OCAxOCBMMTYuNDc1MSAxOCBMMTYuNDc1MSAxNy42NDExIFExNi44Nzc5IDE3LjU2MDUgMTcuMDI0NCAxNy40MjE0IFExNy4xNzA5IDE3LjI4MjIgMTcuMTcwOSAxNi43OTE1IEwxNy4xNzA5IDEzLjE1ODcgUTE3LjE3MDkgMTIuNjQ2IDE3LjA2ODQgMTIuMzg5NiBRMTYuODkyNiAxMS45MjgyIDE2LjM3MjYgMTEuOTI4MiBRMTUuOTg0NCAxMS45MjgyIDE1LjY1ODQgMTIuMjEwMiBRMTUuMzMyNSAxMi40OTIyIDE1LjE1NjcgMTIuNzc3OCBMMTUuMTU2NyAxNi43OTE1IFExNS4xNTY3IDE3LjI4MjIgMTUuMzAzMiAxNy40MjE0IFExNS40NDk3IDE3LjU2MDUgMTUuODUyNSAxNy42NDExIEwxNS44NTI1IDE4IEwxMi4yNDE3IDE4IFoiIHN0cm9rZT0ibm9uZSIgICAgLz48L2cgID48L2c+PC9zdmc+",
        CHLORINE: "PHN2ZyBmaWxsLW9wYWNpdHk9IjEiIHhtbG5zOnhsaW5rPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5L3hsaW5rIiBjb2xvci1yZW5kZXJpbmc9ImF1dG8iIGNvbG9yLWludGVycG9sYXRpb249ImF1dG8iIHRleHQtcmVuZGVyaW5nPSJhdXRvIiBzdHJva2U9ImJsYWNrIiBzdHJva2UtbGluZWNhcD0ic3F1YXJlIiB3aWR0aD0iMjAiIHN0cm9rZS1taXRlcmxpbWl0PSIxMCIgc2hhcGUtcmVuZGVyaW5nPSJhdXRvIiBzdHJva2Utb3BhY2l0eT0iMSIgZmlsbD0iYmxhY2siIHN0cm9rZS1kYXNoYXJyYXk9Im5vbmUiIGZvbnQtd2VpZ2h0PSJub3JtYWwiIHN0cm9rZS13aWR0aD0iMSIgdmlld0JveD0iMCAwIDIwLjAgMjAuMCIgaGVpZ2h0PSIyMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIiBmb250LWZhbWlseT0iJmFwb3M7RGlhbG9nJmFwb3M7IiBmb250LXN0eWxlPSJub3JtYWwiIHN0cm9rZS1saW5lam9pbj0ibWl0ZXIiIGZvbnQtc2l6ZT0iMTIiIHN0cm9rZS1kYXNob2Zmc2V0PSIwIiBpbWFnZS1yZW5kZXJpbmc9ImF1dG8iPjxkZWZzIGlkPSJnZW5lcmljRGVmcyIgIC8+PGcgID48ZyBmb250LXNpemU9IjE0IiBmaWxsPSJyZ2IoMzEsMjQwLDMxKSIgdGV4dC1yZW5kZXJpbmc9Imdlb21ldHJpY1ByZWNpc2lvbiIgaW1hZ2UtcmVuZGVyaW5nPSJvcHRpbWl6ZVNwZWVkIiBjb2xvci1yZW5kZXJpbmc9Im9wdGltaXplUXVhbGl0eSIgZm9udC1mYW1pbHk9IiZhcG9zO0x1Y2lkYSBHcmFuZGUmYXBvczsiIHN0cm9rZT0icmdiKDMxLDI0MCwzMSkiIGNvbG9yLWludGVycG9sYXRpb249ImxpbmVhclJHQiIgICAgPjxwYXRoIGQ9Ik04LjYzOTYgMTUuMjUyOSBRNi4yODEyIDE1LjI1MjkgNC45OTYxIDEzLjg2ODcgUTMuNzEwOSAxMi40ODQ0IDMuNzEwOSA5Ljk0ODIgUTMuNzEwOSA3LjQxODkgNS4wMiA2LjAyNDQgUTYuMzI5MSA0LjYyOTkgOC43MDggNC42Mjk5IFExMC4wNjg0IDQuNjI5OSAxMS44OTM2IDUuMDc0MiBMMTEuODkzNiA2LjQyMDkgUTkuODE1NCA1LjcwMzEgOC42ODc1IDUuNzAzMSBRNy4wNCA1LjcwMzEgNi4xMzc3IDYuODE3NCBRNS4yMzU0IDcuOTMxNiA1LjIzNTQgOS45NjE5IFE1LjIzNTQgMTEuODk2NSA2LjE5OTIgMTMuMDE0MiBRNy4xNjMxIDE0LjEzMTggOC44MzExIDE0LjEzMTggUTEwLjI2NjYgMTQuMTMxOCAxMS45MDcyIDEzLjI1IEwxMS45MDcyIDE0LjQ4MDUgUTEwLjQxMDIgMTUuMjUyOSA4LjYzOTYgMTUuMjUyOSBaTTE0LjM0NjcgMTUgTDE0LjM0NjcgNC4yMDYxIEwxNS42OTM0IDQuMjA2MSBMMTUuNjkzNCAxNSBaIiBzdHJva2U9Im5vbmUiICAgIC8+PC9nICA+PC9nPjwvc3ZnPg\x3d\x3d",
        CLEAR: "PHN2ZyB2ZXJzaW9uPSIxLjEiIGlkPSJMYXllcl8xIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHhtbG5zOnhsaW5rPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5L3hsaW5rIiB4PSIwcHgiIHk9IjBweCIJIHZpZXdCb3g9IjAgMCAxMDAgMTAwIiBzdHlsZT0iZW5hYmxlLWJhY2tncm91bmQ6bmV3IDAgMCAxMDAgMTAwOyIgeG1sOnNwYWNlPSJwcmVzZXJ2ZSI+PGc+CTxnPgkJPHBhdGggc3R5bGU9ImZpbGw6IzQ1NDVBRDsiIGQ9Ik00NC43NzUsMjYuMzMzIi8+CTwvZz4JPGc+CQk8Zz4JCQk8Zz4JCQkJPGxpbmVhckdyYWRpZW50IGlkPSJTVkdJRF8xXyIgZ3JhZGllbnRVbml0cz0idXNlclNwYWNlT25Vc2UiIHgxPSIzMy43Nzc2IiB5MT0iNjQuMTY3NSIgeDI9Ijc5LjM4MjUiIHkyPSI2NC4xNjc1Ij4JCQkJCTxzdG9wICBvZmZzZXQ9IjAuMDMwNyIgc3R5bGU9InN0b3AtY29sb3I6I0YwRTBEOCIvPgkJCQkJPHN0b3AgIG9mZnNldD0iMC41MDMxIiBzdHlsZT0ic3RvcC1jb2xvcjojRjVGMkYwIi8+CQkJCQk8c3RvcCAgb2Zmc2V0PSIxIiBzdHlsZT0ic3RvcC1jb2xvcjojQ0FCOEFEIi8+CQkJCTwvbGluZWFyR3JhZGllbnQ+CQkJCTxwYXRoIHN0eWxlPSJmaWxsOnVybCgjU1ZHSURfMV8pOyIgZD0iTTc3LjE3MSwzOC4wODdjLTIuOTU2LTMuNzYtNy43ODItNC4wNDUtOC41MTUtNS4zMDkJCQkJCWMtMC43MzItMS4yNTMtMC4yNTEtMy4wMzQtMC4yNTEtMy4wMzRINDQuNzU4YzAsMCwwLjQ4LDEuNzgxLTAuMjUsMy4wMzRjLTAuNzM2LDEuMjY0LTUuNTY2LDEuNTQ4LTguNTE1LDUuMzA5CQkJCQljLTIuNDM3LDMuMDkxLTIuMjEsOC42NDctMi4yMSw4LjY0N3Y0Ny4xMzVjMS4zOTQsNi4wMTYsNDQuMDU3LDYuNTY4LDQ1LjU4NSwwbDAuMDA5LTQ3LjEzNQkJCQkJQzc5LjM3Nyw0Ni43MzQsNzkuNjAzLDQxLjE3OCw3Ny4xNzEsMzguMDg3eiIvPgkJCQk8bGluZWFyR3JhZGllbnQgaWQ9IlNWR0lEXzJfIiBncmFkaWVudFVuaXRzPSJ1c2VyU3BhY2VPblVzZSIgeDE9IjMzLjc4MzIiIHkxPSI3OS4zMzIzIiB4Mj0iNzkuMzc3IiB5Mj0iNzkuMzMyMyI+CQkJCQk8c3RvcCAgb2Zmc2V0PSIwIiBzdHlsZT0ic3RvcC1jb2xvcjojQTlFM0ZCIi8+CQkJCQk8c3RvcCAgb2Zmc2V0PSIwLjgzNDQiIHN0eWxlPSJzdG9wLWNvbG9yOiMzNTkxQ0IiLz4JCQkJCTxzdG9wICBvZmZzZXQ9IjEiIHN0eWxlPSJzdG9wLWNvbG9yOiMzNTYyQ0IiLz4JCQkJPC9saW5lYXJHcmFkaWVudD4JCQkJPHBhdGggc3R5bGU9ImZpbGw6dXJsKCNTVkdJRF8yXyk7IiBkPSJNMzMuNzgzLDYwLjA3NHYzMy43OTVjMS4zOTQsNi4wMTYsNDQuMDU3LDYuNTY4LDQ1LjU4NSwwbDAuMDA5LTMzLjc5NUgzMy43ODN6Ii8+CQkJCTxwYXRoIHN0eWxlPSJmaWxsOm5vbmU7c3Ryb2tlOiMzNjM2MzY7c3Ryb2tlLXdpZHRoOjIuOTczOTsiIGQ9Ik03Ny4xNzEsMzguMDg3Yy0yLjk1Ni0zLjc2LTcuNzgyLTQuMDQ1LTguNTE1LTUuMzA5CQkJCQljLTAuNzMyLTEuMjUzLTAuMjUxLTMuMDM0LTAuMjUxLTMuMDM0SDQ0Ljc1OGMwLDAsMC40OCwxLjc4MS0wLjI1LDMuMDM0Yy0wLjczNiwxLjI2NC01LjU2NiwxLjU0OC04LjUxNSw1LjMwOQkJCQkJYy0yLjQzNywzLjA5MS0yLjIxLDguNjQ3LTIuMjEsOC42NDd2NDcuMTM1YzEuMzk0LDYuMDE2LDQ0LjA1Nyw2LjU2OCw0NS41ODUsMGwwLjAwOS00Ny4xMzUJCQkJCUM3OS4zNzcsNDYuNzM0LDc5LjYwMyw0MS4xNzgsNzcuMTcxLDM4LjA4N3oiLz4JCQk8L2c+CQkJPGc+CQkJCTxwYXRoIGQ9Ik01OS4yNDYsNy4yMjFjLTAuMDcyLTAuNTAxLTAuODcyLTQuOTM3LTUuMjQ3LTYuNTc3Yy0zLjI3Ni0xLjIyOS03LjMxMi0wLjM5OS0xMS45NjYsMi40NzMJCQkJCWMtMTMuNjI0LDguNDA0LTMxLjYwMiwyMC44NzctMzEuNjc5LDIwLjkyMWMtMC41MjIsMC4zMTktMC42NjYsMC45NDgtMC4yOSwxLjQxYzAuMzY3LDAuNDYsMS4wOTksMC41NzUsMS42MjksMC4yNTYJCQkJCWMwLjA3NC0wLjA0NCwyMC4zMjItMTAuNzAzLDMzLjc0OS0xOC40NjdjMy45NjYtMi4yOTEsNS42MzQtMi4xNjQsNi4yMS0xLjk1NGMxLjAxMiwwLjM2NiwxLjU4OCwxLjc1NywxLjc0MiwyLjQ3MXYxMy41NDQJCQkJCXYwLjY4OGMwLDAsMC4yMDcsMS4zNzIsMy4yNiwxLjQ3N2MzLjA1NSwwLjEwNSwyLjYxNi0xLjQ3NywyLjYxNi0xLjQ3N1Y3LjU1QzU5LjI3MSw3LjQ0LDU5LjI2MSw3LjMzLDU5LjI0Niw3LjIyMXoiLz4JCQk8L2c+CQkJPHBhdGggZD0iTTcxLjM4NCwyOC4yMjNjMCwxLjYxMy0xLjcxOCwyLjkyOS0zLjg0OCwyLjkyOUg0NS4xOWMtMi4xMjYsMC0zLjg0OS0xLjMxNi0zLjg0OS0yLjkyOXYtMy43MjYJCQkJYzAtMS42MTcsMS43MjMtMi45MjYsMy44NDktMi45MjZoMjIuMzQ2YzIuMTMsMCwzLjg0OCwxLjMxLDMuODQ4LDIuOTI2VjI4LjIyM3oiLz4JCQkJCQkJPGxpbmUgc3R5bGU9ImZpbGw6bm9uZTtzdHJva2U6I0ZGRkZGRjtzdHJva2Utd2lkdGg6Mi45OTk0O3N0cm9rZS1saW5lY2FwOnJvdW5kO3N0cm9rZS1saW5lam9pbjpyb3VuZDsiIHgxPSI0Ny4wNzkiIHkxPSIyOC4yNjIiIHgyPSI0Ny4wNzkiIHkyPSIyNC41MjMiLz4JCTwvZz4JPC9nPgk8bGluZSBzdHlsZT0iZmlsbDpub25lO3N0cm9rZTojMzYzNjM2O3N0cm9rZS13aWR0aDoyLjk3Mzk7IiB4MT0iNDYuOTYxIiB5MT0iNDkuMDY3IiB4Mj0iMzUuMTkxIiB5Mj0iNDkuMDY3Ii8+CTxsaW5lIHN0eWxlPSJmaWxsOm5vbmU7c3Ryb2tlOiMzNjM2MzY7c3Ryb2tlLXdpZHRoOjIuOTczOTsiIHgxPSI0Ni45NjEiIHkxPSI2Ni4wNjQiIHgyPSIzNS4xOTEiIHkyPSI2Ni4wNjQiLz4JPGxpbmUgc3R5bGU9ImZpbGw6bm9uZTtzdHJva2U6IzM2MzYzNjtzdHJva2Utd2lkdGg6Mi45NzM5OyIgeDE9IjQ2Ljk2MSIgeTE9IjgzLjA2MSIgeDI9IjM1LjE5MSIgeTI9IjgzLjA2MSIvPjwvZz48L3N2Zz4\x3d",
        CYCLOBUTANE: "PHN2ZyBmaWxsLW9wYWNpdHk9IjEiIHhtbG5zOnhsaW5rPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5L3hsaW5rIiBjb2xvci1yZW5kZXJpbmc9ImF1dG8iIGNvbG9yLWludGVycG9sYXRpb249ImF1dG8iIHRleHQtcmVuZGVyaW5nPSJhdXRvIiBzdHJva2U9ImJsYWNrIiBzdHJva2UtbGluZWNhcD0ic3F1YXJlIiB3aWR0aD0iMjAiIHN0cm9rZS1taXRlcmxpbWl0PSIxMCIgc2hhcGUtcmVuZGVyaW5nPSJhdXRvIiBzdHJva2Utb3BhY2l0eT0iMSIgZmlsbD0iYmxhY2siIHN0cm9rZS1kYXNoYXJyYXk9Im5vbmUiIGZvbnQtd2VpZ2h0PSJub3JtYWwiIHN0cm9rZS13aWR0aD0iMSIgdmlld0JveD0iMCAwIDIwLjAgMjAuMCIgaGVpZ2h0PSIyMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIiBmb250LWZhbWlseT0iJmFwb3M7RGlhbG9nJmFwb3M7IiBmb250LXN0eWxlPSJub3JtYWwiIHN0cm9rZS1saW5lam9pbj0ibWl0ZXIiIGZvbnQtc2l6ZT0iMTIiIHN0cm9rZS1kYXNob2Zmc2V0PSIwIiBpbWFnZS1yZW5kZXJpbmc9ImF1dG8iPjxkZWZzIGlkPSJnZW5lcmljRGVmcyIgIC8+PGcgID48ZyB0ZXh0LXJlbmRlcmluZz0iZ2VvbWV0cmljUHJlY2lzaW9uIiB0cmFuc2Zvcm09InRyYW5zbGF0ZSgxMCwxMCkiIGNvbG9yLXJlbmRlcmluZz0ib3B0aW1pemVRdWFsaXR5IiBjb2xvci1pbnRlcnBvbGF0aW9uPSJsaW5lYXJSR0IiIGltYWdlLXJlbmRlcmluZz0ib3B0aW1pemVTcGVlZCIgICAgPjxsaW5lIHkyPSI5IiBmaWxsPSJub25lIiB4MT0iLTkiIHgyPSItMCIgeTE9IjAiICAgICAgLz48bGluZSB5Mj0iMCIgZmlsbD0ibm9uZSIgeDE9Ii0wIiB4Mj0iOSIgeTE9IjkiICAgICAgLz48bGluZSB5Mj0iLTkiIGZpbGw9Im5vbmUiIHgxPSI5IiB4Mj0iMCIgeTE9IjAiICAgICAgLz48bGluZSB5Mj0iMCIgZmlsbD0ibm9uZSIgeDE9IjAiIHgyPSItOSIgeTE9Ii05IiAgICAvPjwvZyAgPjwvZz48L3N2Zz4\x3d",
        CYCLOHEPTANE: "PHN2ZyBmaWxsLW9wYWNpdHk9IjEiIHhtbG5zOnhsaW5rPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5L3hsaW5rIiBjb2xvci1yZW5kZXJpbmc9ImF1dG8iIGNvbG9yLWludGVycG9sYXRpb249ImF1dG8iIHRleHQtcmVuZGVyaW5nPSJhdXRvIiBzdHJva2U9ImJsYWNrIiBzdHJva2UtbGluZWNhcD0ic3F1YXJlIiB3aWR0aD0iMjAiIHN0cm9rZS1taXRlcmxpbWl0PSIxMCIgc2hhcGUtcmVuZGVyaW5nPSJhdXRvIiBzdHJva2Utb3BhY2l0eT0iMSIgZmlsbD0iYmxhY2siIHN0cm9rZS1kYXNoYXJyYXk9Im5vbmUiIGZvbnQtd2VpZ2h0PSJub3JtYWwiIHN0cm9rZS13aWR0aD0iMSIgdmlld0JveD0iMCAwIDIwLjAgMjAuMCIgaGVpZ2h0PSIyMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIiBmb250LWZhbWlseT0iJmFwb3M7RGlhbG9nJmFwb3M7IiBmb250LXN0eWxlPSJub3JtYWwiIHN0cm9rZS1saW5lam9pbj0ibWl0ZXIiIGZvbnQtc2l6ZT0iMTIiIHN0cm9rZS1kYXNob2Zmc2V0PSIwIiBpbWFnZS1yZW5kZXJpbmc9ImF1dG8iPjxkZWZzIGlkPSJnZW5lcmljRGVmcyIgIC8+PGcgID48ZyB0ZXh0LXJlbmRlcmluZz0iZ2VvbWV0cmljUHJlY2lzaW9uIiB0cmFuc2Zvcm09InRyYW5zbGF0ZSgxMCwxMCkiIGNvbG9yLXJlbmRlcmluZz0ib3B0aW1pemVRdWFsaXR5IiBjb2xvci1pbnRlcnBvbGF0aW9uPSJsaW5lYXJSR0IiIGltYWdlLXJlbmRlcmluZz0ib3B0aW1pemVTcGVlZCIgICAgPjxsaW5lIHkyPSItNS42MTE0IiBmaWxsPSJub25lIiB4MT0iLTAiIHgyPSItNy4wMzY1IiB5MT0iLTkiICAgICAgLz48bGluZSB5Mj0iMi4wMDI3IiBmaWxsPSJub25lIiB4MT0iLTcuMDM2NSIgeDI9Ii04Ljc3NDQiIHkxPSItNS42MTE0IiAgICAgIC8+PGxpbmUgeTI9IjguMTA4NyIgZmlsbD0ibm9uZSIgeDE9Ii04Ljc3NDQiIHgyPSItMy45MDUiIHkxPSIyLjAwMjciICAgICAgLz48bGluZSB5Mj0iOC4xMDg3IiBmaWxsPSJub25lIiB4MT0iLTMuOTA1IiB4Mj0iMy45MDUiIHkxPSI4LjEwODciICAgICAgLz48bGluZSB5Mj0iMi4wMDI3IiBmaWxsPSJub25lIiB4MT0iMy45MDUiIHgyPSI4Ljc3NDQiIHkxPSI4LjEwODciICAgICAgLz48bGluZSB5Mj0iLTUuNjExNCIgZmlsbD0ibm9uZSIgeDE9IjguNzc0NCIgeDI9IjcuMDM2NSIgeTE9IjIuMDAyNyIgICAgICAvPjxsaW5lIHkyPSItOSIgZmlsbD0ibm9uZSIgeDE9IjcuMDM2NSIgeDI9Ii0wIiB5MT0iLTUuNjExNCIgICAgLz48L2cgID48L2c+PC9zdmc+",
        CYCLOHEXANE: "PHN2ZyBmaWxsLW9wYWNpdHk9IjEiIHhtbG5zOnhsaW5rPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5L3hsaW5rIiBjb2xvci1yZW5kZXJpbmc9ImF1dG8iIGNvbG9yLWludGVycG9sYXRpb249ImF1dG8iIHRleHQtcmVuZGVyaW5nPSJhdXRvIiBzdHJva2U9ImJsYWNrIiBzdHJva2UtbGluZWNhcD0ic3F1YXJlIiB3aWR0aD0iMjAiIHN0cm9rZS1taXRlcmxpbWl0PSIxMCIgc2hhcGUtcmVuZGVyaW5nPSJhdXRvIiBzdHJva2Utb3BhY2l0eT0iMSIgZmlsbD0iYmxhY2siIHN0cm9rZS1kYXNoYXJyYXk9Im5vbmUiIGZvbnQtd2VpZ2h0PSJub3JtYWwiIHN0cm9rZS13aWR0aD0iMSIgdmlld0JveD0iMCAwIDIwLjAgMjAuMCIgaGVpZ2h0PSIyMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIiBmb250LWZhbWlseT0iJmFwb3M7RGlhbG9nJmFwb3M7IiBmb250LXN0eWxlPSJub3JtYWwiIHN0cm9rZS1saW5lam9pbj0ibWl0ZXIiIGZvbnQtc2l6ZT0iMTIiIHN0cm9rZS1kYXNob2Zmc2V0PSIwIiBpbWFnZS1yZW5kZXJpbmc9ImF1dG8iPjxkZWZzIGlkPSJnZW5lcmljRGVmcyIgIC8+PGcgID48ZyB0ZXh0LXJlbmRlcmluZz0iZ2VvbWV0cmljUHJlY2lzaW9uIiB0cmFuc2Zvcm09InRyYW5zbGF0ZSgxMCwxMCkiIGNvbG9yLXJlbmRlcmluZz0ib3B0aW1pemVRdWFsaXR5IiBjb2xvci1pbnRlcnBvbGF0aW9uPSJsaW5lYXJSR0IiIGltYWdlLXJlbmRlcmluZz0ib3B0aW1pemVTcGVlZCIgICAgPjxsaW5lIHkyPSI4LjUiIGZpbGw9Im5vbmUiIHgxPSItNy4zNjEyIiB4Mj0iLTAiIHkxPSI0LjI1IiAgICAgIC8+PGxpbmUgeTI9IjQuMjUiIGZpbGw9Im5vbmUiIHgxPSItMCIgeDI9IjcuMzYxMiIgeTE9IjguNSIgICAgICAvPjxsaW5lIHkyPSItNC4yNSIgZmlsbD0ibm9uZSIgeDE9IjcuMzYxMiIgeDI9IjcuMzYxMiIgeTE9IjQuMjUiICAgICAgLz48bGluZSB5Mj0iLTguNSIgZmlsbD0ibm9uZSIgeDE9IjcuMzYxMiIgeDI9IjAiIHkxPSItNC4yNSIgICAgICAvPjxsaW5lIHkyPSItNC4yNSIgZmlsbD0ibm9uZSIgeDE9IjAiIHgyPSItNy4zNjEyIiB5MT0iLTguNSIgICAgICAvPjxsaW5lIHkyPSI0LjI1IiBmaWxsPSJub25lIiB4MT0iLTcuMzYxMiIgeDI9Ii03LjM2MTIiIHkxPSItNC4yNSIgICAgLz48L2cgID48L2c+PC9zdmc+",
        CYCLOOCTANE: "PHN2ZyBmaWxsLW9wYWNpdHk9IjEiIHhtbG5zOnhsaW5rPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5L3hsaW5rIiBjb2xvci1yZW5kZXJpbmc9ImF1dG8iIGNvbG9yLWludGVycG9sYXRpb249ImF1dG8iIHRleHQtcmVuZGVyaW5nPSJhdXRvIiBzdHJva2U9ImJsYWNrIiBzdHJva2UtbGluZWNhcD0ic3F1YXJlIiB3aWR0aD0iMjAiIHN0cm9rZS1taXRlcmxpbWl0PSIxMCIgc2hhcGUtcmVuZGVyaW5nPSJhdXRvIiBzdHJva2Utb3BhY2l0eT0iMSIgZmlsbD0iYmxhY2siIHN0cm9rZS1kYXNoYXJyYXk9Im5vbmUiIGZvbnQtd2VpZ2h0PSJub3JtYWwiIHN0cm9rZS13aWR0aD0iMSIgdmlld0JveD0iMCAwIDIwLjAgMjAuMCIgaGVpZ2h0PSIyMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIiBmb250LWZhbWlseT0iJmFwb3M7RGlhbG9nJmFwb3M7IiBmb250LXN0eWxlPSJub3JtYWwiIHN0cm9rZS1saW5lam9pbj0ibWl0ZXIiIGZvbnQtc2l6ZT0iMTIiIHN0cm9rZS1kYXNob2Zmc2V0PSIwIiBpbWFnZS1yZW5kZXJpbmc9ImF1dG8iPjxkZWZzIGlkPSJnZW5lcmljRGVmcyIgIC8+PGcgID48ZyB0ZXh0LXJlbmRlcmluZz0iZ2VvbWV0cmljUHJlY2lzaW9uIiB0cmFuc2Zvcm09InRyYW5zbGF0ZSgxMCwxMCkiIGNvbG9yLXJlbmRlcmluZz0ib3B0aW1pemVRdWFsaXR5IiBjb2xvci1pbnRlcnBvbGF0aW9uPSJsaW5lYXJSR0IiIGltYWdlLXJlbmRlcmluZz0ib3B0aW1pemVTcGVlZCIgICAgPjxsaW5lIHkyPSI2LjM2NCIgZmlsbD0ibm9uZSIgeDE9Ii05IiB4Mj0iLTYuMzY0IiB5MT0iMCIgICAgICAvPjxsaW5lIHkyPSI5IiBmaWxsPSJub25lIiB4MT0iLTYuMzY0IiB4Mj0iLTAiIHkxPSI2LjM2NCIgICAgICAvPjxsaW5lIHkyPSI2LjM2NCIgZmlsbD0ibm9uZSIgeDE9Ii0wIiB4Mj0iNi4zNjQiIHkxPSI5IiAgICAgIC8+PGxpbmUgeTI9IjAiIGZpbGw9Im5vbmUiIHgxPSI2LjM2NCIgeDI9IjkiIHkxPSI2LjM2NCIgICAgICAvPjxsaW5lIHkyPSItNi4zNjQiIGZpbGw9Im5vbmUiIHgxPSI5IiB4Mj0iNi4zNjQiIHkxPSIwIiAgICAgIC8+PGxpbmUgeTI9Ii05IiBmaWxsPSJub25lIiB4MT0iNi4zNjQiIHgyPSIwIiB5MT0iLTYuMzY0IiAgICAgIC8+PGxpbmUgeTI9Ii02LjM2NCIgZmlsbD0ibm9uZSIgeDE9IjAiIHgyPSItNi4zNjQiIHkxPSItOSIgICAgICAvPjxsaW5lIHkyPSIwIiBmaWxsPSJub25lIiB4MT0iLTYuMzY0IiB4Mj0iLTkiIHkxPSItNi4zNjQiICAgIC8+PC9nICA+PC9nPjwvc3ZnPg\x3d\x3d",
        CYCLOPENTANE: "PHN2ZyBmaWxsLW9wYWNpdHk9IjEiIHhtbG5zOnhsaW5rPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5L3hsaW5rIiBjb2xvci1yZW5kZXJpbmc9ImF1dG8iIGNvbG9yLWludGVycG9sYXRpb249ImF1dG8iIHRleHQtcmVuZGVyaW5nPSJhdXRvIiBzdHJva2U9ImJsYWNrIiBzdHJva2UtbGluZWNhcD0ic3F1YXJlIiB3aWR0aD0iMjAiIHN0cm9rZS1taXRlcmxpbWl0PSIxMCIgc2hhcGUtcmVuZGVyaW5nPSJhdXRvIiBzdHJva2Utb3BhY2l0eT0iMSIgZmlsbD0iYmxhY2siIHN0cm9rZS1kYXNoYXJyYXk9Im5vbmUiIGZvbnQtd2VpZ2h0PSJub3JtYWwiIHN0cm9rZS13aWR0aD0iMSIgdmlld0JveD0iMCAwIDIwLjAgMjAuMCIgaGVpZ2h0PSIyMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIiBmb250LWZhbWlseT0iJmFwb3M7RGlhbG9nJmFwb3M7IiBmb250LXN0eWxlPSJub3JtYWwiIHN0cm9rZS1saW5lam9pbj0ibWl0ZXIiIGZvbnQtc2l6ZT0iMTIiIHN0cm9rZS1kYXNob2Zmc2V0PSIwIiBpbWFnZS1yZW5kZXJpbmc9ImF1dG8iPjxkZWZzIGlkPSJnZW5lcmljRGVmcyIgIC8+PGcgID48ZyB0ZXh0LXJlbmRlcmluZz0iZ2VvbWV0cmljUHJlY2lzaW9uIiB0cmFuc2Zvcm09InRyYW5zbGF0ZSgxMCwxMCkiIGNvbG9yLXJlbmRlcmluZz0ib3B0aW1pemVRdWFsaXR5IiBjb2xvci1pbnRlcnBvbGF0aW9uPSJsaW5lYXJSR0IiIGltYWdlLXJlbmRlcmluZz0ib3B0aW1pemVTcGVlZCIgICAgPjxsaW5lIHkyPSItMi43ODEyIiBmaWxsPSJub25lIiB4MT0iLTAiIHgyPSItOC41NTk1IiB5MT0iLTkiICAgICAgLz48bGluZSB5Mj0iNy4yODEyIiBmaWxsPSJub25lIiB4MT0iLTguNTU5NSIgeDI9Ii01LjI5MDEiIHkxPSItMi43ODEyIiAgICAgIC8+PGxpbmUgeTI9IjcuMjgxMiIgZmlsbD0ibm9uZSIgeDE9Ii01LjI5MDEiIHgyPSI1LjI5MDEiIHkxPSI3LjI4MTIiICAgICAgLz48bGluZSB5Mj0iLTIuNzgxMiIgZmlsbD0ibm9uZSIgeDE9IjUuMjkwMSIgeDI9IjguNTU5NSIgeTE9IjcuMjgxMiIgICAgICAvPjxsaW5lIHkyPSItOSIgZmlsbD0ibm9uZSIgeDE9IjguNTU5NSIgeDI9Ii0wIiB5MT0iLTIuNzgxMiIgICAgLz48L2cgID48L2c+PC9zdmc+",
        CYCLOPROPANE: "PHN2ZyBmaWxsLW9wYWNpdHk9IjEiIHhtbG5zOnhsaW5rPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5L3hsaW5rIiBjb2xvci1yZW5kZXJpbmc9ImF1dG8iIGNvbG9yLWludGVycG9sYXRpb249ImF1dG8iIHRleHQtcmVuZGVyaW5nPSJhdXRvIiBzdHJva2U9ImJsYWNrIiBzdHJva2UtbGluZWNhcD0ic3F1YXJlIiB3aWR0aD0iMjAiIHN0cm9rZS1taXRlcmxpbWl0PSIxMCIgc2hhcGUtcmVuZGVyaW5nPSJhdXRvIiBzdHJva2Utb3BhY2l0eT0iMSIgZmlsbD0iYmxhY2siIHN0cm9rZS1kYXNoYXJyYXk9Im5vbmUiIGZvbnQtd2VpZ2h0PSJub3JtYWwiIHN0cm9rZS13aWR0aD0iMSIgdmlld0JveD0iMCAwIDIwLjAgMjAuMCIgaGVpZ2h0PSIyMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIiBmb250LWZhbWlseT0iJmFwb3M7RGlhbG9nJmFwb3M7IiBmb250LXN0eWxlPSJub3JtYWwiIHN0cm9rZS1saW5lam9pbj0ibWl0ZXIiIGZvbnQtc2l6ZT0iMTIiIHN0cm9rZS1kYXNob2Zmc2V0PSIwIiBpbWFnZS1yZW5kZXJpbmc9ImF1dG8iPjxkZWZzIGlkPSJnZW5lcmljRGVmcyIgIC8+PGcgID48ZyB0ZXh0LXJlbmRlcmluZz0iZ2VvbWV0cmljUHJlY2lzaW9uIiB0cmFuc2Zvcm09InRyYW5zbGF0ZSgxMCwxMCkgcm90YXRlKDkwKSB0cmFuc2xhdGUoMiwwKSIgY29sb3ItcmVuZGVyaW5nPSJvcHRpbWl6ZVF1YWxpdHkiIGNvbG9yLWludGVycG9sYXRpb249ImxpbmVhclJHQiIgaW1hZ2UtcmVuZGVyaW5nPSJvcHRpbWl6ZVNwZWVkIiAgICA+PGxpbmUgeTI9IjcuNzk0MiIgZmlsbD0ibm9uZSIgeDE9Ii05IiB4Mj0iNC41IiB5MT0iMCIgICAgICAvPjxsaW5lIHkyPSItNy43OTQyIiBmaWxsPSJub25lIiB4MT0iNC41IiB4Mj0iNC41IiB5MT0iNy43OTQyIiAgICAgIC8+PGxpbmUgeTI9IjAiIGZpbGw9Im5vbmUiIHgxPSI0LjUiIHgyPSItOSIgeTE9Ii03Ljc5NDIiICAgIC8+PC9nICA+PC9nPjwvc3ZnPg\x3d\x3d",
        DECREASE_CHARGE: "PHN2ZyBmaWxsLW9wYWNpdHk9IjEiIHhtbG5zOnhsaW5rPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5L3hsaW5rIiBjb2xvci1yZW5kZXJpbmc9ImF1dG8iIGNvbG9yLWludGVycG9sYXRpb249ImF1dG8iIHRleHQtcmVuZGVyaW5nPSJhdXRvIiBzdHJva2U9ImJsYWNrIiBzdHJva2UtbGluZWNhcD0ic3F1YXJlIiB3aWR0aD0iMjAiIHN0cm9rZS1taXRlcmxpbWl0PSIxMCIgc2hhcGUtcmVuZGVyaW5nPSJhdXRvIiBzdHJva2Utb3BhY2l0eT0iMSIgZmlsbD0iYmxhY2siIHN0cm9rZS1kYXNoYXJyYXk9Im5vbmUiIGZvbnQtd2VpZ2h0PSJub3JtYWwiIHN0cm9rZS13aWR0aD0iMSIgdmlld0JveD0iMCAwIDIwLjAgMjAuMCIgaGVpZ2h0PSIyMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIiBmb250LWZhbWlseT0iJmFwb3M7RGlhbG9nJmFwb3M7IiBmb250LXN0eWxlPSJub3JtYWwiIHN0cm9rZS1saW5lam9pbj0ibWl0ZXIiIGZvbnQtc2l6ZT0iMTIiIHN0cm9rZS1kYXNob2Zmc2V0PSIwIiBpbWFnZS1yZW5kZXJpbmc9ImF1dG8iPjxkZWZzIGlkPSJnZW5lcmljRGVmcyIgIC8+PGcgID48ZyBzdHJva2UtbGluZWNhcD0iYnV0dCIgdGV4dC1yZW5kZXJpbmc9Imdlb21ldHJpY1ByZWNpc2lvbiIgY29sb3ItcmVuZGVyaW5nPSJvcHRpbWl6ZVF1YWxpdHkiIGltYWdlLXJlbmRlcmluZz0ib3B0aW1pemVTcGVlZCIgc3Ryb2tlLWxpbmVqb2luPSJiZXZlbCIgY29sb3ItaW50ZXJwb2xhdGlvbj0ibGluZWFyUkdCIiBzdHJva2Utd2lkdGg9IjEuMiIgICAgPjxsaW5lIHkyPSIxMCIgZmlsbD0ibm9uZSIgeDE9IjYiIHgyPSIxNCIgeTE9IjEwIiAgICAgIC8+PGNpcmNsZSBmaWxsPSJub25lIiByPSI2IiBjeD0iMTAiIGN5PSIxMCIgICAgLz48L2cgID48L2c+PC9zdmc+",
        ERASE: "PHN2ZyB2ZXJzaW9uPSIxLjEiIGlkPSJMYXllcl8xIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHhtbG5zOnhsaW5rPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5L3hsaW5rIiB4PSIwcHgiIHk9IjBweCIJIHZpZXdCb3g9IjAgMCAxMDAgMTAwIiBzdHlsZT0iZW5hYmxlLWJhY2tncm91bmQ6bmV3IDAgMCAxMDAgMTAwOyIgeG1sOnNwYWNlPSJwcmVzZXJ2ZSI+PGc+CTxwYXRoIHN0eWxlPSJmaWxsOiNBMDY4N0I7c3Ryb2tlOiM5NTM4NUM7c3Ryb2tlLXdpZHRoOjIuNDgwMjsiIGQ9Ik0yNC4zMiw5OC4yNThjMCwwLDAuNDQ1LDEuMDA2LDYuMzc5LTIuNjk1CQljMi4xNTMtMS4zNDMsNTMuMTg4LTQxLjE2Myw1Ni41NDUtNDQuNDI1YzIuNjQ4LTIuNTczLDMuMjgzLTMuNTAzLDQuNjYxLTYuODk3YzEuMDk0LTIuNjgsNS42ODktMTQuMTQ4LDYuMDA0LTE0Ljg3MgkJYzAuMzEtMC43MTgsMS4wOTgtMy42NjIsMC42NDgtNS44NzJjLTAuNDM4LTIuMjEzLTAuOTA1LTMuNzA4LTIuOTE0LTUuNjNDOTMuNjMzLDE1Ljk1LDMwLjYxMiw2Ny41NywzMC42MTIsNjcuNTdMMjQuMzIsOTguMjU4eiIJCS8+CQkJPGxpbmVhckdyYWRpZW50IGlkPSJTVkdJRF8xXyIgZ3JhZGllbnRVbml0cz0idXNlclNwYWNlT25Vc2UiIHgxPSI3NC43MzAyIiB5MT0iLTM4LjI4NTQiIHgyPSItMTYuMjE5NiIgeTI9Ii0zOC4yODU0IiBncmFkaWVudFRyYW5zZm9ybT0ibWF0cml4KDAuOTMyNyAtMC4zNjA2IDAuMzYwNiAwLjkzMjcgNDEuODEwMiA4My44NTA0KSI+CQk8c3RvcCAgb2Zmc2V0PSIwIiBzdHlsZT0ic3RvcC1jb2xvcjojRjI5RUJFIi8+CQk8c3RvcCAgb2Zmc2V0PSIwLjI3NDMiIHN0eWxlPSJzdG9wLWNvbG9yOiNGM0EyQzEiLz4JCTxzdG9wICBvZmZzZXQ9IjAuNTM5MSIgc3R5bGU9InN0b3AtY29sb3I6I0Y2QURDOSIvPgkJPHN0b3AgIG9mZnNldD0iMC43OTk0IiBzdHlsZT0ic3RvcC1jb2xvcjojRkFDMUQ3Ii8+CQk8c3RvcCAgb2Zmc2V0PSIwLjk4OSIgc3R5bGU9InN0b3AtY29sb3I6I0ZGRDRFNSIvPgk8L2xpbmVhckdyYWRpZW50Pgk8cGF0aCBzdHlsZT0iZmlsbDp1cmwoI1NWR0lEXzFfKTtzdHJva2U6I0QwNjc5MDtzdHJva2Utd2lkdGg6Mi40ODAyO3N0cm9rZS1saW5lY2FwOnJvdW5kO3N0cm9rZS1saW5lam9pbjpyb3VuZDsiIGQ9IgkJTTExLjExMSw0OS40MjVMNjcuOTc2LDQuNjQ0YzAsMCwzLjYxOS0zLjIzNiw2Ljg2OC0zLjMzN2MzLjI0NC0wLjEsNC40NTcsMS42MSw2Ljc3OCwzLjY2OQkJQzgzLjk0LDcuMDQ0LDk1LjA2OCwxNy4xNTIsOTYuMDkxLDE4LjM0YzEuMDI5LDEuMTgzLDIuNTY4LDMuNzU5LDEuMzY1LDYuMjI2Yy0xLjE4OCwyLjQ3Mi0xLjkwMSwzLjE1NC01Ljc1NCw2LjI4MwkJYy0zLjg0NSwzLjEzNC01NC41MTEsNDIuODQ5LTU0LjUxMSw0Mi44NDlMMTEuMTExLDQ5LjQyNXoiLz4JCQk8bGluZWFyR3JhZGllbnQgaWQ9IlNWR0lEXzJfIiBncmFkaWVudFVuaXRzPSJ1c2VyU3BhY2VPblVzZSIgeDE9Ii0wLjY0NjgiIHkxPSItMTcuODU0MSIgeDI9Ii0zNS4xOTU5IiB5Mj0iLTE3Ljg1NDEiIGdyYWRpZW50VHJhbnNmb3JtPSJtYXRyaXgoMC45MzI3IC0wLjM2MDYgMC4zNjA2IDAuOTMyNyA0MS44MTAyIDgzLjg1MDQpIj4JCTxzdG9wICBvZmZzZXQ9IjAuMDExIiBzdHlsZT0ic3RvcC1jb2xvcjojRTA4NkE3Ii8+CQk8c3RvcCAgb2Zmc2V0PSIwLjE3MDIiIHN0eWxlPSJzdG9wLWNvbG9yOiNFODk1QjQiLz4JCTxzdG9wICBvZmZzZXQ9IjAuNDQwMyIgc3R5bGU9InN0b3AtY29sb3I6I0YzQTlDNSIvPgkJPHN0b3AgIG9mZnNldD0iMC43MTUzIiBzdHlsZT0ic3RvcC1jb2xvcjojRkFCNENGIi8+CQk8c3RvcCAgb2Zmc2V0PSIxIiBzdHlsZT0ic3RvcC1jb2xvcjojRkNCOEQyIi8+CTwvbGluZWFyR3JhZGllbnQ+CTxwYXRoIHN0eWxlPSJmaWxsOnVybCgjU1ZHSURfMl8pO3N0cm9rZTojRDA2NzkwO3N0cm9rZS13aWR0aDoyLjQ4MDI7c3Ryb2tlLWxpbmVjYXA6cm91bmQ7c3Ryb2tlLWxpbmVqb2luOnJvdW5kOyIgZD0iCQlNMTEuMTExLDQ5LjQyNWMwLDAtNC43MzIsMTAuMDU1LTYuMTQyLDE0LjAwNmMtMS40MjIsMy45NTUtMi42OTgsNy4yNTQtMy4wODMsOC44MDVjLTAuMzc4LDEuNTQ2LTAuODM5LDIuOTI0LTAuMzU0LDQuNzI1CQljMC40ODMsMS43OTcsMS4xMzMsMy41MzUsMi42MjIsNC45MzNjMS40OSwxLjM5OCwxNC42MjYsMTQuMjksMTUuNDU1LDE0Ljk2YzAuODMyLDAuNjY4LDMuMDM5LDIuOTc0LDYuMzc3LDEuMDQyCQljMy4xNTMtMS44MjYsMTEuMjA2LTI0LjE5NywxMS4yMDYtMjQuMTk3TDExLjExMSw0OS40MjV6Ii8+CQkJPGxpbmVhckdyYWRpZW50IGlkPSJTVkdJRF8zXyIgZ3JhZGllbnRVbml0cz0idXNlclNwYWNlT25Vc2UiIHgxPSI2MTAuMTA4NyIgeTE9Ii0zMjUuMDI4MSIgeDI9IjY3My4xMTgyIiB5Mj0iLTMyNS4wMjgxIiBncmFkaWVudFRyYW5zZm9ybT0ibWF0cml4KDAuOTk2MiAwLjA4NzQgLTAuMDg3NCAwLjk5NjIgLTYyMS4xMjkyIDI5NS45NDc1KSI+CQk8c3RvcCAgb2Zmc2V0PSIwLjAxMjMiIHN0eWxlPSJzdG9wLWNvbG9yOiNGRkZGRkYiLz4JCTxzdG9wICBvZmZzZXQ9IjAuNTc2NyIgc3R5bGU9InN0b3AtY29sb3I6I0ZGRDRFNSIvPgkJPHN0b3AgIG9mZnNldD0iMC42ODM2IiBzdHlsZT0ic3RvcC1jb2xvcjojRkNEMUUyIi8+CQk8c3RvcCAgb2Zmc2V0PSIxIiBzdHlsZT0ic3RvcC1jb2xvcjojRjhDRURGIi8+CTwvbGluZWFyR3JhZGllbnQ+CTxwYXRoIHN0eWxlPSJmaWxsOnVybCgjU1ZHSURfM18pOyIgZD0iTTEyLjk2OSw0OS40MTJjMCwwLDU3Ljg0LTQ1LjcyNyw1OS4yMDctNDYuMjY3YzEuMzY3LTAuNTM5LDEuMjYtMC44NCwzLjE3Ny0wLjY2NAkJYzEuOTEyLDAuMTc1LDMuNTA1LDEuNTI3LDMuNTA1LDEuNTI3bDEuMjM0LDEuMjk1YzAsMC0xLjg4NiwxLjQwOS0zLjM1NiwyLjU4MWMtMS45MDIsMS41MDgtNTguNzExLDQ2LjE0LTU4LjcxMSw0Ni4xNAkJTDEyLjk2OSw0OS40MTJ6Ii8+CQkJPGxpbmVhckdyYWRpZW50IGlkPSJTVkdJRF80XyIgZ3JhZGllbnRVbml0cz0idXNlclNwYWNlT25Vc2UiIHgxPSIyMzAuMjk3MSIgeTE9Ii0xMjcuNjk1NyIgeDI9IjI0Ny43NjkzIiB5Mj0iLTEyNy42OTU3IiBncmFkaWVudFRyYW5zZm9ybT0ibWF0cml4KDAuOTgzOSAtMC4xNzg1IDAuMTc4NSAwLjk4MzkgLTIwMi43ODkxIDIzNC44MTk0KSI+CQk8c3RvcCAgb2Zmc2V0PSIwLjAxMjMiIHN0eWxlPSJzdG9wLWNvbG9yOiNGRkZGRkYiLz4JCTxzdG9wICBvZmZzZXQ9IjAuNTc2NyIgc3R5bGU9InN0b3AtY29sb3I6I0ZGRDRFNSIvPgkJPHN0b3AgIG9mZnNldD0iMC42ODM2IiBzdHlsZT0ic3RvcC1jb2xvcjojRkNEMUUyIi8+CQk8c3RvcCAgb2Zmc2V0PSIxIiBzdHlsZT0ic3RvcC1jb2xvcjojRjhDRURGIi8+CTwvbGluZWFyR3JhZGllbnQ+CTxwYXRoIHN0eWxlPSJmaWxsOnVybCgjU1ZHSURfNF8pOyIgZD0iTTExLjU4Nyw1MS41OTNsNS4wMjMsNC42MDlMNS45OTEsODEuNzI3YzAsMC0zLjQ2Ny0yLjQxNi0zLjUwNC01LjkzMQkJQzIuNDU4LDczLjAyNSw1Ljg5Myw2My40ODQsMTEuNTg3LDUxLjU5M3oiLz4JCQk8bGluZWFyR3JhZGllbnQgaWQ9IlNWR0lEXzVfIiBncmFkaWVudFVuaXRzPSJ1c2VyU3BhY2VPblVzZSIgeDE9IjYxMC4yMDY2IiB5MT0iLTMyNi42OTEzIiB4Mj0iNjY1LjA0NDEiIHkyPSItMzI2LjY5MTMiIGdyYWRpZW50VHJhbnNmb3JtPSJtYXRyaXgoMC45OTYyIDAuMDg3NCAtMC4wODc0IDAuOTk2MiAtNjIxLjEyOTIgMjk1Ljk0NzUpIj4JCTxzdG9wICBvZmZzZXQ9IjAuMDEyMyIgc3R5bGU9InN0b3AtY29sb3I6I0ZGRkZGRiIvPgkJPHN0b3AgIG9mZnNldD0iMC41NzY3IiBzdHlsZT0ic3RvcC1jb2xvcjojRkZENEU1Ii8+CQk8c3RvcCAgb2Zmc2V0PSIwLjY4MzYiIHN0eWxlPSJzdG9wLWNvbG9yOiNGQ0QxRTIiLz4JCTxzdG9wICBvZmZzZXQ9IjEiIHN0eWxlPSJzdG9wLWNvbG9yOiNGOENFREYiLz4JPC9saW5lYXJHcmFkaWVudD4JPHBhdGggc3R5bGU9ImZpbGw6dXJsKCNTVkdJRF81Xyk7IiBkPSJNMTMuMDc2LDQ5LjMwN2MwLDAsNTcuMDY1LTQ1LjQ3OSw1OS4xLTQ2LjE2MiIvPjwvZz48L3N2Zz4\x3d",
        FLIP_HOR: "PHN2ZyB2ZXJzaW9uPSIxLjEiIGlkPSJMYXllcl8xIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHhtbG5zOnhsaW5rPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5L3hsaW5rIiB4PSIwcHgiIHk9IjBweCIJIHZpZXdCb3g9IjAgMCAxMDAgMTAwIiBzdHlsZT0iZW5hYmxlLWJhY2tncm91bmQ6bmV3IDAgMCAxMDAgMTAwOyIgeG1sOnNwYWNlPSJwcmVzZXJ2ZSI+PGc+CTxnPgkJPHBhdGggc3R5bGU9ImZpbGw6IzFCNzVCODsiIGQ9Ik04Mi44MjgsNjIuNjQ4TDU1LjQzLDUzLjA3VjIyLjY0M2wyNy4zOTgtOS41NzhsMTYuNzQsMjQuNzkyTDgyLjgyOCw2Mi42NDhMODIuODI4LDYyLjY0OHoJCQkgTTYyLjQ5OCw0OC4wNTNsMTcuNTIxLDYuMTI1bDExLjAyMS0xNi4zMjFMODAuMDE5LDIxLjUzNUw2Mi40OTgsMjcuNjZWNDguMDUzTDYyLjQ5OCw0OC4wNTN6Ii8+CTwvZz4JPGc+CQk8cGF0aCBzdHlsZT0iZmlsbDojMUI3NUI4OyIgZD0iTTE4LjAzOSw2Mi42NDhMMS4yOTcsMzcuODU2bDE2Ljc0Mi0yNC43OTJsMjcuMzk5LDkuNTc4VjUzLjA3TDE4LjAzOSw2Mi42NDhMMTguMDM5LDYyLjY0OHoJCQkgTTkuODI3LDM3Ljg1NmwxMS4wMjIsMTYuMzIxbDE3LjUyMS02LjEyNVYyNy42NmwtMTcuNTIxLTYuMTI1TDkuODI3LDM3Ljg1Nkw5LjgyNywzNy44NTZ6Ii8+CTwvZz4JPGc+CQk8cGF0aCBkPSJNNTIuODY4LDY4LjQyOWgtNS4xODdWNTQuOTQ0aDUuMTg3VjY4LjQyOUw1Mi44NjgsNjguNDI5eiBNNTIuODY4LDQxLjQ2aC01LjE4N1YyNy45NzVoNS4xODdWNDEuNDZMNTIuODY4LDQxLjQ2egkJCSBNNTIuODY4LDE0LjQ5aC01LjE4N1YxLjAwNmg1LjE4N1YxNC40OUw1Mi44NjgsMTQuNDl6Ii8+CTwvZz4JPGc+CQk8cG9seWdvbiBwb2ludHM9IjU5LjUyNyw3Ny41MDcgOTEuNjgyLDY2LjI2NiA4My40MTQsOTguMzgxIAkJIi8+CTwvZz4JPGc+CQk8cGF0aCBkPSJNNDYuODEyLDk5LjYzNGMtMi4wODYsMC00LjI4Ny0wLjEwMS02LjYxMi0wLjMxOEMyMC40MTcsOTcuNDYsNy43OCw4Mi4xOTEsNy4yNTEsODEuNTQzbDYuOTk0LTUuNjkzCQkJYzAuMSwwLjEyMSwxMC44NTUsMTIuOTkyLDI2Ljc5NywxNC40ODdjMjEuNzU2LDIuMDQxLDMwLjAwNS03Ljg5MiwzMC4wODMtNy45OTJsNy4xNjUsNS40NzcJCQlDNzcuODg5LDg4LjM0Niw2OC45ODEsOTkuNjM0LDQ2LjgxMiw5OS42MzRMNDYuODEyLDk5LjYzNHoiLz4JPC9nPjwvZz48L3N2Zz4\x3d",
        FLIP_VER: "PHN2ZyB2ZXJzaW9uPSIxLjEiIGlkPSJMYXllcl8xIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHhtbG5zOnhsaW5rPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5L3hsaW5rIiB4PSIwcHgiIHk9IjBweCIJIHZpZXdCb3g9IjAgMCAxMDAgMTAwIiBzdHlsZT0iZW5hYmxlLWJhY2tncm91bmQ6bmV3IDAgMCAxMDAgMTAwOyIgeG1sOnNwYWNlPSJwcmVzZXJ2ZSI+PGc+CTxnPgkJPHBhdGggc3R5bGU9ImZpbGw6IzFCNzVCODsiIGQ9Ik01My4yMjEsNDQuODdIMjIuNzkzbC05LjU3OC0yNy4zOThsMjQuNzkyLTE2Ljc0bDI0Ljc5MiwxNi43NEw1My4yMjEsNDQuODdMNTMuMjIxLDQ0Ljg3egkJCSBNMjcuODEsMzcuODAyaDIwLjM5M2w2LjEyNC0xNy41MkwzOC4wMDcsOS4yNjFMMjEuNjg2LDIwLjI4MkwyNy44MSwzNy44MDJMMjcuODEsMzcuODAyeiIvPgk8L2c+CTxnPgkJPHBhdGggc3R5bGU9ImZpbGw6IzFCNzVCODsiIGQ9Ik0zOC4wMDcsOTkuMDAzTDEzLjIxNSw4Mi4yNjFsOS41NzgtMjcuMzk4aDMwLjQyOGw5LjU3OCwyNy4zOThMMzguMDA3LDk5LjAwM0wzOC4wMDcsOTkuMDAzegkJCSBNMjEuNjg2LDc5LjQ1MWwxNi4zMjEsMTEuMDIybDE2LjMyMS0xMS4wMjJsLTYuMTI1LTE3LjUyMUgyNy44MUwyMS42ODYsNzkuNDUxTDIxLjY4Niw3OS40NTF6Ii8+CTwvZz4JPGc+CQk8cGF0aCBkPSJNNjguNTgsNTIuNjE4SDU1LjA5NnYtNS4xODZINjguNThWNTIuNjE4TDY4LjU4LDUyLjYxOHogTTQxLjYxLDUyLjYxOEgyOC4xMjV2LTUuMTg2SDQxLjYxVjUyLjYxOEw0MS42MSw1Mi42MTh6CQkJIE0xNC42NDEsNTIuNjE4SDEuMTU2di01LjE4NmgxMy40ODRWNTIuNjE4TDE0LjY0MSw1Mi42MTh6Ii8+CTwvZz4JPGc+CQk8cG9seWdvbiBwb2ludHM9Ijc3LjY1Niw0MC43NzMgNjYuNDE2LDguNjE4IDk4LjUzMSwxNi44ODYgCQkiLz4JPC9nPgk8Zz4JCTxwYXRoIGQ9Ik04MS42OTMsOTMuMDQ5TDc2LDg2LjA1NWMwLjEyMS0wLjEsMTIuOTkyLTEwLjg1NSwxNC40ODgtMjYuNzk3YzIuMDQxLTIxLjc2Mi03Ljg5My0zMC4wMDYtNy45OTQtMzAuMDgzbDUuNDc3LTcuMTY0CQkJYzAuNTc0LDAuNDM4LDE0LjAzMSwxMS4wNTcsMTEuNDk2LDM4LjA4OUM5Ny42MDksNzkuODg0LDgyLjM0Miw5Mi41MjEsODEuNjkzLDkzLjA0OUw4MS42OTMsOTMuMDQ5eiIvPgk8L2c+PC9nPjwvc3ZnPg\x3d\x3d",
        FLUORINE: "PHN2ZyBmaWxsLW9wYWNpdHk9IjEiIHhtbG5zOnhsaW5rPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5L3hsaW5rIiBjb2xvci1yZW5kZXJpbmc9ImF1dG8iIGNvbG9yLWludGVycG9sYXRpb249ImF1dG8iIHRleHQtcmVuZGVyaW5nPSJhdXRvIiBzdHJva2U9ImJsYWNrIiBzdHJva2UtbGluZWNhcD0ic3F1YXJlIiB3aWR0aD0iMjAiIHN0cm9rZS1taXRlcmxpbWl0PSIxMCIgc2hhcGUtcmVuZGVyaW5nPSJhdXRvIiBzdHJva2Utb3BhY2l0eT0iMSIgZmlsbD0iYmxhY2siIHN0cm9rZS1kYXNoYXJyYXk9Im5vbmUiIGZvbnQtd2VpZ2h0PSJub3JtYWwiIHN0cm9rZS13aWR0aD0iMSIgdmlld0JveD0iMCAwIDIwLjAgMjAuMCIgaGVpZ2h0PSIyMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIiBmb250LWZhbWlseT0iJmFwb3M7RGlhbG9nJmFwb3M7IiBmb250LXN0eWxlPSJub3JtYWwiIHN0cm9rZS1saW5lam9pbj0ibWl0ZXIiIGZvbnQtc2l6ZT0iMTIiIHN0cm9rZS1kYXNob2Zmc2V0PSIwIiBpbWFnZS1yZW5kZXJpbmc9ImF1dG8iPjxkZWZzIGlkPSJnZW5lcmljRGVmcyIgIC8+PGcgID48ZyBmb250LXNpemU9IjE0IiBmaWxsPSJyZ2IoMTQ0LDIyNCw4MCkiIHRleHQtcmVuZGVyaW5nPSJnZW9tZXRyaWNQcmVjaXNpb24iIGltYWdlLXJlbmRlcmluZz0ib3B0aW1pemVTcGVlZCIgY29sb3ItcmVuZGVyaW5nPSJvcHRpbWl6ZVF1YWxpdHkiIGZvbnQtZmFtaWx5PSImYXBvcztMdWNpZGEgR3JhbmRlJmFwb3M7IiBzdHJva2U9InJnYigxNDQsMjI0LDgwKSIgY29sb3ItaW50ZXJwb2xhdGlvbj0ibGluZWFyUkdCIiAgICA+PHBhdGggZD0iTTcuMzA1NyAxNSBMNy4zMDU3IDQuODgyOCBMMTIuOTU5IDQuODgyOCBMMTIuOTU5IDUuOTU2MSBMOC43NDEyIDUuOTU2MSBMOC43NDEyIDkuMzQ2NyBMMTIuMjgyMiA5LjM0NjcgTDEyLjI4MjIgMTAuNDA2MiBMOC43NDEyIDEwLjQwNjIgTDguNzQxMiAxNSBaIiBzdHJva2U9Im5vbmUiICAgIC8+PC9nICA+PC9nPjwvc3ZnPg\x3d\x3d",
        HYDROGEN: "PHN2ZyBmaWxsLW9wYWNpdHk9IjEiIHhtbG5zOnhsaW5rPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5L3hsaW5rIiBjb2xvci1yZW5kZXJpbmc9ImF1dG8iIGNvbG9yLWludGVycG9sYXRpb249ImF1dG8iIHRleHQtcmVuZGVyaW5nPSJhdXRvIiBzdHJva2U9ImJsYWNrIiBzdHJva2UtbGluZWNhcD0ic3F1YXJlIiB3aWR0aD0iMjAiIHN0cm9rZS1taXRlcmxpbWl0PSIxMCIgc2hhcGUtcmVuZGVyaW5nPSJhdXRvIiBzdHJva2Utb3BhY2l0eT0iMSIgZmlsbD0iYmxhY2siIHN0cm9rZS1kYXNoYXJyYXk9Im5vbmUiIGZvbnQtd2VpZ2h0PSJub3JtYWwiIHN0cm9rZS13aWR0aD0iMSIgdmlld0JveD0iMCAwIDIwLjAgMjAuMCIgaGVpZ2h0PSIyMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIiBmb250LWZhbWlseT0iJmFwb3M7RGlhbG9nJmFwb3M7IiBmb250LXN0eWxlPSJub3JtYWwiIHN0cm9rZS1saW5lam9pbj0ibWl0ZXIiIGZvbnQtc2l6ZT0iMTIiIHN0cm9rZS1kYXNob2Zmc2V0PSIwIiBpbWFnZS1yZW5kZXJpbmc9ImF1dG8iPjxkZWZzIGlkPSJnZW5lcmljRGVmcyIgIC8+PGcgID48ZyB0ZXh0LXJlbmRlcmluZz0iZ2VvbWV0cmljUHJlY2lzaW9uIiBmb250LXNpemU9IjE0IiBmb250LWZhbWlseT0iJmFwb3M7THVjaWRhIEdyYW5kZSZhcG9zOyIgY29sb3ItaW50ZXJwb2xhdGlvbj0ibGluZWFyUkdCIiBjb2xvci1yZW5kZXJpbmc9Im9wdGltaXplUXVhbGl0eSIgaW1hZ2UtcmVuZGVyaW5nPSJvcHRpbWl6ZVNwZWVkIiAgICA+PHBhdGggZD0iTTYuMzA1NyAxNSBMNi4zMDU3IDQuODgyOCBMNy43NDEyIDQuODgyOCBMNy43NDEyIDkuMTQ4NCBMMTIuNTUzNyA5LjE0ODQgTDEyLjU1MzcgNC44ODI4IEwxMy45ODkzIDQuODgyOCBMMTMuOTg5MyAxNSBMMTIuNTUzNyAxNSBMMTIuNTUzNyAxMC4yMjE3IEw3Ljc0MTIgMTAuMjIxNyBMNy43NDEyIDE1IFoiIHN0cm9rZT0ibm9uZSIgICAgLz48L2cgID48L2c+PC9zdmc+",
        INCREASE_CHARGE: "PHN2ZyBmaWxsLW9wYWNpdHk9IjEiIHhtbG5zOnhsaW5rPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5L3hsaW5rIiBjb2xvci1yZW5kZXJpbmc9ImF1dG8iIGNvbG9yLWludGVycG9sYXRpb249ImF1dG8iIHRleHQtcmVuZGVyaW5nPSJhdXRvIiBzdHJva2U9ImJsYWNrIiBzdHJva2UtbGluZWNhcD0ic3F1YXJlIiB3aWR0aD0iMjAiIHN0cm9rZS1taXRlcmxpbWl0PSIxMCIgc2hhcGUtcmVuZGVyaW5nPSJhdXRvIiBzdHJva2Utb3BhY2l0eT0iMSIgZmlsbD0iYmxhY2siIHN0cm9rZS1kYXNoYXJyYXk9Im5vbmUiIGZvbnQtd2VpZ2h0PSJub3JtYWwiIHN0cm9rZS13aWR0aD0iMSIgdmlld0JveD0iMCAwIDIwLjAgMjAuMCIgaGVpZ2h0PSIyMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIiBmb250LWZhbWlseT0iJmFwb3M7RGlhbG9nJmFwb3M7IiBmb250LXN0eWxlPSJub3JtYWwiIHN0cm9rZS1saW5lam9pbj0ibWl0ZXIiIGZvbnQtc2l6ZT0iMTIiIHN0cm9rZS1kYXNob2Zmc2V0PSIwIiBpbWFnZS1yZW5kZXJpbmc9ImF1dG8iPjxkZWZzIGlkPSJnZW5lcmljRGVmcyIgIC8+PGcgID48ZyBzdHJva2UtbGluZWNhcD0iYnV0dCIgdGV4dC1yZW5kZXJpbmc9Imdlb21ldHJpY1ByZWNpc2lvbiIgY29sb3ItcmVuZGVyaW5nPSJvcHRpbWl6ZVF1YWxpdHkiIGltYWdlLXJlbmRlcmluZz0ib3B0aW1pemVTcGVlZCIgc3Ryb2tlLWxpbmVqb2luPSJiZXZlbCIgY29sb3ItaW50ZXJwb2xhdGlvbj0ibGluZWFyUkdCIiBzdHJva2Utd2lkdGg9IjEuMiIgICAgPjxsaW5lIHkyPSIxMCIgZmlsbD0ibm9uZSIgeDE9IjYiIHgyPSIxNCIgeTE9IjEwIiAgICAgIC8+PGxpbmUgeTI9IjE0IiBmaWxsPSJub25lIiB4MT0iMTAiIHgyPSIxMCIgeTE9IjYiICAgICAgLz48Y2lyY2xlIGZpbGw9Im5vbmUiIHI9IjYiIGN4PSIxMCIgY3k9IjEwIiAgICAvPjwvZyAgPjwvZz48L3N2Zz4\x3d",
        IODINE: "PHN2ZyBmaWxsLW9wYWNpdHk9IjEiIHhtbG5zOnhsaW5rPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5L3hsaW5rIiBjb2xvci1yZW5kZXJpbmc9ImF1dG8iIGNvbG9yLWludGVycG9sYXRpb249ImF1dG8iIHRleHQtcmVuZGVyaW5nPSJhdXRvIiBzdHJva2U9ImJsYWNrIiBzdHJva2UtbGluZWNhcD0ic3F1YXJlIiB3aWR0aD0iMjAiIHN0cm9rZS1taXRlcmxpbWl0PSIxMCIgc2hhcGUtcmVuZGVyaW5nPSJhdXRvIiBzdHJva2Utb3BhY2l0eT0iMSIgZmlsbD0iYmxhY2siIHN0cm9rZS1kYXNoYXJyYXk9Im5vbmUiIGZvbnQtd2VpZ2h0PSJub3JtYWwiIHN0cm9rZS13aWR0aD0iMSIgdmlld0JveD0iMCAwIDIwLjAgMjAuMCIgaGVpZ2h0PSIyMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIiBmb250LWZhbWlseT0iJmFwb3M7RGlhbG9nJmFwb3M7IiBmb250LXN0eWxlPSJub3JtYWwiIHN0cm9rZS1saW5lam9pbj0ibWl0ZXIiIGZvbnQtc2l6ZT0iMTIiIHN0cm9rZS1kYXNob2Zmc2V0PSIwIiBpbWFnZS1yZW5kZXJpbmc9ImF1dG8iPjxkZWZzIGlkPSJnZW5lcmljRGVmcyIgIC8+PGcgID48ZyBmb250LXNpemU9IjE0IiBmaWxsPSJyZ2IoMTQ4LDAsMTQ4KSIgdGV4dC1yZW5kZXJpbmc9Imdlb21ldHJpY1ByZWNpc2lvbiIgaW1hZ2UtcmVuZGVyaW5nPSJvcHRpbWl6ZVNwZWVkIiBjb2xvci1yZW5kZXJpbmc9Im9wdGltaXplUXVhbGl0eSIgZm9udC1mYW1pbHk9IiZhcG9zO0x1Y2lkYSBHcmFuZGUmYXBvczsiIHN0cm9rZT0icmdiKDE0OCwwLDE0OCkiIGNvbG9yLWludGVycG9sYXRpb249ImxpbmVhclJHQiIgICAgPjxwYXRoIGQ9Ik05LjI5ODggMTUgTDkuMjk4OCA0Ljg4MjggTDEwLjczNDQgNC44ODI4IEwxMC43MzQ0IDE1IFoiIHN0cm9rZT0ibm9uZSIgICAgLz48L2cgID48L2c+PC9zdmc+",
        ISOTOPE: "PHN2ZyBmaWxsLW9wYWNpdHk9IjEiIHhtbG5zOnhsaW5rPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5L3hsaW5rIiBjb2xvci1yZW5kZXJpbmc9ImF1dG8iIGNvbG9yLWludGVycG9sYXRpb249ImF1dG8iIHRleHQtcmVuZGVyaW5nPSJhdXRvIiBzdHJva2U9ImJsYWNrIiBzdHJva2UtbGluZWNhcD0ic3F1YXJlIiB3aWR0aD0iMjAiIHN0cm9rZS1taXRlcmxpbWl0PSIxMCIgc2hhcGUtcmVuZGVyaW5nPSJhdXRvIiBzdHJva2Utb3BhY2l0eT0iMSIgZmlsbD0iYmxhY2siIHN0cm9rZS1kYXNoYXJyYXk9Im5vbmUiIGZvbnQtd2VpZ2h0PSJub3JtYWwiIHN0cm9rZS13aWR0aD0iMSIgdmlld0JveD0iMCAwIDIwLjAgMjAuMCIgaGVpZ2h0PSIyMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIiBmb250LWZhbWlseT0iJ0RpYWxvZyciIGZvbnQtc3R5bGU9Im5vcm1hbCIgc3Ryb2tlLWxpbmVqb2luPSJtaXRlciIgZm9udC1zaXplPSIxMnB4IiBzdHJva2UtZGFzaG9mZnNldD0iMCIgaW1hZ2UtcmVuZGVyaW5nPSJhdXRvIj48ZGVmcyBpZD0iZ2VuZXJpY0RlZnMiICAvPjxnICA+PGcgdGV4dC1yZW5kZXJpbmc9Imdlb21ldHJpY1ByZWNpc2lvbiIgZm9udC1mYW1pbHk9IidMdWNpZGEgR3JhbmRlJyIgY29sb3ItaW50ZXJwb2xhdGlvbj0ibGluZWFyUkdCIiBjb2xvci1yZW5kZXJpbmc9Im9wdGltaXplUXVhbGl0eSIgaW1hZ2UtcmVuZGVyaW5nPSJvcHRpbWl6ZVNwZWVkIiAgICA+PHBhdGggZD0iTTEzLjMzNCAxNS4yMTY4IFExMS4zMTI1IDE1LjIxNjggMTAuMjEwOSAxNC4wMzAzIFE5LjEwOTQgMTIuODQzOCA5LjEwOTQgMTAuNjY5OSBROS4xMDk0IDguNTAyIDEwLjIzMTQgNy4zMDY2IFExMS4zNTM1IDYuMTExMyAxMy4zOTI2IDYuMTExMyBRMTQuNTU4NiA2LjExMTMgMTYuMTIzIDYuNDkyMiBMMTYuMTIzIDcuNjQ2NSBRMTQuMzQxOCA3LjAzMTIgMTMuMzc1IDcuMDMxMiBRMTEuOTYyOSA3LjAzMTIgMTEuMTg5NSA3Ljk4NjMgUTEwLjQxNiA4Ljk0MTQgMTAuNDE2IDEwLjY4MTYgUTEwLjQxNiAxMi4zMzk4IDExLjI0MjIgMTMuMjk3OSBRMTIuMDY4NCAxNC4yNTU5IDEzLjQ5OCAxNC4yNTU5IFExNC43Mjg1IDE0LjI1NTkgMTYuMTM0OCAxMy41IEwxNi4xMzQ4IDE0LjU1NDcgUTE0Ljg1MTYgMTUuMjE2OCAxMy4zMzQgMTUuMjE2OCBaIiBzdHJva2U9Im5vbmUiICAgICAgLz48cGF0aCBkPSJNMi40Mjk3IDEwIEw0LjQ0NjMgNy4yNjA3IEwyLjQ4ODMgNC42OTczIEwzLjYzMDkgNC42OTczIEw1LjE3ODcgNi43MzgzIEw2LjU4MDEgNC42OTczIEw3LjUxNzYgNC42OTczIEw1LjY4MTYgNy4zODc3IEw3LjY3ODcgMTAgTDYuNTM2MSAxMCBMNC45Mzk1IDcuOTAwNCBMMy4zOTY1IDEwIFoiIHN0cm9rZT0ibm9uZSIgICAgLz48L2cgID48L2c+PC9zdmc+",
        MOVE: "PHN2ZyB2ZXJzaW9uPSIxLjEiIGlkPSJMYXllcl8xIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHhtbG5zOnhsaW5rPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5L3hsaW5rIiB4PSIwcHgiIHk9IjBweCIJIHZpZXdCb3g9IjAgMCAxMDAgMTAwIiBzdHlsZT0iZW5hYmxlLWJhY2tncm91bmQ6bmV3IDAgMCAxMDAgMTAwOyIgeG1sOnNwYWNlPSJwcmVzZXJ2ZSI+PGc+CTxnPgkJPGRlZnM+CQkJPGVsbGlwc2UgaWQ9IlNWR0lEXzFfIiBjeD0iNTMuMDIzIiBjeT0iMzkuNjAyIiByeD0iNjIuNzQiIHJ5PSI2MC4yNjYiLz4JCTwvZGVmcz4JCTxjbGlwUGF0aCBpZD0iU1ZHSURfMl8iPgkJCTx1c2UgeGxpbms6aHJlZj0iI1NWR0lEXzFfIiAgc3R5bGU9Im92ZXJmbG93OnZpc2libGU7Ii8+CQk8L2NsaXBQYXRoPgkJPGxpbmVhckdyYWRpZW50IGlkPSJTVkdJRF8zXyIgZ3JhZGllbnRVbml0cz0idXNlclNwYWNlT25Vc2UiIHgxPSIzLjc4NTYiIHkxPSI2Ni42NzI2IiB4Mj0iOTIuNjgyOCIgeTI9IjY2LjY3MjYiPgkJCTxzdG9wICBvZmZzZXQ9IjAiIHN0eWxlPSJzdG9wLWNvbG9yOiNERUFCODgiLz4JCQk8c3RvcCAgb2Zmc2V0PSIxIiBzdHlsZT0ic3RvcC1jb2xvcjojQzc4QTYyIi8+CQk8L2xpbmVhckdyYWRpZW50PgkJPHBhdGggc3R5bGU9ImNsaXAtcGF0aDp1cmwoI1NWR0lEXzJfKTtmaWxsOnVybCgjU1ZHSURfM18pOyIgZD0iTTI5Ljg4Nyw2My40MWMtMS43MTgtMC44MjktNC4xMDItMy40MzctNi4xNTctNi42NzkJCQljLTEuNDc4LTIuMzQ2LTMuMTczLTUuMTk0LTUuNzA4LTguMzM5Yy0yLjUzNi0zLjEzMy05LjM2NC04LjY3Mi0xMy41MzEtNC4yMTFjLTIuMjUxLDIuNDA1LDEuNTcxLDUuMDUzLDEuOTk4LDUuNjc2CQkJYzUuNTM5LDcuOSw3Ljk2OSwxNC43NTUsMTEuODE3LDIxLjg5NGMzLjg1MSw3LjE0Miw4LjkxMywxMy43MjMsMTQuNjIzLDE4Ljc4MWMzLjExNSwyLjczNi05LjEwNCwzNC43MzQtMy44ODYsMzYuNDc4CQkJYzQuNzg3LDEuNTkyLDIzLjA5LDExLjkxOCwzMy41MjctMy4xMDFjMS4zMDEtMS44NjUsNC41OS0yOC45NTUsNi43NzYtMzAuNjI1YzguNDg2LTYuNDU5LDEyLjA0My0yOS41MiwxMS45NjktMzIuMzk1CQkJYy0wLjA3NC0yLjg3NCw0LjkyNS0xMy4wNTEsNS41MTUtMTUuODg4YzAuNTc2LTIuNzk0LDYuNjQzLTE0LjI4MSw1Ljc2OC0xNy41ODNjLTAuNjg1LTIuNjAxLTMuMjQyLTQuMTAyLTUuNDQ2LTIuMzM3CQkJYy0yLjIxOCwxLjc2Ny00LjYwNCw4LjI2Ni02LjQ3OCwxMi43MzNjLTEuODc0LDQuNDY1LTUuNTY3LDEyLjc2My03LjQ4NSwxMi44OTNjLTEuNzgyLDAuMTE4LTIuMzY3LTEuNzg2LTIuMjY3LTQuNDA2CQkJYzAuMTAyLTIuNjE5LDIuMDk4LTI5LjA2NSwxLjY4My0zMi40NWMtMC40MjItMy4zODUtMS4xNTEtNi4yOTktNC4xMDQtNi41MzdjLTIuNDY5LTAuMTg4LTQuNTg2LDEuMDgyLTUuMzMyLDkuOTU0CQkJYy0wLjc1Miw4Ljg3My0xLjM0OCwyMy4zMjMtMS42MzUsMjYuNzgxYy0wLjM5LDQuODMtMS44NTEsNC43MDMtMi44Niw0LjUwMWMtMC42MDMtMC4xMTktMS42NTgtMS40NzUtMS42MjgtNC43NjkJCQljMC4wMS0zLjMwMi0xLjkxMy0zMi4wMTgtMi4xNTktMzUuMTQ1Yy0wLjI0LTMuMTMzLTAuODY1LTcuMTg5LTQuMTI2LTcuMjM5Yy01LjI2MS0wLjA4Mi01LjIxNCw1LjU5OC01LjA3OCw5Ljc3NgkJCWMwLjE4NCw0Ljk5NiwxLjcwNiwyMy4wMDYsMS43ODcsMjYuOTczYzAuMSw0LjY3LTAuMTk0LDcuMjU0LTIuMDU5LDYuODc5Yy0xLjU4MS0wLjMyLTIuMDQtMy43NDYtMi42LTcuNTc2CQkJYy0wLjQzNy0zLjEwMi00LjI0OC0yMS45MDEtNC45NTgtMjQuOTU2Yy0wLjc4My0zLjMyNi0yLjUwNi02LjYwNS01Ljg3LTUuNzgxYy0zLjIxNywwLjc4Mi0zLjk4NywzLjE0Ni00LjAwNCw3LjUzOAkJCWMtMC4wMjMsNC4zOTQsNC42MzQsMjguMjE2LDUuMTY3LDMxLjk5MmMwLjU3Niw0LjE2MywyLjI3NSwxMi4wMTksMS44MjYsMTQuMTI3QzM0LjUxNiw2Mi40NzksMzEuOTYxLDY0LjQwNywyOS44ODcsNjMuNDF6Ii8+CQk8bGluZWFyR3JhZGllbnQgaWQ9IlNWR0lEXzRfIiBncmFkaWVudFVuaXRzPSJ1c2VyU3BhY2VPblVzZSIgeDE9IjE4Ljc2MTUiIHkxPSI2NC4yOTc4IiB4Mj0iMTguNzYxNSIgeTI9IjQyLjUxMDkiPgkJCTxzdG9wICBvZmZzZXQ9IjAiIHN0eWxlPSJzdG9wLWNvbG9yOiNCRDgwNTciLz4JCQk8c3RvcCAgb2Zmc2V0PSIxIiBzdHlsZT0ic3RvcC1jb2xvcjojREVBNTgxIi8+CQk8L2xpbmVhckdyYWRpZW50PgkJPHBhdGggc3R5bGU9ImNsaXAtcGF0aDp1cmwoI1NWR0lEXzJfKTtmaWxsOnVybCgjU1ZHSURfNF8pOyIgZD0iTTMzLjAzMiw2My4wNTdjLTAuOTU0LDAuNjItMi4xMSwwLjg1My0zLjE0NSwwLjM1NAkJCWMtMS43MTgtMC44MjktNC4xMDItMy40MzctNi4xNTctNi42NzljLTEuNDc4LTIuMzQ2LTMuMTczLTUuMTk0LTUuNzA4LTguMzM5Yy0yLjUzNi0zLjEzMy05LjM2NC04LjY3Mi0xMy41MzEtNC4yMTEJCQljMCwwLDMuNS0yLjQ2LDkuNTcyLDMuNDQ1YzMuMTA0LDMuMDE4LDQuNTk1LDExLjMxNiw4LjIsMTQuOTI3QzI1Ljg2Nyw2Ni4xNTksMzMuMDMyLDYzLjA1NywzMy4wMzIsNjMuMDU3eiIvPgkJPGxpbmVhckdyYWRpZW50IGlkPSJTVkdJRF81XyIgZ3JhZGllbnRVbml0cz0idXNlclNwYWNlT25Vc2UiIHgxPSIzOC42OTUzIiB5MT0iNi41ODI4IiB4Mj0iMzguNjk1MyIgeTI9IjQ1LjAyMzkiPgkJCTxzdG9wICBvZmZzZXQ9IjAiIHN0eWxlPSJzdG9wLWNvbG9yOiNDNzk1NzUiLz4JCQk8c3RvcCAgb2Zmc2V0PSIxIiBzdHlsZT0ic3RvcC1jb2xvcjojQzQ3RjUxIi8+CQk8L2xpbmVhckdyYWRpZW50PgkJPHBhdGggc3R5bGU9ImNsaXAtcGF0aDp1cmwoI1NWR0lEXzJfKTtmaWxsOnVybCgjU1ZHSURfNV8pOyIgZD0iTTQ1LjQwOSw0NS4wMjRjLTEuNTgxLTAuMzItMi4wNC0zLjc0Ni0yLjYtNy41NzYJCQljLTAuNDM3LTMuMTAyLTQuMjQ4LTIxLjkwMS00Ljk1OC0yNC45NTZjLTAuNzgzLTMuMzI2LTIuNTA2LTYuNjA1LTUuODctNS43ODFjMCwwLDIuNTg0LDMuMDMyLDIuOTA2LDUuMzI4CQkJYzAuMzI5LDIuMjkzLDMuOTM2LDI1LjI1Niw1LjU3NiwyOS4wMjNDNDIuMTA1LDQ0LjgzOCw0NS40MDksNDUuMDI0LDQ1LjQwOSw0NS4wMjR6Ii8+CQk8bGluZWFyR3JhZGllbnQgaWQ9IlNWR0lEXzZfIiBncmFkaWVudFVuaXRzPSJ1c2VyU3BhY2VPblVzZSIgeDE9IjU0LjcxNTQiIHkxPSI0OC43MTc4IiB4Mj0iNTQuNzE1NCIgeTI9IjEuMzk2NSI+CQkJPHN0b3AgIG9mZnNldD0iMCIgc3R5bGU9InN0b3AtY29sb3I6I0JEODA1NyIvPgkJCTxzdG9wICBvZmZzZXQ9IjEiIHN0eWxlPSJzdG9wLWNvbG9yOiNDNzgyNTYiLz4JCTwvbGluZWFyR3JhZGllbnQ+CQk8cGF0aCBzdHlsZT0iY2xpcC1wYXRoOnVybCgjU1ZHSURfMl8pO2ZpbGw6dXJsKCNTVkdJRF82Xyk7IiBkPSJNNTguNjcyLDQ4LjU1Yy0wLjYwMy0wLjExOS0xLjY1OC0xLjQ3NS0xLjYyOC00Ljc2OQkJCWMwLjAxLTMuMzAyLTEuOTEzLTMyLjAxOC0yLjE1OS0zNS4xNDVjLTAuMjQtMy4xMzMtMC44NjUtNy4xODktNC4xMjYtNy4yMzljMCwwLDIuMDA2LDIuNjA5LDIuODI4LDE4LjE4NgkJCWMwLjgyMywxNS41ODMsMC44MjMsMjMuNzc5LDIuNDY0LDI2Ljg5NkM1Ny42OTEsNDkuNTkzLDU4LjY3Miw0OC41NSw1OC42NzIsNDguNTV6Ii8+CQk8bGluZWFyR3JhZGllbnQgaWQ9IlNWR0lEXzdfIiBncmFkaWVudFVuaXRzPSJ1c2VyU3BhY2VPblVzZSIgeDE9IjcwLjU3OTYiIHkxPSI1MC41NjMiIHgyPSI3MC41Nzk2IiB5Mj0iNy4zMTQiPgkJCTxzdG9wICBvZmZzZXQ9IjAiIHN0eWxlPSJzdG9wLWNvbG9yOiNCRDgwNTciLz4JCQk8c3RvcCAgb2Zmc2V0PSIxIiBzdHlsZT0ic3RvcC1jb2xvcjojQzc4MjU2Ii8+CQk8L2xpbmVhckdyYWRpZW50PgkJPHBhdGggc3R5bGU9ImNsaXAtcGF0aDp1cmwoI1NWR0lEXzJfKTtmaWxsOnVybCgjU1ZHSURfN18pOyIgZD0iTTcyLjI4NSw1MC41NjNjLTEuMDgtMC40OTYtMS40NDUtMi4xNDgtMS4zNjQtNC4yNjIJCQljMC4xMDItMi42MTksMi4wOTgtMjkuMDY1LDEuNjgzLTMyLjQ1Yy0wLjQyMi0zLjM4NS0xLjE1MS02LjI5OS00LjEwNC02LjUzN2MwLDAsMi4xNDYsMy4yNDYsMi4xNDYsOC4wMDUJCQljMCw0Ljc1Ni0yLjQ2MywyNi41NjYtMS42NDUsMjkuNTE5QzY5LjgyMiw0Ny43OSw3Mi4yODUsNTAuNTYzLDcyLjI4NSw1MC41NjN6Ii8+CQk8bGluZWFyR3JhZGllbnQgaWQ9IlNWR0lEXzhfIiBncmFkaWVudFVuaXRzPSJ1c2VyU3BhY2VPblVzZSIgeDE9IjcwLjgzODUiIHkxPSIxMzEuODgyOCIgeDI9IjcwLjgzODUiIHkyPSIyNC44MDE5Ij4JCQk8c3RvcCAgb2Zmc2V0PSIwIiBzdHlsZT0ic3RvcC1jb2xvcjojQUQ3NTUwIi8+CQkJPHN0b3AgIG9mZnNldD0iMSIgc3R5bGU9InN0b3AtY29sb3I6I0JBN0E1MCIvPgkJPC9saW5lYXJHcmFkaWVudD4JCTxwYXRoIHN0eWxlPSJjbGlwLXBhdGg6dXJsKCNTVkdJRF8yXyk7ZmlsbDp1cmwoI1NWR0lEXzhfKTsiIGQ9Ik00OC45OTQsMTMxLjg4M2M0Ljg4NC0wLjM3NSw5Ljc1NC0yLjQ3MiwxMy41NzUtNy45NzQJCQljMS4zMDEtMS44NjUsNC41OS0yOC45NTUsNi43NzYtMzAuNjI1YzguNDg2LTYuNDU5LDEyLjA0My0yOS41MiwxMS45NjktMzIuMzk1Yy0wLjA3NC0yLjg3NCw0LjkyNS0xMy4wNTEsNS41MTUtMTUuODg4CQkJYzAuNTc2LTIuNzk0LDYuNjQzLTE0LjI4MSw1Ljc2OC0xNy41ODNjLTAuMzA5LTEuMTMyLTAuOTU3LTIuMDYxLTEuNzgxLTIuNTk3YzAsMCwyLjk1LTAuOTcxLTEuOTY3LDEwLjk5OAkJCWMtNC45MiwxMS45NzItOS42ODYsMTkuNTE1LTEwLjE3MSwyMy42MTVjLTAuNDk0LDQuMDk5LTIuNDYxLDE3Ljg3Ni01LjQwOCwyMS45NzRjLTIuOTU5LDQuMTAzLTE0LjU5OCw3LjA1Ny0xNC43NjMsMTEuODEyCQkJQzU4LjM0LDk3Ljk3OCw0OC45OTQsMTMxLjg4Myw0OC45OTQsMTMxLjg4M3oiLz4JCTxsaW5lYXJHcmFkaWVudCBpZD0iU1ZHSURfOV8iIGdyYWRpZW50VW5pdHM9InVzZXJTcGFjZU9uVXNlIiB4MT0iMzIuMzczNSIgeTE9Ijk1LjkwMTkiIHgyPSI2OS4zNDU3IiB5Mj0iOTUuOTAxOSI+CQkJPHN0b3AgIG9mZnNldD0iMCIgc3R5bGU9InN0b3AtY29sb3I6I0RFQUI4OCIvPgkJCTxzdG9wICBvZmZzZXQ9IjAuNDc4NSIgc3R5bGU9InN0b3AtY29sb3I6I0M3OEE2MiIvPgkJCTxzdG9wICBvZmZzZXQ9IjEiIHN0eWxlPSJzdG9wLWNvbG9yOiM5OTZBNEIiLz4JCTwvbGluZWFyR3JhZGllbnQ+CQk8cGF0aCBzdHlsZT0iY2xpcC1wYXRoOnVybCgjU1ZHSURfMl8pO2ZpbGw6dXJsKCNTVkdJRF85Xyk7IiBkPSJNMzIuOTI5LDkwLjUzMmMwLDAsNS41NzMsNS4xNDcsMTQuMDkzLDQuNDkyCQkJYzguNTMzLTAuNjU3LDUuOTExLTEuMzE0LDExLjE1NC0xLjMxNGM1LjI0OSwwLDMuODEyLDAuODc1LDcuMjIyLDAuNjU3YzMuNDAxLTAuMjE2LDMuOTQ4LTEuMDgzLDMuOTQ4LTEuMDgzCQkJcy0wLjgzNywxLjQ2My0xLjE2MywyLjcwM2MtMC4zMjEsMS4yMzQtMC45OSw1LjI4NC0wLjk5LDUuMjg0bC0zNC44MTktMS42NWMwLDAsMS4zNDctMy42MjIsMS4yMDItNS41ODQJCQlDMzMuNDMzLDkyLjA3OSwzMi45MjksOTAuNTMyLDMyLjkyOSw5MC41MzJ6Ii8+CQk8cGF0aCBzdHlsZT0iY2xpcC1wYXRoOnVybCgjU1ZHSURfMl8pO2ZpbGw6bm9uZTtzdHJva2U6IzdENTczMztzdHJva2Utd2lkdGg6Mi40NzsiIGQ9Ik0yOS44ODcsNjMuNDEJCQljLTEuNzE4LTAuODI5LTQuMTAyLTMuNDM3LTYuMTU3LTYuNjc5Yy0xLjQ3OC0yLjM0Ni0zLjE3My01LjE5NC01LjcwOC04LjMzOWMtMi41MzYtMy4xMzMtOS4zNjQtOC42NzItMTMuNTMxLTQuMjExCQkJYy0yLjI1MSwyLjQwNSwxLjU3MSw1LjA1MywxLjk5OCw1LjY3NmM1LjUzOSw3LjksNy45NjksMTQuNzU1LDExLjgxNywyMS44OTRjMy44NTEsNy4xNDIsOC45MTMsMTMuNzIzLDE0LjYyMywxOC43ODEJCQljMy4xMTUsMi43MzYtOS4xMDQsMzQuNzM0LTMuODg2LDM2LjQ3OGM0Ljc4NywxLjU5MiwyMy4wOSwxMS45MTgsMzMuNTI3LTMuMTAxYzEuMzAxLTEuODY1LDQuNTktMjguOTU1LDYuNzc2LTMwLjYyNQkJCWM4LjQ4Ni02LjQ1OSwxMi4wNDMtMjkuNTIsMTEuOTY5LTMyLjM5NWMtMC4wNzQtMi44NzQsNC45MjUtMTMuMDUxLDUuNTE1LTE1Ljg4OGMwLjU3Ni0yLjc5NCw2LjY0My0xNC4yODEsNS43NjgtMTcuNTgzCQkJYy0wLjY4NS0yLjYwMS0zLjI0Mi00LjEwMi01LjQ0Ni0yLjMzN2MtMi4yMTgsMS43NjctNC42MDQsOC4yNjYtNi40NzgsMTIuNzMzYy0xLjg3NCw0LjQ2NS01LjU2NywxMi43NjMtNy40ODUsMTIuODkzCQkJYy0xLjc4MiwwLjExOC0yLjM2Ny0xLjc4Ni0yLjI2Ny00LjQwNmMwLjEwMi0yLjYxOSwyLjA5OC0yOS4wNjUsMS42ODMtMzIuNDVjLTAuNDIyLTMuMzg1LTEuMTUxLTYuMjk5LTQuMTA0LTYuNTM3CQkJYy0yLjQ2OS0wLjE4OC00LjU4NiwxLjA4Mi01LjMzMiw5Ljk1NGMtMC43NTIsOC44NzMtMS4zNDgsMjMuMzIzLTEuNjM1LDI2Ljc4MWMtMC4zOSw0LjgzLTEuODUxLDQuNzAzLTIuODYsNC41MDEJCQljLTAuNjAzLTAuMTE5LTEuNjU4LTEuNDc1LTEuNjI4LTQuNzY5YzAuMDEtMy4zMDItMS45MTMtMzIuMDE4LTIuMTU5LTM1LjE0NWMtMC4yNC0zLjEzMy0wLjg2NS03LjE4OS00LjEyNi03LjIzOQkJCWMtNS4yNjEtMC4wODItNS4yMTQsNS41OTgtNS4wNzgsOS43NzZjMC4xODQsNC45OTYsMS43MDYsMjMuMDA2LDEuNzg3LDI2Ljk3M2MwLjEsNC42Ny0wLjE5NCw3LjI1NC0yLjA1OSw2Ljg3OQkJCWMtMS41ODEtMC4zMi0yLjA0LTMuNzQ2LTIuNi03LjU3NmMtMC40MzctMy4xMDItNC4yNDgtMjEuOTAxLTQuOTU4LTI0Ljk1NmMtMC43ODMtMy4zMjYtMi41MDYtNi42MDUtNS44Ny01Ljc4MQkJCWMtMy4yMTcsMC43ODItMy45ODcsMy4xNDYtNC4wMDQsNy41MzhjLTAuMDIzLDQuMzk0LDQuNjM0LDI4LjIxNiw1LjE2NywzMS45OTJjMC41NzYsNC4xNjMsMi4yNzUsMTIuMDE5LDEuODI2LDE0LjEyNwkJCUMzNC41MTYsNjIuNDc5LDMxLjk2MSw2NC40MDcsMjkuODg3LDYzLjQxeiIvPgk8L2c+CTxsaW5lYXJHcmFkaWVudCBpZD0iU1ZHSURfMTBfIiBncmFkaWVudFVuaXRzPSJ1c2VyU3BhY2VPblVzZSIgeDE9IjQ1LjQ4NDciIHkxPSI4Ny42NDE2IiB4Mj0iNDUuNDg0NyIgeTI9IjY3Ljk1OCI+CQk8c3RvcCAgb2Zmc2V0PSIwIiBzdHlsZT0ic3RvcC1jb2xvcjojQkQ4MDU3Ii8+CQk8c3RvcCAgb2Zmc2V0PSIxIiBzdHlsZT0ic3RvcC1jb2xvcjojQzc4MjU2Ii8+CTwvbGluZWFyR3JhZGllbnQ+CTxwYXRoIHN0eWxlPSJmaWxsOnVybCgjU1ZHSURfMTBfKTsiIGQ9Ik0zOS4zMTYsNjcuOTU4YzAsMCw3LjgyNywxLjMwMywxMC4xNzEsNi41NjZjMy45Myw4Ljg1MiwxLjMxMiwxMy4xMTcsMS4zMTIsMTMuMTE3CQlzLTAuNzU3LTguNzYxLTUuNjUyLTE0LjUyOUM0MS4zOTMsNjguNjkxLDM5LjMxNiw2Ny45NTgsMzkuMzE2LDY3Ljk1OHoiLz4JPGxpbmVhckdyYWRpZW50IGlkPSJTVkdJRF8xMV8iIGdyYWRpZW50VW5pdHM9InVzZXJTcGFjZU9uVXNlIiB4MT0iNTcuOCIgeTE9IjY1LjI4MzUiIHgyPSI1Ny44IiB5Mj0iNTcuNzM2MyI+CQk8c3RvcCAgb2Zmc2V0PSIwIiBzdHlsZT0ic3RvcC1jb2xvcjojQkQ4MDU3Ii8+CQk8c3RvcCAgb2Zmc2V0PSIxIiBzdHlsZT0ic3RvcC1jb2xvcjojQzc4MjU2Ii8+CTwvbGluZWFyR3JhZGllbnQ+CTxwYXRoIHN0eWxlPSJmaWxsOnVybCgjU1ZHSURfMTFfKTsiIGQ9Ik00MS42NDgsNTcuNzM2YzAsMCwxLjY0LDIuNjQyLDUuMzc0LDMuMTc2YzUuMDU2LDAuNzE0LDguNTYyLTAuNTU2LDguNTYyLTAuNTU2CQlzLTAuMDA0LDIuNDY0LDQuNTk2LDMuMTE3YzQuNTkxLDAuNjU2LDguMzYtMC40OTEsOC4zNi0wLjQ5MXMxLjMxNSwyLjQ2LDMuMTE2LDIuMjkzYzEuOC0wLjE2MiwyLjI5Ni0wLjk4MiwyLjI5Ni0wLjk4MgkJcy0xLjY0LDAuNDkzLTIuNDU3LTAuMTYzYy0wLjgyNi0wLjY1Ni0yLjk1NS0yLjc5My0yLjk1NS0yLjc5M3MtNC43NTgsMC45ODgtNy4yMTUsMGMtMi40NjQtMC45OC01LjA4My0zLjExMS01LjA4My0zLjExMQkJcy01LjY3LDAuOTgxLTguMzY3LDAuODIzQzQzLjQyLDU4Ljc4MSw0MS42NDgsNTcuNzM2LDQxLjY0OCw1Ny43MzZ6Ii8+PC9nPjwvc3ZnPg\x3d\x3d",
        NITROGEN: "PHN2ZyBmaWxsLW9wYWNpdHk9IjEiIHhtbG5zOnhsaW5rPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5L3hsaW5rIiBjb2xvci1yZW5kZXJpbmc9ImF1dG8iIGNvbG9yLWludGVycG9sYXRpb249ImF1dG8iIHRleHQtcmVuZGVyaW5nPSJhdXRvIiBzdHJva2U9ImJsYWNrIiBzdHJva2UtbGluZWNhcD0ic3F1YXJlIiB3aWR0aD0iMjAiIHN0cm9rZS1taXRlcmxpbWl0PSIxMCIgc2hhcGUtcmVuZGVyaW5nPSJhdXRvIiBzdHJva2Utb3BhY2l0eT0iMSIgZmlsbD0iYmxhY2siIHN0cm9rZS1kYXNoYXJyYXk9Im5vbmUiIGZvbnQtd2VpZ2h0PSJub3JtYWwiIHN0cm9rZS13aWR0aD0iMSIgdmlld0JveD0iMCAwIDIwLjAgMjAuMCIgaGVpZ2h0PSIyMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIiBmb250LWZhbWlseT0iJmFwb3M7RGlhbG9nJmFwb3M7IiBmb250LXN0eWxlPSJub3JtYWwiIHN0cm9rZS1saW5lam9pbj0ibWl0ZXIiIGZvbnQtc2l6ZT0iMTIiIHN0cm9rZS1kYXNob2Zmc2V0PSIwIiBpbWFnZS1yZW5kZXJpbmc9ImF1dG8iPjxkZWZzIGlkPSJnZW5lcmljRGVmcyIgIC8+PGcgID48ZyBmb250LXNpemU9IjE0IiBmaWxsPSJyZ2IoNDgsODAsMjQ4KSIgdGV4dC1yZW5kZXJpbmc9Imdlb21ldHJpY1ByZWNpc2lvbiIgaW1hZ2UtcmVuZGVyaW5nPSJvcHRpbWl6ZVNwZWVkIiBjb2xvci1yZW5kZXJpbmc9Im9wdGltaXplUXVhbGl0eSIgZm9udC1mYW1pbHk9IiZhcG9zO0x1Y2lkYSBHcmFuZGUmYXBvczsiIHN0cm9rZT0icmdiKDQ4LDgwLDI0OCkiIGNvbG9yLWludGVycG9sYXRpb249ImxpbmVhclJHQiIgICAgPjxwYXRoIGQ9Ik02LjMwNTcgMTUgTDYuMzA1NyA0Ljg4MjggTDcuNzEzOSA0Ljg4MjggTDEyLjgwNjYgMTIuNjk2MyBMMTIuODA2NiA0Ljg4MjggTDE0LjAzNzEgNC44ODI4IEwxNC4wMzcxIDE1IEwxMi42MzU3IDE1IEw3LjUzNjEgNy4xODY1IEw3LjUzNjEgMTUgWiIgc3Ryb2tlPSJub25lIiAgICAvPjwvZyAgPjwvZz48L3N2Zz4\x3d",
        OPEN: "PHN2ZyB2ZXJzaW9uPSIxLjEiIGlkPSJMYXllcl8xIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHhtbG5zOnhsaW5rPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5L3hsaW5rIiB4PSIwcHgiIHk9IjBweCIJIHZpZXdCb3g9IjAgMCAxMDAgMTAwIiBzdHlsZT0iZW5hYmxlLWJhY2tncm91bmQ6bmV3IDAgMCAxMDAgMTAwOyIgeG1sOnNwYWNlPSJwcmVzZXJ2ZSI+PGc+CTxsaW5lYXJHcmFkaWVudCBpZD0iU1ZHSURfMV8iIGdyYWRpZW50VW5pdHM9InVzZXJTcGFjZU9uVXNlIiB4MT0iNDUuMTAyIiB5MT0iMTIuMDcyMyIgeDI9IjQ1LjEwMiIgeTI9Ijg3Ljg0MzciPgkJPHN0b3AgIG9mZnNldD0iMCIgc3R5bGU9InN0b3AtY29sb3I6I0Q2QTUwNiIvPgkJPHN0b3AgIG9mZnNldD0iMC4yODg3IiBzdHlsZT0ic3RvcC1jb2xvcjojRDNBMzA2Ii8+CQk8c3RvcCAgb2Zmc2V0PSIwLjQ5MjgiIHN0eWxlPSJzdG9wLWNvbG9yOiNDQTlDMDYiLz4JCTxzdG9wICBvZmZzZXQ9IjAuNjcwNyIgc3R5bGU9InN0b3AtY29sb3I6I0JBOTAwNSIvPgkJPHN0b3AgIG9mZnNldD0iMC44MzM3IiBzdHlsZT0ic3RvcC1jb2xvcjojQTQ3RTA1Ii8+CQk8c3RvcCAgb2Zmc2V0PSIwLjk4NTIiIHN0eWxlPSJzdG9wLWNvbG9yOiM4ODY4MDQiLz4JCTxzdG9wICBvZmZzZXQ9IjEiIHN0eWxlPSJzdG9wLWNvbG9yOiM4NTY2MDQiLz4JPC9saW5lYXJHcmFkaWVudD4JPHBhdGggc3R5bGU9ImZpbGw6dXJsKCNTVkdJRF8xXyk7c3Ryb2tlOiM5OTZFMDA7c3Ryb2tlLXdpZHRoOjIuNDgzNztzdHJva2UtbGluZWNhcDpyb3VuZDtzdHJva2UtbGluZWpvaW46cm91bmQ7IiBkPSIJCU00NC4zNDEsMTguNDk1bC0wLjU4NC0yLjUwOGMtMC40MjItMS43NzYtMC45MDctMi44NzQtMS40NDctMy4yOTJjLTAuNTI4LTAuNDEyLTEuNzM3LTAuNjIzLTMuNjAxLTAuNjIzSDIwLjYwNAkJYy0yLjA4OSwwLTMuNDk1LDAuMjE5LTQuMTk4LDAuNjUyYy0wLjczMiwwLjQ3NC0xLjI3NywxLjQ5MS0xLjY2NywzLjA1MmwtMC42LDIuNTA1Yy0wLjUxNywyLjA2Ni0xLjEwMSwzLjM0LTEuNzM1LDMuODExCQljLTAuNjM0LDAuNDcyLTIuMDQxLDAuNzAyLTQuMjM0LDAuNzAySDUuMTUzYy0xLjU4NCwwLTIuNjA2LDAuMjY3LTMuMTE0LDAuNzk0Yy0wLjUxLDAuNTIxLTAuNzY0LDEuNjI5LTAuNzY0LDMuMzM0bDIuMzIsNjAuOTIyCQlsMjEuNDk5LTQ2LjgyN2MxLjUzMi0zLjI5MSwyLjUzNy00LjExMywzLjM4Ni00LjY2MmMwLjgyOC0wLjUzMyw0LjU0MS0wLjY1OCw4LjA5LTAuNjU4aDUyLjM1OGwtMC4zNjItOC43MzUJCWMwLTIuNzc4LTEuMjExLTQuMTY3LTMuNjc4LTQuMTY3SDUxLjc5Yy0zLjA3NiwwLTQuOTQ5LTAuMTk4LTUuNjgxLTAuNTkyQzQ1LjM4NiwyMS43OTcsNDQuOCwyMC41Nyw0NC4zNDEsMTguNDk1Ii8+CTxnPgkJPGc+CQkJPGxpbmVhckdyYWRpZW50IGlkPSJTVkdJRF8yXyIgZ3JhZGllbnRVbml0cz0idXNlclNwYWNlT25Vc2UiIHgxPSIzLjU5MDgiIHkxPSI2MS43NjE1IiB4Mj0iOTguNjYwMiIgeTI9IjYxLjc2MTUiPgkJCQk8c3RvcCAgb2Zmc2V0PSIwIiBzdHlsZT0ic3RvcC1jb2xvcjojRkZGNjk0Ii8+CQkJCTxzdG9wICBvZmZzZXQ9IjAuNDcyNCIgc3R5bGU9InN0b3AtY29sb3I6I0ZGRTkwMCIvPgkJCQk8c3RvcCAgb2Zmc2V0PSIwLjYzNTkiIHN0eWxlPSJzdG9wLWNvbG9yOiNGOUU0MDAiLz4JCQkJPHN0b3AgIG9mZnNldD0iMC44NDkxIiBzdHlsZT0ic3RvcC1jb2xvcjojRTlENTAwIi8+CQkJCTxzdG9wICBvZmZzZXQ9IjEiIHN0eWxlPSJzdG9wLWNvbG9yOiNEOUM2MDAiLz4JCQk8L2xpbmVhckdyYWRpZW50PgkJCTxwYXRoIHN0eWxlPSJmaWxsOnVybCgjU1ZHSURfMl8pO3N0cm9rZTojRkJDNzAwO3N0cm9rZS13aWR0aDoyLjQ4Mzc7c3Ryb2tlLWxpbmVjYXA6cm91bmQ7c3Ryb2tlLWxpbmVqb2luOnJvdW5kOyIgZD0iCQkJCU0zLjU5MSw4Ny44OTRoNzIuNDc1bDIxLjUzOC00OC4xOTJjMC43MDItMS43MzcsMS4wNTctMi43MDksMS4wNTctMi45MzFjLTAuMTA5LTAuNzU0LTEuMDk1LTEuMTQxLTMuMDI2LTEuMTQxSDMxLjgzOAkJCQljLTEuODczLDAtMy4xOTEsMC4yNDMtMy45MDMsMC43MDVjLTAuNzEzLDAuNDctMS40MzUsMS41NDEtMi4xODcsMy4yMDVMMy41OTEsODcuODk0eiIvPgkJPC9nPgkJPGxpbmVhckdyYWRpZW50IGlkPSJTVkdJRF8zXyIgZ3JhZGllbnRVbml0cz0idXNlclNwYWNlT25Vc2UiIHgxPSI3LjMyMDMiIHkxPSI2MS42NTU5IiB4Mj0iOTYuMjI5NiIgeTI9IjYxLjY1NTkiPgkJCTxzdG9wICBvZmZzZXQ9IjAuMDA2MSIgc3R5bGU9InN0b3AtY29sb3I6I0ZGRkZGRiIvPgkJCTxzdG9wICBvZmZzZXQ9IjAuNDg0NyIgc3R5bGU9InN0b3AtY29sb3I6I0ZGRkJDOSIvPgkJCTxzdG9wICBvZmZzZXQ9IjEiIHN0eWxlPSJzdG9wLWNvbG9yOiNGRkY0ODIiLz4JCTwvbGluZWFyR3JhZGllbnQ+CQk8cGF0aCBzdHlsZT0iZmlsbDp1cmwoI1NWR0lEXzNfKTsiIGQ9Ik03LjMyLDg1LjMwM2MwLDAsMTkuMzE0LTQyLjUwNywxOS42ODctNDMuNTU5YzAuMzc4LTEuMDQxLDAuOTc0LTIuMzM3LDIuMjI1LTMuMTMxCQkJYzEuMjQ4LTAuNzgsMi40MzgtMC42NTQsMy42OTctMC42NTRjMS4yNjMsMCw2MS4yNjgsMC4xMDksNjEuMjY4LDAuMTA5czEuMjYxLDAsMS42NDIsMC4zODhjMS42MzksMS43MzUtMi4zMjUsMS43MzctMy44MTgsMS43NjEJCQljLTEuMDA1LDAuMDItNTYuNzctMC4xMzUtNTguMjgsMC4yNjJjLTEuNTE0LDAuMzg5LTIuMTU1LTAuMTUzLTIuOTE5LDAuNDk5Yy0wLjc2MSwwLjY1OC0xLjEzLDEuMzA3LTEuNTE0LDIuMDkzCQkJQzI4Ljk0LDQzLjg1NCw5Ljc4Nyw4NS4zNiw5Ljc4Nyw4NS4zNkw3LjMyLDg1LjMwM3oiLz4JPC9nPjwvZz48L3N2Zz4\x3d",
        OXYGEN: "PHN2ZyBmaWxsLW9wYWNpdHk9IjEiIHhtbG5zOnhsaW5rPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5L3hsaW5rIiBjb2xvci1yZW5kZXJpbmc9ImF1dG8iIGNvbG9yLWludGVycG9sYXRpb249ImF1dG8iIHRleHQtcmVuZGVyaW5nPSJhdXRvIiBzdHJva2U9ImJsYWNrIiBzdHJva2UtbGluZWNhcD0ic3F1YXJlIiB3aWR0aD0iMjAiIHN0cm9rZS1taXRlcmxpbWl0PSIxMCIgc2hhcGUtcmVuZGVyaW5nPSJhdXRvIiBzdHJva2Utb3BhY2l0eT0iMSIgZmlsbD0iYmxhY2siIHN0cm9rZS1kYXNoYXJyYXk9Im5vbmUiIGZvbnQtd2VpZ2h0PSJub3JtYWwiIHN0cm9rZS13aWR0aD0iMSIgdmlld0JveD0iMCAwIDIwLjAgMjAuMCIgaGVpZ2h0PSIyMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIiBmb250LWZhbWlseT0iJmFwb3M7RGlhbG9nJmFwb3M7IiBmb250LXN0eWxlPSJub3JtYWwiIHN0cm9rZS1saW5lam9pbj0ibWl0ZXIiIGZvbnQtc2l6ZT0iMTIiIHN0cm9rZS1kYXNob2Zmc2V0PSIwIiBpbWFnZS1yZW5kZXJpbmc9ImF1dG8iPjxkZWZzIGlkPSJnZW5lcmljRGVmcyIgIC8+PGcgID48ZyBmb250LXNpemU9IjE0IiBmaWxsPSJyZ2IoMjU1LDEzLDEzKSIgdGV4dC1yZW5kZXJpbmc9Imdlb21ldHJpY1ByZWNpc2lvbiIgaW1hZ2UtcmVuZGVyaW5nPSJvcHRpbWl6ZVNwZWVkIiBjb2xvci1yZW5kZXJpbmc9Im9wdGltaXplUXVhbGl0eSIgZm9udC1mYW1pbHk9IiZhcG9zO0x1Y2lkYSBHcmFuZGUmYXBvczsiIHN0cm9rZT0icmdiKDI1NSwxMywxMykiIGNvbG9yLWludGVycG9sYXRpb249ImxpbmVhclJHQiIgICAgPjxwYXRoIGQ9Ik0xMC4zNzk5IDE1LjI1MjkgUTguMjc0NCAxNS4yNTI5IDYuOTkyNyAxMy43OTM1IFE1LjcxMDkgMTIuMzM0IDUuNzEwOSA5LjkzNDYgUTUuNzEwOSA3LjUyMTUgNi45OTk1IDYuMDc1NyBROC4yODgxIDQuNjI5OSAxMC40NDE0IDQuNjI5OSBRMTIuNTg3OSA0LjYyOTkgMTMuODc5OSA2LjA3MjMgUTE1LjE3MTkgNy41MTQ2IDE1LjE3MTkgOS45MjA5IFExNS4xNzE5IDEyLjM3NSAxMy44Nzk5IDEzLjgxNCBRMTIuNTg3OSAxNS4yNTI5IDEwLjM3OTkgMTUuMjUyOSBaTTEwLjQwMDQgMTQuMTc5NyBRMTEuOTUyMSAxNC4xNzk3IDEyLjc5OTggMTMuMDYyIFExMy42NDc1IDExLjk0NDMgMTMuNjQ3NSA5LjkwNzIgUTEzLjY0NzUgNy45MzE2IDEyLjc5NjQgNi44MTc0IFExMS45NDUzIDUuNzAzMSAxMC40NDE0IDUuNzAzMSBROC45MzA3IDUuNzAzMSA4LjA4MyA2LjgyMDggUTcuMjM1NCA3LjkzODUgNy4yMzU0IDkuOTI3NyBRNy4yMzU0IDExLjkxMDIgOC4wNzYyIDEzLjA0NDkgUTguOTE3IDE0LjE3OTcgMTAuNDAwNCAxNC4xNzk3IFoiIHN0cm9rZT0ibm9uZSIgICAgLz48L2cgID48L2c+PC9zdmc+",
        PERIODIC_TABLE: "PHN2ZyB2ZXJzaW9uPSIxLjEiIGlkPSJMYXllcl8xIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHhtbG5zOnhsaW5rPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5L3hsaW5rIiB4PSIwcHgiIHk9IjBweCIJIHZpZXdCb3g9IjAgMCAxMDAgMTAwIiBzdHlsZT0iZW5hYmxlLWJhY2tncm91bmQ6bmV3IDAgMCAxMDAgMTAwOyIgeG1sOnNwYWNlPSJwcmVzZXJ2ZSI+PGc+CTxwb2x5Z29uIHN0eWxlPSJmaWxsOiNGNzkzMUU7IiBwb2ludHM9IjEyLjUxLDkuNTY4IDYuMjEyLDkuNTY4IDYuMjEyLDkuNTQgNi4yMTIsMCAtMC4yMTksMCAtMC4yMTksOS41NCAtMC4yMTksNzAuODUgCQkxMi41MSw3MC44NSAJIi8+CTxwb2x5Z29uIHN0eWxlPSJmaWxsOiMyOUFCRTI7IiBwb2ludHM9IjkzLjE3LDAgOTMuMTcsMTAuMzYyIDY3LjQ0NywxMC4zNjIgNjcuNDQ3LDcwLjg1IDY4LjIxOSw3MC44NSA5OS45MDEsNzAuODUgOTkuOTAxLDAgCSIvPgk8bGluZSBzdHlsZT0iZmlsbDpub25lO3N0cm9rZTojMDA3MUJDO3N0cm9rZS13aWR0aDozLjAxMzQ7IiB4MT0iOTcuNDY3IiB5MT0iNjguNTMyIiB4Mj0iOTcuNDY3IiB5Mj0iMi4xOSIvPgk8bGluZSBzdHlsZT0iZmlsbDpub25lO3N0cm9rZTojMDA3MUJDO3N0cm9rZS13aWR0aDozLjAxMzQ7IiB4MT0iNzAuNTk4IiB5MT0iNjguNTMyIiB4Mj0iOTguOTMxIiB5Mj0iNjguNTMyIi8+CTxwb2x5bGluZSBzdHlsZT0iZmlsbDpub25lO3N0cm9rZTojMDBGRkZGO3N0cm9rZS13aWR0aDozLjAxMzQ7IiBwb2ludHM9IjY5LjM3NSw3MC44NSA2OS4zNzUsMTIuMjc4IDk1LjE0MiwxMi4yNzggOTUuMTQyLDEuNzk2IAkJOTkuMjI2LDEuODA1IAkiLz4JPHJlY3QgeD0iMTIuNTA1IiB5PSIzMC4yOTgiIHN0eWxlPSJmaWxsOiNFRDFDMjQ7IiB3aWR0aD0iNTQuODcxIiBoZWlnaHQ9IjQwLjYwOCIvPgk8cmVjdCB4PSI1Ljc3IiB5PSI4MC4xMDciIHN0eWxlPSJmaWxsOiM4Q0M2M0Y7IiB3aWR0aD0iODcuMTQ2IiBoZWlnaHQ9IjE5Ljg5MyIvPgk8bGluZSBzdHlsZT0iZmlsbDpub25lO3N0cm9rZTojRjE1QTI0O3N0cm9rZS13aWR0aDozLjAxMzQ7IiB4MT0iMS43NiIgeTE9IjY4LjM1NiIgeDI9IjExLjUxIiB5Mj0iNjguMzU2Ii8+CTxsaW5lIHN0eWxlPSJmaWxsOm5vbmU7c3Ryb2tlOiNGQkQyM0I7c3Ryb2tlLXdpZHRoOjMuMDEzNDsiIHgxPSIxLjc2IiB5MT0iMCIgeDI9IjEuNzYiIHkyPSI3MC44NSIvPgk8bGluZSBzdHlsZT0iZmlsbDpub25lO3N0cm9rZTojRjE1QTI0O3N0cm9rZS13aWR0aDozLjAxMzQ7IiB4MT0iMTAuMjUiIHkxPSI5LjYwNCIgeDI9IjEwLjI1IiB5Mj0iNzAuODUiLz4JPGxpbmUgc3R5bGU9ImZpbGw6bm9uZTtzdHJva2U6I0JEMUMyNDtzdHJva2Utd2lkdGg6My4wMTM0OyIgeDE9IjEzLjkxNyIgeTE9IjY4LjUzMiIgeDI9IjY2LjU4MyIgeTI9IjY4LjUzMiIvPgk8bGluZSBzdHlsZT0iZmlsbDpub25lO3N0cm9rZTojRjY3N0NBO3N0cm9rZS13aWR0aDozLjAxMzQ7IiB4MT0iMTUuMDA2IiB5MT0iMzAuNzI5IiB4Mj0iMTUuMDA2IiB5Mj0iNzAuODUiLz4JPGxpbmUgc3R5bGU9ImZpbGw6bm9uZTtzdHJva2U6I0JEMUMyNDtzdHJva2Utd2lkdGg6My4wMTM0OyIgeDE9IjY1LjI1IiB5MT0iMzAuNzI5IiB4Mj0iNjUuMjUiIHkyPSI3MC44NSIvPgk8bGluZSBzdHlsZT0iZmlsbDpub25lO3N0cm9rZTojRkJEMjNCO3N0cm9rZS13aWR0aDozLjAxMzQ7IiB4MT0iNS4zODkiIHkxPSIxMi4wNjQiIHgyPSIxMi41MSIgeTI9IjEyLjA2NCIvPgk8cGF0aCBzdHlsZT0iZmlsbDojRUQxQzI0OyIgZD0iTTUuMjA4LDEuMDA0djguNTYzdjEuMDA0aDEuMDA0aDUuMjkzdjU5LjI3MkgwLjc4NlY5LjU0VjEuMDA0SDUuMjA4IE02LjIxMiwwaC02LjQzMXY5LjU0djYxLjMxCQlIMTIuNTFWOS41NjhINi4yMTJWOS41NFYwTDYuMjEyLDB6Ii8+CTxsaW5lIHN0eWxlPSJmaWxsOm5vbmU7c3Ryb2tlOiNGNjc3Q0E7c3Ryb2tlLXdpZHRoOjMuMDEzNDsiIHgxPSIxMy45MTciIHkxPSIzMi44MzgiIHgyPSI2Ni41ODMiIHkyPSIzMi44MzgiLz4JPHBhdGggc3R5bGU9ImZpbGw6bm9uZTtzdHJva2U6I0JEMUMyNDtzdHJva2Utd2lkdGg6My4wMTM0OyIgZD0iTTY2LjU4Myw2OC41MzIiLz4JPHBhdGggc3R5bGU9ImZpbGw6bm9uZTtzdHJva2U6I0JEMUMyNDtzdHJva2Utd2lkdGg6My4wMTM0OyIgZD0iTTEzLjkxNyw2OC41MzIiLz4JPHBhdGggc3R5bGU9ImZpbGw6IzlBMDAwMDsiIGQ9Ik02Ni4zNzEsMzEuMzAydjM4LjU5OUgxMy41MDlWMzEuMzAySDY2LjM3MSBNNjcuMzc2LDMwLjI5OEgxMi41MDV2NDAuNjA4aDU0Ljg3MVYzMC4yOTgJCUw2Ny4zNzYsMzAuMjk4eiIvPgk8cGF0aCBzdHlsZT0iZmlsbDojMDA0RUJDOyIgZD0iTTk4Ljg5NiwxLjAwNHY2OC44NEg2OC40NTJWMTEuMzY3SDkzLjE3aDEuMDA1di0xLjAwNFYxLjAwNEg5OC44OTYgTTk5LjkwMSwwSDkzLjE3djEwLjM2Mkg2Ny40NDcJCVY3MC44NWgwLjc3MWgzMS42ODNWMEw5OS45MDEsMHoiLz4JPGxpbmUgc3R5bGU9ImZpbGw6bm9uZTtzdHJva2U6IzAwOTI0NTtzdHJva2Utd2lkdGg6My4wMTM0OyIgeDE9IjYuOTE3IiB5MT0iOTcuOTYyIiB4Mj0iOTIuOTE2IiB5Mj0iOTcuOTYyIi8+CTxsaW5lIHN0eWxlPSJmaWxsOm5vbmU7c3Ryb2tlOiNEOUUwMjE7c3Ryb2tlLXdpZHRoOjMuMDEzNDsiIHgxPSI4LjE4NyIgeTE9IjgwLjU0MiIgeDI9IjguMTg3IiB5Mj0iMTAwIi8+CTxsaW5lIHN0eWxlPSJmaWxsOm5vbmU7c3Ryb2tlOiMwMDkyNDU7c3Ryb2tlLXdpZHRoOjMuMDEzNDsiIHgxPSI5MC40MzEiIHkxPSI4MC41NDIiIHgyPSI5MC40MzEiIHkyPSIxMDAiLz4JPGxpbmUgc3R5bGU9ImZpbGw6bm9uZTtzdHJva2U6I0Q5RTAyMTtzdHJva2Utd2lkdGg6My4wMTM0OyIgeDE9IjYuOTE3IiB5MT0iODIuMTQxIiB4Mj0iOTIuOTE2IiB5Mj0iODIuMTQxIi8+CTxwYXRoIHN0eWxlPSJmaWxsOiMwMDY4Mzc7IiBkPSJNOTEuOTExLDgxLjExMnYxNy44ODNINi43NzRWODEuMTEySDkxLjkxMSBNOTIuOTE2LDgwLjEwN0g1Ljc3VjEwMGg4Ny4xNDZWODAuMTA3TDkyLjkxNiw4MC4xMDd6IgkJLz48L2c+PC9zdmc+",
        PHOSPHORUS: "PHN2ZyBmaWxsLW9wYWNpdHk9IjEiIHhtbG5zOnhsaW5rPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5L3hsaW5rIiBjb2xvci1yZW5kZXJpbmc9ImF1dG8iIGNvbG9yLWludGVycG9sYXRpb249ImF1dG8iIHRleHQtcmVuZGVyaW5nPSJhdXRvIiBzdHJva2U9ImJsYWNrIiBzdHJva2UtbGluZWNhcD0ic3F1YXJlIiB3aWR0aD0iMjAiIHN0cm9rZS1taXRlcmxpbWl0PSIxMCIgc2hhcGUtcmVuZGVyaW5nPSJhdXRvIiBzdHJva2Utb3BhY2l0eT0iMSIgZmlsbD0iYmxhY2siIHN0cm9rZS1kYXNoYXJyYXk9Im5vbmUiIGZvbnQtd2VpZ2h0PSJub3JtYWwiIHN0cm9rZS13aWR0aD0iMSIgdmlld0JveD0iMCAwIDIwLjAgMjAuMCIgaGVpZ2h0PSIyMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIiBmb250LWZhbWlseT0iJmFwb3M7RGlhbG9nJmFwb3M7IiBmb250LXN0eWxlPSJub3JtYWwiIHN0cm9rZS1saW5lam9pbj0ibWl0ZXIiIGZvbnQtc2l6ZT0iMTIiIHN0cm9rZS1kYXNob2Zmc2V0PSIwIiBpbWFnZS1yZW5kZXJpbmc9ImF1dG8iPjxkZWZzIGlkPSJnZW5lcmljRGVmcyIgIC8+PGcgID48ZyBmb250LXNpemU9IjE0IiBmaWxsPSJyZ2IoMjU1LDEyOCwwKSIgdGV4dC1yZW5kZXJpbmc9Imdlb21ldHJpY1ByZWNpc2lvbiIgaW1hZ2UtcmVuZGVyaW5nPSJvcHRpbWl6ZVNwZWVkIiBjb2xvci1yZW5kZXJpbmc9Im9wdGltaXplUXVhbGl0eSIgZm9udC1mYW1pbHk9IiZhcG9zO0x1Y2lkYSBHcmFuZGUmYXBvczsiIHN0cm9rZT0icmdiKDI1NSwxMjgsMCkiIGNvbG9yLWludGVycG9sYXRpb249ImxpbmVhclJHQiIgICAgPjxwYXRoIGQ9Ik03LjMwNTcgMTUgTDcuMzA1NyA0Ljg4MjggTDEwLjA2MDUgNC44ODI4IFExMS44OTI2IDQuODgyOCAxMi42OTI0IDUuNTAxNSBRMTMuNDkyMiA2LjEyMDEgMTMuNDkyMiA3LjUzNTIgUTEzLjQ5MjIgOS4xNDg0IDEyLjM5ODQgMTAuMDY0NSBRMTEuMzA0NyAxMC45ODA1IDkuMzYzMyAxMC45ODA1IEw4LjcyNzUgMTAuOTgwNSBMOC43Mjc1IDE1IFpNOC43Mjc1IDkuODkzNiBMOS4zMDg2IDkuODkzNiBRMTAuNTg2OSA5Ljg5MzYgMTEuMjg0MiA5LjMwNTcgUTExLjk4MTQgOC43MTc4IDExLjk4MTQgNy42NDQ1IFExMS45ODE0IDYuNzM1NCAxMS40MzQ2IDYuMzQ1NyBRMTAuODg3NyA1Ljk1NjEgOS42MDk0IDUuOTU2MSBMOC43Mjc1IDUuOTU2MSBaIiBzdHJva2U9Im5vbmUiICAgIC8+PC9nICA+PC9nPjwvc3ZnPg\x3d\x3d",
        REDO: "PHN2ZyB2ZXJzaW9uPSIxLjEiIGlkPSJMYXllcl8xIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHhtbG5zOnhsaW5rPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5L3hsaW5rIiB4PSIwcHgiIHk9IjBweCIJIHZpZXdCb3g9IjAgMCAxMDAgMTAwIiBzdHlsZT0iZW5hYmxlLWJhY2tncm91bmQ6bmV3IDAgMCAxMDAgMTAwOyIgeG1sOnNwYWNlPSJwcmVzZXJ2ZSI+PGc+CTxnPgkJCQkJPGxpbmVhckdyYWRpZW50IGlkPSJTVkdJRF8xXyIgZ3JhZGllbnRVbml0cz0idXNlclNwYWNlT25Vc2UiIHgxPSItNTY1LjE2NDIiIHkxPSItMTI2LjU5MyIgeDI9Ii01NjUuMTY0MiIgeTI9Ii05MS45NjUxIiBncmFkaWVudFRyYW5zZm9ybT0ibWF0cml4KDAuOTI1OCAtMC40MDg3IC0wLjQ0ODIgLTEuMDE1MSA1MDQuNzA0MSAtMzE3LjM3NDUpIj4JCQk8c3RvcCAgb2Zmc2V0PSIwLjIzMzEiIHN0eWxlPSJzdG9wLWNvbG9yOiMwMEEzM0UiLz4JCQk8c3RvcCAgb2Zmc2V0PSIwLjI1NDQiIHN0eWxlPSJzdG9wLWNvbG9yOiMwMTlEM0IiLz4JCQk8c3RvcCAgb2Zmc2V0PSIwLjM5NDIiIHN0eWxlPSJzdG9wLWNvbG9yOiMwOTdDMjkiLz4JCQk8c3RvcCAgb2Zmc2V0PSIwLjUzNzQiIHN0eWxlPSJzdG9wLWNvbG9yOiMwRjYxMUEiLz4JCQk8c3RvcCAgb2Zmc2V0PSIwLjY4MzgiIHN0eWxlPSJzdG9wLWNvbG9yOiMxNDRGMTAiLz4JCQk8c3RvcCAgb2Zmc2V0PSIwLjgzNTMiIHN0eWxlPSJzdG9wLWNvbG9yOiMxNjQ0MEEiLz4JCQk8c3RvcCAgb2Zmc2V0PSIxIiBzdHlsZT0ic3RvcC1jb2xvcjojMTc0MDA4Ii8+CQk8L2xpbmVhckdyYWRpZW50PgkJPHBhdGggc3R5bGU9ImZpbGw6dXJsKCNTVkdJRF8xXyk7IiBkPSJNNjYuMjE4LDkuMDU2QzIwLjE3LTEzLjkyNSwyLjg4OSwyOS44MiwyLjg4OSwyOS44MnMtNi4xNDMsMTYuNjU1LTAuNDk3LDI3LjU1OQkJCWMyLjE2NSw0LjE3OSwyLjU2LTI4Ljg2OCwyNi4yNzMtMzAuOTUyQzUyLjYyLDI0LjMyLDY2LjIxOCw5LjA1Niw2Ni4yMTgsOS4wNTZ6Ii8+CQkJCQk8bGluZWFyR3JhZGllbnQgaWQ9IlNWR0lEXzJfIiBncmFkaWVudFVuaXRzPSJ1c2VyU3BhY2VPblVzZSIgeDE9IjkzOS44ODY1IiB5MT0iNDkuOTY5MyIgeDI9IjEwMzYuODcyNiIgeTI9IjQ5Ljk2OTMiIGdyYWRpZW50VHJhbnNmb3JtPSJtYXRyaXgoLTEgMCAwIDEgMTAzOS43NjE3IDApIj4JCQk8c3RvcCAgb2Zmc2V0PSIwIiBzdHlsZT0ic3RvcC1jb2xvcjojMDA3NTYzIi8+CQkJPHN0b3AgIG9mZnNldD0iMC4xMTExIiBzdHlsZT0ic3RvcC1jb2xvcjojMTM5MDUzIi8+CQkJPHN0b3AgIG9mZnNldD0iMC4yNzc2IiBzdHlsZT0ic3RvcC1jb2xvcjojMkNCMTNGIi8+CQkJPHN0b3AgIG9mZnNldD0iMC40NDg0IiBzdHlsZT0ic3RvcC1jb2xvcjojM0ZDQzMwIi8+CQkJPHN0b3AgIG9mZnNldD0iMC42MjMiIHN0eWxlPSJzdG9wLWNvbG9yOiM0Q0RFMjUiLz4JCQk8c3RvcCAgb2Zmc2V0PSIwLjgwMzciIHN0eWxlPSJzdG9wLWNvbG9yOiM1NEU5MUUiLz4JCQk8c3RvcCAgb2Zmc2V0PSIxIiBzdHlsZT0ic3RvcC1jb2xvcjojNTdFRDFDIi8+CQk8L2xpbmVhckdyYWRpZW50PgkJPHBhdGggc3R5bGU9ImZpbGw6dXJsKCNTVkdJRF8yXyk7IiBkPSJNMTAuNzEsMTcuMTEyYzUuNDczLTYuNjA1LDE0LjA3My0xMy43MTMsMjQuODQyLTE2LjIxNgkJCWM4LjQyNy0xLjk1OSwxOC40NDktMS4wMjEsMzAuMDIyLDUuMzc4YzEyLjA1Nyw2LjY2NiwxNS4yODQsMTkuMjQ3LDE4LjAyMywyNS44MDJsNy4zNzEtMy4yNTIJCQljNS41NjEtMi40NTQsOS41MzEsMC4zNzUsOC44MjUsNi4yODRsLTcuMDI4LDU4Ljc0NmMtMC43MDQsNS45MDktNS4zMTEsNy44NjgtMTAuMjM1LDQuMzUzTDM0LjY1NSw2NC4wMTkJCQljLTQuOTIyLTMuNTE1LTQuNDAzLTguMzk5LDEuMTU4LTEwLjg1Mmw4LjEzNy0zLjU5Yy0xLjUyMy00LjYyNS02LjgwNC0xNC4yNTMtMTQuODQxLTIwLjU1MgkJCUM5LjY5OCwxMy44MDgsMi44ODksMjkuODIsMi44ODksMjkuODJTNS4yMzUsMjMuNzE4LDEwLjcxLDE3LjExMnoiLz4JPC9nPgk8bGluZWFyR3JhZGllbnQgaWQ9IlNWR0lEXzNfIiBncmFkaWVudFVuaXRzPSJ1c2VyU3BhY2VPblVzZSIgeDE9IjQ5LjI0OTMiIHkxPSIxNy45NDgxIiB4Mj0iNDkuMjQ5MyIgeTI9Ijk3LjIzMjciPgkJPHN0b3AgIG9mZnNldD0iMCIgc3R5bGU9InN0b3AtY29sb3I6I0I5RkY5RSIvPgkJPHN0b3AgIG9mZnNldD0iMC4xNzkyIiBzdHlsZT0ic3RvcC1jb2xvcjojQjVGRDlDIi8+CQk8c3RvcCAgb2Zmc2V0PSIwLjM0NDIiIHN0eWxlPSJzdG9wLWNvbG9yOiNBQUY3OTYiLz4JCTxzdG9wICBvZmZzZXQ9IjAuNTAzNSIgc3R5bGU9InN0b3AtY29sb3I6Izk3RUU4RCIvPgkJPHN0b3AgIG9mZnNldD0iMC42NTk1IiBzdHlsZT0ic3RvcC1jb2xvcjojN0RFMDdGIi8+CQk8c3RvcCAgb2Zmc2V0PSIwLjgxMyIgc3R5bGU9InN0b3AtY29sb3I6IzVCQ0U2RSIvPgkJPHN0b3AgIG9mZnNldD0iMC45NjI2IiBzdHlsZT0ic3RvcC1jb2xvcjojMzJCOTU5Ii8+CQk8c3RvcCAgb2Zmc2V0PSIxIiBzdHlsZT0ic3RvcC1jb2xvcjojMjdCMzUzIi8+CTwvbGluZWFyR3JhZGllbnQ+CTxwYXRoIHN0eWxlPSJmaWxsOnVybCgjU1ZHSURfM18pOyIgZD0iTTguMDc0LDIyLjQxN2MwLDAsNC40MzctMy4yMDEsMTEuOTM0LTAuNzk5YzE5Ljk3Nyw2LjM5OSwyNi4zOTgsMjkuMTE4LDI2LjM5OCwyOS4xMTgJCXMtNy41MiwzLjMzOC05LjIxMSw0LjM1Yy0xLjY5MywxLjAwOS0zLjA0OCwyLjAyMS0zLjA0OCw0LjA0MWMwLDIuMDIxLDEuNDk1LDIuNDg0LDMuMjg4LDMuODYxCQljMS41MTYsMS4xNjYsNDMuMjA1LDMwLjY5LDQ1LjQ3MiwzMi41MTFjNC4yMTgsMy4zODgsOC4wODEsMC43ODIsNy40NTIsMC42OTJjLTIuNTg3LTAuMzY5LTQuMzE1LTEuODgyLTYuMDk3LTMuMDUJCWMtMy42ODYtMi40MTctNDIuNDI1LTMxLjI2NS00NC41MjctMzMuMDAzYy0wLjQwMy0wLjMzNC0yLjU2OS0xLjEwMy0wLjIyOS0yLjQwMmMzLjIzNS0xLjc5Nyw1LjA4OS0yLjQsOC4wMTktMy42NwkJYzIuODU0LTEuMjM3LDMuMDE1LTIuODMxLDIuNzM1LTMuOTQyYy0wLjQ5NC0xLjk1OS0wLjU5NS0zLjE2NS0zLjI0NC03LjgzOGMtNy41ODYtMTMuMzgyLTE4LjI4NS0yMS44OS0yNS4wNTgtMjMuNTc0CQljLTYuNzcyLTEuNjg0LTEwLjcxNy0wLjE1OS0xMS43MzMsMC41MTVDOS4yMDcsMTkuOSw4LjA3NCwyMi40MTcsOC4wNzQsMjIuNDE3eiIvPjwvZz48L3N2Zz4\x3d",
        REMOVE_LONE_PAIR: "PHN2ZyBmaWxsLW9wYWNpdHk9IjEiIHhtbG5zOnhsaW5rPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5L3hsaW5rIiBjb2xvci1yZW5kZXJpbmc9ImF1dG8iIGNvbG9yLWludGVycG9sYXRpb249ImF1dG8iIHRleHQtcmVuZGVyaW5nPSJhdXRvIiBzdHJva2U9ImJsYWNrIiBzdHJva2UtbGluZWNhcD0ic3F1YXJlIiB3aWR0aD0iMjAiIHN0cm9rZS1taXRlcmxpbWl0PSIxMCIgc2hhcGUtcmVuZGVyaW5nPSJhdXRvIiBzdHJva2Utb3BhY2l0eT0iMSIgZmlsbD0iYmxhY2siIHN0cm9rZS1kYXNoYXJyYXk9Im5vbmUiIGZvbnQtd2VpZ2h0PSJub3JtYWwiIHN0cm9rZS13aWR0aD0iMSIgdmlld0JveD0iMCAwIDIwLjAgMjAuMCIgaGVpZ2h0PSIyMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIiBmb250LWZhbWlseT0iJmFwb3M7RGlhbG9nJmFwb3M7IiBmb250LXN0eWxlPSJub3JtYWwiIHN0cm9rZS1saW5lam9pbj0ibWl0ZXIiIGZvbnQtc2l6ZT0iMTIiIHN0cm9rZS1kYXNob2Zmc2V0PSIwIiBpbWFnZS1yZW5kZXJpbmc9ImF1dG8iPjxkZWZzIGlkPSJnZW5lcmljRGVmcyIgIC8+PGcgID48ZyB0ZXh0LXJlbmRlcmluZz0iZ2VvbWV0cmljUHJlY2lzaW9uIiBjb2xvci1yZW5kZXJpbmc9Im9wdGltaXplUXVhbGl0eSIgY29sb3ItaW50ZXJwb2xhdGlvbj0ibGluZWFyUkdCIiBpbWFnZS1yZW5kZXJpbmc9Im9wdGltaXplU3BlZWQiICAgID48Y2lyY2xlIGZpbGw9Im5vbmUiIHI9IjIiIGN4PSI2IiBjeT0iMTAiICAgICAgLz48Y2lyY2xlIGZpbGw9Im5vbmUiIHI9IjIiIGN4PSIxNCIgY3k9IjEwIiAgICAvPjwvZyAgPjwvZz48L3N2Zz4\x3d",
        REMOVE_RADICAL: "PHN2ZyBmaWxsLW9wYWNpdHk9IjEiIHhtbG5zOnhsaW5rPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5L3hsaW5rIiBjb2xvci1yZW5kZXJpbmc9ImF1dG8iIGNvbG9yLWludGVycG9sYXRpb249ImF1dG8iIHRleHQtcmVuZGVyaW5nPSJhdXRvIiBzdHJva2U9ImJsYWNrIiBzdHJva2UtbGluZWNhcD0ic3F1YXJlIiB3aWR0aD0iMjAiIHN0cm9rZS1taXRlcmxpbWl0PSIxMCIgc2hhcGUtcmVuZGVyaW5nPSJhdXRvIiBzdHJva2Utb3BhY2l0eT0iMSIgZmlsbD0iYmxhY2siIHN0cm9rZS1kYXNoYXJyYXk9Im5vbmUiIGZvbnQtd2VpZ2h0PSJub3JtYWwiIHN0cm9rZS13aWR0aD0iMSIgdmlld0JveD0iMCAwIDIwLjAgMjAuMCIgaGVpZ2h0PSIyMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIiBmb250LWZhbWlseT0iJmFwb3M7RGlhbG9nJmFwb3M7IiBmb250LXN0eWxlPSJub3JtYWwiIHN0cm9rZS1saW5lam9pbj0ibWl0ZXIiIGZvbnQtc2l6ZT0iMTIiIHN0cm9rZS1kYXNob2Zmc2V0PSIwIiBpbWFnZS1yZW5kZXJpbmc9ImF1dG8iPjxkZWZzIGlkPSJnZW5lcmljRGVmcyIgIC8+PGcgID48ZyB0ZXh0LXJlbmRlcmluZz0iZ2VvbWV0cmljUHJlY2lzaW9uIiBjb2xvci1yZW5kZXJpbmc9Im9wdGltaXplUXVhbGl0eSIgY29sb3ItaW50ZXJwb2xhdGlvbj0ibGluZWFyUkdCIiBpbWFnZS1yZW5kZXJpbmc9Im9wdGltaXplU3BlZWQiICAgID48Y2lyY2xlIGZpbGw9Im5vbmUiIHI9IjIiIGN4PSIxMCIgY3k9IjEwIiAgICAvPjwvZyAgPjwvZz48L3N2Zz4\x3d",
        RING_ARBITRARY: "PHN2ZyBmaWxsLW9wYWNpdHk9IjEiIHhtbG5zOnhsaW5rPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5L3hsaW5rIiBjb2xvci1yZW5kZXJpbmc9ImF1dG8iIGNvbG9yLWludGVycG9sYXRpb249ImF1dG8iIHRleHQtcmVuZGVyaW5nPSJhdXRvIiBzdHJva2U9ImJsYWNrIiBzdHJva2UtbGluZWNhcD0ic3F1YXJlIiB3aWR0aD0iMjAiIHN0cm9rZS1taXRlcmxpbWl0PSIxMCIgc2hhcGUtcmVuZGVyaW5nPSJhdXRvIiBzdHJva2Utb3BhY2l0eT0iMSIgZmlsbD0iYmxhY2siIHN0cm9rZS1kYXNoYXJyYXk9Im5vbmUiIGZvbnQtd2VpZ2h0PSJub3JtYWwiIHN0cm9rZS13aWR0aD0iMSIgdmlld0JveD0iMCAwIDIwLjAgMjAuMCIgaGVpZ2h0PSIyMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIiBmb250LWZhbWlseT0iJmFwb3M7RGlhbG9nJmFwb3M7IiBmb250LXN0eWxlPSJub3JtYWwiIHN0cm9rZS1saW5lam9pbj0ibWl0ZXIiIGZvbnQtc2l6ZT0iMTIiIHN0cm9rZS1kYXNob2Zmc2V0PSIwIiBpbWFnZS1yZW5kZXJpbmc9ImF1dG8iPjxkZWZzIGlkPSJnZW5lcmljRGVmcyIgIC8+PGcgID48ZGVmcyBpZD0iZGVmczEiICAgID48bGluZWFyR3JhZGllbnQgeDE9IjE1IiBncmFkaWVudFVuaXRzPSJ1c2VyU3BhY2VPblVzZSIgeDI9IjIwIiB5MT0iMTUiIHkyPSIyMCIgaWQ9ImxpbmVhckdyYWRpZW50MSIgc3ByZWFkTWV0aG9kPSJwYWQiICAgICAgPjxzdG9wIHN0b3Atb3BhY2l0eT0iMSIgc3RvcC1jb2xvcj0iYmx1ZSIgb2Zmc2V0PSIwJSIgICAgICAgIC8+PHN0b3Agc3RvcC1vcGFjaXR5PSIxIiBzdG9wLWNvbG9yPSJibGFjayIgb2Zmc2V0PSIxMDAlIiAgICAgIC8+PC9saW5lYXJHcmFkaWVudCAgICA+PC9kZWZzICAgID48ZyB0ZXh0LXJlbmRlcmluZz0iZ2VvbWV0cmljUHJlY2lzaW9uIiBjb2xvci1yZW5kZXJpbmc9Im9wdGltaXplUXVhbGl0eSIgY29sb3ItaW50ZXJwb2xhdGlvbj0ibGluZWFyUkdCIiBpbWFnZS1yZW5kZXJpbmc9Im9wdGltaXplU3BlZWQiICAgID48Y2lyY2xlIGZpbGw9Im5vbmUiIHI9IjkiIGN4PSIxMCIgY3k9IjEwIiAgICAvPjwvZyAgICA+PGcgZm9udC1zaXplPSIxNCIgZmlsbD0idXJsKCNsaW5lYXJHcmFkaWVudDEpIiB0ZXh0LXJlbmRlcmluZz0iZ2VvbWV0cmljUHJlY2lzaW9uIiBpbWFnZS1yZW5kZXJpbmc9Im9wdGltaXplU3BlZWQiIGNvbG9yLXJlbmRlcmluZz0ib3B0aW1pemVRdWFsaXR5IiBmb250LWZhbWlseT0ic2VyaWYiIHN0cm9rZT0idXJsKCNsaW5lYXJHcmFkaWVudDEpIiBjb2xvci1pbnRlcnBvbGF0aW9uPSJsaW5lYXJSR0IiIGZvbnQtd2VpZ2h0PSJib2xkIiAgICA+PHBhdGggZD0iTTcuMjI1NiAxMy42NjUgUTcuNjA4NCAxMy42MTcyIDcuNzg5NiAxMy40NTY1IFE3Ljk3MDcgMTMuMjk1OSA3Ljk3MDcgMTIuODE3NCBMNy45NzA3IDguNzAyMSBRNy45NzA3IDguMjc4MyA3LjgyMzcgOC4xMTQzIFE3LjY3NjggNy45NTAyIDcuMjI1NiA3Ljg5NTUgTDcuMjI1NiA3LjU1MzcgTDkuODc3OSA3LjU1MzcgTDkuODc3OSA4LjU1ODYgUTEwLjIxMjkgOC4wNTI3IDEwLjcyOSA3LjcyMTIgUTExLjI0NTEgNy4zODk2IDExLjg3NCA3LjM4OTYgUTEyLjc3NjQgNy4zODk2IDEzLjI3MiA3Ljg1NDUgUTEzLjc2NzYgOC4zMTkzIDEzLjc2NzYgOS40ODgzIEwxMy43Njc2IDEyLjg3MjEgUTEzLjc2NzYgMTMuMzQzOCAxMy45MjgyIDEzLjQ4MDUgUTE0LjA4ODkgMTMuNjE3MiAxNC40NjQ4IDEzLjY2NSBMMTQuNDY0OCAxNCBMMTEuMTc2OCAxNCBMMTEuMTc2OCAxMy42NjUgUTExLjU1MjcgMTMuNTg5OCAxMS42ODk1IDEzLjQ2IFExMS44MjYyIDEzLjMzMDEgMTEuODI2MiAxMi44NzIxIEwxMS44MjYyIDkuNDgxNCBRMTEuODI2MiA5LjAwMjkgMTEuNzMwNSA4Ljc2MzcgUTExLjU2NjQgOC4zMzMgMTEuMDgxMSA4LjMzMyBRMTAuNzE4OCA4LjMzMyAxMC40MTQ2IDguNTk2MiBRMTAuMTEwNCA4Ljg1OTQgOS45NDYzIDkuMTI2IEw5Ljk0NjMgMTIuODcyMSBROS45NDYzIDEzLjMzMDEgMTAuMDgzIDEzLjQ2IFExMC4yMTk3IDEzLjU4OTggMTAuNTk1NyAxMy42NjUgTDEwLjU5NTcgMTQgTDcuMjI1NiAxNCBaIiBzdHJva2U9Im5vbmUiICAgIC8+PC9nICA+PC9nPjwvc3ZnPg\x3d\x3d",
        SILICON: "PHN2ZyBmaWxsLW9wYWNpdHk9IjEiIHhtbG5zOnhsaW5rPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5L3hsaW5rIiBjb2xvci1yZW5kZXJpbmc9ImF1dG8iIGNvbG9yLWludGVycG9sYXRpb249ImF1dG8iIHRleHQtcmVuZGVyaW5nPSJhdXRvIiBzdHJva2U9ImJsYWNrIiBzdHJva2UtbGluZWNhcD0ic3F1YXJlIiB3aWR0aD0iMjAiIHN0cm9rZS1taXRlcmxpbWl0PSIxMCIgc2hhcGUtcmVuZGVyaW5nPSJhdXRvIiBzdHJva2Utb3BhY2l0eT0iMSIgZmlsbD0iYmxhY2siIHN0cm9rZS1kYXNoYXJyYXk9Im5vbmUiIGZvbnQtd2VpZ2h0PSJub3JtYWwiIHN0cm9rZS13aWR0aD0iMSIgdmlld0JveD0iMCAwIDIwLjAgMjAuMCIgaGVpZ2h0PSIyMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIiBmb250LWZhbWlseT0iJmFwb3M7RGlhbG9nJmFwb3M7IiBmb250LXN0eWxlPSJub3JtYWwiIHN0cm9rZS1saW5lam9pbj0ibWl0ZXIiIGZvbnQtc2l6ZT0iMTIiIHN0cm9rZS1kYXNob2Zmc2V0PSIwIiBpbWFnZS1yZW5kZXJpbmc9ImF1dG8iPjxkZWZzIGlkPSJnZW5lcmljRGVmcyIgIC8+PGcgID48ZyBmb250LXNpemU9IjE0IiBmaWxsPSJyZ2IoMjQwLDIwMCwxNjApIiB0ZXh0LXJlbmRlcmluZz0iZ2VvbWV0cmljUHJlY2lzaW9uIiBpbWFnZS1yZW5kZXJpbmc9Im9wdGltaXplU3BlZWQiIGNvbG9yLXJlbmRlcmluZz0ib3B0aW1pemVRdWFsaXR5IiBmb250LWZhbWlseT0iJmFwb3M7THVjaWRhIEdyYW5kZSZhcG9zOyIgc3Ryb2tlPSJyZ2IoMjQwLDIwMCwxNjApIiBjb2xvci1pbnRlcnBvbGF0aW9uPSJsaW5lYXJSR0IiICAgID48cGF0aCBkPSJNNy4yODgxIDE1LjI1MjkgUTYuMjY5NSAxNS4yNTI5IDQuNjgzNiAxNC44MDg2IEw0LjY4MzYgMTMuMzg2NyBRNi4zOTI2IDE0LjE3OTcgNy40OTMyIDE0LjE3OTcgUTguMzQwOCAxNC4xNzk3IDguODU2OSAxMy43MzU0IFE5LjM3MyAxMy4yOTEgOS4zNzMgMTIuNTY2NCBROS4zNzMgMTEuOTcxNyA5LjAzNDcgMTEuNTU0NyBROC42OTYzIDExLjEzNzcgNy43ODcxIDEwLjYyNSBMNy4wODk4IDEwLjIyMTcgUTUuNzk3OSA5LjQ4MzQgNS4yNjgxIDguODMwNiBRNC43MzgzIDguMTc3NyA0LjczODMgNy4zMDk2IFE0LjczODMgNi4xNDA2IDUuNTg1OSA1LjM4NTMgUTYuNDMzNiA0LjYyOTkgNy43NDYxIDQuNjI5OSBROC45MTUgNC42Mjk5IDEwLjIxMzkgNS4wMTk1IEwxMC4yMTM5IDYuMzMyIFE4LjYxNDMgNS43MDMxIDcuODI4MSA1LjcwMzEgUTcuMDgzIDUuNzAzMSA2LjU5NzcgNi4wOTk2IFE2LjExMjMgNi40OTYxIDYuMTEyMyA3LjA5NzcgUTYuMTEyMyA3LjYwMzUgNi40Njc4IDcuOTkzMiBRNi44MjMyIDguMzgyOCA3Ljc2NjYgOC45MjI5IEw4LjQ5MTIgOS4zMzMgUTkuODAzNyAxMC4wNzgxIDEwLjMyMzIgMTAuNzQxMiBRMTAuODQyOCAxMS40MDQzIDEwLjg0MjggMTIuMzM0IFExMC44NDI4IDEzLjY1MzMgOS44Njg3IDE0LjQ1MzEgUTguODk0NSAxNS4yNTI5IDcuMjg4MSAxNS4yNTI5IFpNMTMuMzQ2NyAxNSBMMTMuMzQ2NyA3LjU3NjIgTDE0LjY5MzQgNy41NzYyIEwxNC42OTM0IDE1IFpNMTMuMzQ2NyA2LjIyOTUgTDEzLjM0NjcgNC44ODI4IEwxNC42OTM0IDQuODgyOCBMMTQuNjkzNCA2LjIyOTUgWiIgc3Ryb2tlPSJub25lIiAgICAvPjwvZyAgPjwvZz48L3N2Zz4\x3d",
        SULFUR: "PHN2ZyBmaWxsLW9wYWNpdHk9IjEiIHhtbG5zOnhsaW5rPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5L3hsaW5rIiBjb2xvci1yZW5kZXJpbmc9ImF1dG8iIGNvbG9yLWludGVycG9sYXRpb249ImF1dG8iIHRleHQtcmVuZGVyaW5nPSJhdXRvIiBzdHJva2U9ImJsYWNrIiBzdHJva2UtbGluZWNhcD0ic3F1YXJlIiB3aWR0aD0iMjAiIHN0cm9rZS1taXRlcmxpbWl0PSIxMCIgc2hhcGUtcmVuZGVyaW5nPSJhdXRvIiBzdHJva2Utb3BhY2l0eT0iMSIgZmlsbD0iYmxhY2siIHN0cm9rZS1kYXNoYXJyYXk9Im5vbmUiIGZvbnQtd2VpZ2h0PSJub3JtYWwiIHN0cm9rZS13aWR0aD0iMSIgdmlld0JveD0iMCAwIDIwLjAgMjAuMCIgaGVpZ2h0PSIyMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIiBmb250LWZhbWlseT0iJmFwb3M7RGlhbG9nJmFwb3M7IiBmb250LXN0eWxlPSJub3JtYWwiIHN0cm9rZS1saW5lam9pbj0ibWl0ZXIiIGZvbnQtc2l6ZT0iMTIiIHN0cm9rZS1kYXNob2Zmc2V0PSIwIiBpbWFnZS1yZW5kZXJpbmc9ImF1dG8iPjxkZWZzIGlkPSJnZW5lcmljRGVmcyIgIC8+PGcgID48ZyBmb250LXNpemU9IjE0IiBmaWxsPSJyZ2IoMjA0LDEwMiwwKSIgdGV4dC1yZW5kZXJpbmc9Imdlb21ldHJpY1ByZWNpc2lvbiIgaW1hZ2UtcmVuZGVyaW5nPSJvcHRpbWl6ZVNwZWVkIiBjb2xvci1yZW5kZXJpbmc9Im9wdGltaXplUXVhbGl0eSIgZm9udC1mYW1pbHk9IiZhcG9zO0x1Y2lkYSBHcmFuZGUmYXBvczsiIHN0cm9rZT0icmdiKDIwNCwxMDIsMCkiIGNvbG9yLWludGVycG9sYXRpb249ImxpbmVhclJHQiIgICAgPjxwYXRoIGQ9Ik05LjI4ODEgMTUuMjUyOSBROC4yNjk1IDE1LjI1MjkgNi42ODM2IDE0LjgwODYgTDYuNjgzNiAxMy4zODY3IFE4LjM5MjYgMTQuMTc5NyA5LjQ5MzIgMTQuMTc5NyBRMTAuMzQwOCAxNC4xNzk3IDEwLjg1NjkgMTMuNzM1NCBRMTEuMzczIDEzLjI5MSAxMS4zNzMgMTIuNTY2NCBRMTEuMzczIDExLjk3MTcgMTEuMDM0NyAxMS41NTQ3IFExMC42OTYzIDExLjEzNzcgOS43ODcxIDEwLjYyNSBMOS4wODk4IDEwLjIyMTcgUTcuNzk3OSA5LjQ4MzQgNy4yNjgxIDguODMwNiBRNi43MzgzIDguMTc3NyA2LjczODMgNy4zMDk2IFE2LjczODMgNi4xNDA2IDcuNTg1OSA1LjM4NTMgUTguNDMzNiA0LjYyOTkgOS43NDYxIDQuNjI5OSBRMTAuOTE1IDQuNjI5OSAxMi4yMTM5IDUuMDE5NSBMMTIuMjEzOSA2LjMzMiBRMTAuNjE0MyA1LjcwMzEgOS44MjgxIDUuNzAzMSBROS4wODMgNS43MDMxIDguNTk3NyA2LjA5OTYgUTguMTEyMyA2LjQ5NjEgOC4xMTIzIDcuMDk3NyBROC4xMTIzIDcuNjAzNSA4LjQ2NzggNy45OTMyIFE4LjgyMzIgOC4zODI4IDkuNzY2NiA4LjkyMjkgTDEwLjQ5MTIgOS4zMzMgUTExLjgwMzcgMTAuMDc4MSAxMi4zMjMyIDEwLjc0MTIgUTEyLjg0MjggMTEuNDA0MyAxMi44NDI4IDEyLjMzNCBRMTIuODQyOCAxMy42NTMzIDExLjg2ODcgMTQuNDUzMSBRMTAuODk0NSAxNS4yNTI5IDkuMjg4MSAxNS4yNTI5IFoiIHN0cm9rZT0ibm9uZSIgICAgLz48L2cgID48L2c+PC9zdmc+",
        TEMPLATES: "PHN2ZyB2ZXJzaW9uPSIxLjEiIGlkPSJMYXllcl8xIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHhtbG5zOnhsaW5rPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5L3hsaW5rIiB4PSIwcHgiIHk9IjBweCIJIHZpZXdCb3g9IjAgMCAxMDAgMTAwIiBzdHlsZT0iZW5hYmxlLWJhY2tncm91bmQ6bmV3IDAgMCAxMDAgMTAwOyIgeG1sOnNwYWNlPSJwcmVzZXJ2ZSI+PGc+CTxnPgkJCQkJPGxpbmVhckdyYWRpZW50IGlkPSJTVkdJRF8xXyIgZ3JhZGllbnRVbml0cz0idXNlclNwYWNlT25Vc2UiIHgxPSItNzkuNTkzNCIgeTE9Ii04NzUuODg3NyIgeDI9Ii0yNC4wNTUyIiB5Mj0iLTg3NS44ODc3IiBncmFkaWVudFRyYW5zZm9ybT0ibWF0cml4KDAuOTM5IC0wLjM0MzkgMC4zNDM5IDAuOTM5IDM3Ni4xMzA4IDg2OC44MTQxKSI+CQkJPHN0b3AgIG9mZnNldD0iMCIgc3R5bGU9InN0b3AtY29sb3I6IzdBNzVCMyIvPgkJCTxzdG9wICBvZmZzZXQ9IjAuMjEyMiIgc3R5bGU9InN0b3AtY29sb3I6Izc2NzFCMSIvPgkJCTxzdG9wICBvZmZzZXQ9IjAuNDM0IiBzdHlsZT0ic3RvcC1jb2xvcjojNjk2NkFBIi8+CQkJPHN0b3AgIG9mZnNldD0iMC41IiBzdHlsZT0ic3RvcC1jb2xvcjojNjQ2MUE3Ii8+CQkJPHN0b3AgIG9mZnNldD0iMC41Mzc5IiBzdHlsZT0ic3RvcC1jb2xvcjojNUU1QUEzIi8+CQkJPHN0b3AgIG9mZnNldD0iMC42NDU5IiBzdHlsZT0ic3RvcC1jb2xvcjojNTE0QzlCIi8+CQkJPHN0b3AgIG9mZnNldD0iMC43Nzc3IiBzdHlsZT0ic3RvcC1jb2xvcjojNDk0NDk2Ii8+CQkJPHN0b3AgIG9mZnNldD0iMSIgc3R5bGU9InN0b3AtY29sb3I6IzQ3NDE5NSIvPgkJPC9saW5lYXJHcmFkaWVudD4JCTxwYXRoIHN0eWxlPSJmaWxsOnVybCgjU1ZHSURfMV8pOyIgZD0iTTQ2LjE3Nyw2Ny45MjVjMCwwLTAuMTksMS44MSwwLjI5MSwyLjU5NmMwLjQ3OSwwLjc4NCwxLjQwNiwxLjIxMywxLjQwNiwxLjIxMwkJCWMxLjUxNSwwLjk4MiwyLjU5MiwwLjA5NSwyLjU5MiwwLjA5NWMxLjE0NS0xLjE0NywyLjUyMy0xLjY0MywzLjYxMS0xLjE0OGMxLjY0MSwwLjc0NSwxLjc4MiwzLjA4LDAuNTk5LDUuNjc1CQkJYy0xLjE4NiwyLjU5My0zLjIzNiw0LjQ2LTQuODgyLDMuNzE4Yy0xLjE4NS0wLjUzNy0xLjcxMS0yLjEwOC0xLjQ1NS0zLjkxN2MwLDAsMC4yNzQtMS42MjEtMS45MzYtMS44NjgJCQljMCwwLTAuODE3LTAuMjg1LTEuNzc3LTAuMTIxYy0wLjk5NSwwLjE3NS0xLjkxMSwxLjEwOC0xLjkxMSwxLjEwOGwtNy4xNTEsMTUuMDA4TDAuMDgsNzMuNDY4bDE2Ljg1NC0zNS4zOTNsMTIuNjAzLDUuOTY4CQkJYzAsMCwxLjU1OCwwLjU5LDEuMzc4LDEuNDI0Yy0wLjExLDAuNTE1LTAuODk3LDAuNjQ2LTAuODk3LDAuNjQ2Yy0yLjM2MS0wLjItNC4zNjQsMC41NC01LjEwOSwyLjExNAkJCWMtMS4xMjQsMi4zNzIsMS4wMTksNS43MzgsNC43ODYsNy41MTdjMy43NjQsMS43NzYsNy43MjgsMS4yOTcsOC44NTYtMS4wNzRjMC44MTctMS43MjEtMC4wODItMy45Ni0yLjA3LTUuNzQyCQkJYzAsMC0wLjYwMy0wLjk1MiwwLjU5Ni0xLjFjMC43MjctMC4wOTIsMS40NjEsMC40ODMsMS40NjEsMC40ODNsMTMuODg0LDYuNTc3TDQ2LjE3Nyw2Ny45MjV6Ii8+CQkJCQk8bGluZWFyR3JhZGllbnQgaWQ9IlNWR0lEXzJfIiBncmFkaWVudFVuaXRzPSJ1c2VyU3BhY2VPblVzZSIgeDE9Ii00OS41NzM2IiB5MT0iLTkwNS4xNDYyIiB4Mj0iNS45NjQ3IiB5Mj0iLTkwNS4xNDYyIiBncmFkaWVudFRyYW5zZm9ybT0ibWF0cml4KDAuOTM5IC0wLjM0MzkgMC4zNDM5IDAuOTM5IDM3Ni4xMzA4IDg2OC44MTQxKSI+CQkJPHN0b3AgIG9mZnNldD0iMCIgc3R5bGU9InN0b3AtY29sb3I6IzU3RUQxQyIvPgkJCTxzdG9wICBvZmZzZXQ9IjAuMTk2MyIgc3R5bGU9InN0b3AtY29sb3I6IzU0RTkxRSIvPgkJCTxzdG9wICBvZmZzZXQ9IjAuMzc3IiBzdHlsZT0ic3RvcC1jb2xvcjojNENERTI1Ii8+CQkJPHN0b3AgIG9mZnNldD0iMC41NTE2IiBzdHlsZT0ic3RvcC1jb2xvcjojM0ZDQzMwIi8+CQkJPHN0b3AgIG9mZnNldD0iMC43MjI0IiBzdHlsZT0ic3RvcC1jb2xvcjojMkNCMTNGIi8+CQkJPHN0b3AgIG9mZnNldD0iMC44ODg5IiBzdHlsZT0ic3RvcC1jb2xvcjojMTM5MDUzIi8+CQkJPHN0b3AgIG9mZnNldD0iMSIgc3R5bGU9InN0b3AtY29sb3I6IzAwNzU2MyIvPgkJPC9saW5lYXJHcmFkaWVudD4JCTxwYXRoIHN0eWxlPSJmaWxsOnVybCgjU1ZHSURfMl8pOyIgZD0iTTY0LjExLDMwLjQ1NmMwLDAtMC44MDQsMS40NDctMC4xMzMsMS45NjhjMC40MTgsMC4zMjMsMS4xMDEtMC4wODMsMS4xMDEtMC4wODMJCQljMS42NzUtMS42NzUsMy42ODEtMi4zOTgsNS4yNzEtMS42NzdjMi4zOTQsMS4wODksMi45MzgsNS4wMzUsMS4yMTYsOC44MThjLTEuNzI3LDMuNzgzLTUuMDY3LDUuOTczLTcuNDY0LDQuODg4CQkJYy0xLjczMy0wLjc4Ny0yLjQ5My0zLjA3Ny0yLjEyNS01LjcxOWMwLDAtMC4xNjYtMS4xMTItMS4xNzQtMC40NTNjLTAuNjEzLDAuMzk1LTAuODM3LDEuMjY0LTAuODM3LDEuMjY0bC02LjI3MywxMy4wMjMJCQljMC0wLjAwMi0xNC45MzEtNy4wNzYtMTQuOTMxLTcuMDc2cy0xLjMwMi0wLjIxOS0yLjE3OSwwLjI5MmMtMC44MzksMC40OS0xLjI3OCwxLjIzNC0xLjI3OCwxLjIzNAkJCWMtMS41MjYsMS42MTUtMC4yNjYsMi42Ny0wLjI2NiwyLjY3YzEuMzY2LDEuMjIxLDEuOTc5LDIuNzU3LDEuNDIsMy45MzRjLTAuNzcsMS42MjctMy41NSwxLjUyNS02LjEzNCwwLjMwOQkJCWMtMi41NzgtMS4yMjEtMy45ODQtMy4wOTUtMy4yMTMtNC43MjFjMC41MS0xLjA4LDEuODgzLTEuNTg5LDMuNDk4LTEuNDVjMCwwLDEuMzk5LTAuMDE1LDEuOTE5LTEuNzQxYzAsMCwwLjQzLTAuOTI5LDAuMjkxLTEuODM2CQkJYy0wLjE0Ni0wLjkwOS0xLjQ1Mi0yLjE5Mi0xLjQ1Mi0yLjE5MmwtMTMuMTYzLTYuMjM5TDM1LjA2NCwwLjI3NGwxMi4yNjIsNS44MTJsLTAuMDA5LDAuMDU3YzAsMCwxLjU1OCwwLjU4LDEuMzkzLDEuNDE2CQkJYy0wLjEwNSwwLjUxNS0wLjg5NCwwLjY1MS0wLjg5NCwwLjY1MWMtMi4zNTktMC4xOC00LjM1MiwwLjU3Ni01LjA4NSwyLjE1OGMtMS4xMDksMi4zNzgsMS4wNTksNS43MjcsNC44NCw3LjQ3NAkJCWMzLjc4MSwxLjc0Niw3Ljc0MywxLjIzMyw4Ljg1Mi0xLjE0OGMwLjgwNi0xLjcyNi0wLjEyMy0zLjk1Ny0yLjEyLTUuNzJjMCwwLTAuNjEtMC45NDYsMC41ODYtMS4xMDYJCQljMC43MjUtMC4wOTksMS40MywwLjQ2MywxLjQzLDAuNDYzbDAsMGwxNC4yMjcsNi43NTdMNjQuMTEsMzAuNDU2eiIvPgkJCQkJPGxpbmVhckdyYWRpZW50IGlkPSJTVkdJRF8zXyIgZ3JhZGllbnRVbml0cz0idXNlclNwYWNlT25Vc2UiIHgxPSI2MzAuMDQ2NCIgeTE9Ii0yNjI3LjA3MiIgeDI9IjY4NS41MDk5IiB5Mj0iLTI2MjcuMDcyIiBncmFkaWVudFRyYW5zZm9ybT0ibWF0cml4KDAuNTkwMSAtMC44MDczIDAuODA3MyAwLjU5MDEgMTgxMC4zOTUzIDIxNTcuOTcxMikiPgkJCTxzdG9wICBvZmZzZXQ9IjAiIHN0eWxlPSJzdG9wLWNvbG9yOiNFRDFDMjQiLz4JCQk8c3RvcCAgb2Zmc2V0PSIxIiBzdHlsZT0ic3RvcC1jb2xvcjojQTEwMzA5Ii8+CQk8L2xpbmVhckdyYWRpZW50PgkJPHBhdGggc3R5bGU9ImZpbGw6dXJsKCNTVkdJRF8zXyk7IiBkPSJNNzguNjEzLDU2Ljc1OGMwLDAtMS41ODEsMC4zMzctMS44OTYtMC40NTRjLTAuMTk3LTAuNDg3LDAuMzgyLTEuMDMsMC4zODItMS4wMwkJCWMyLjA3Ni0xLjE0MywzLjMzMi0yLjg2NiwzLjA3My00LjU4OGMtMC4zODItMi41OTctNC4wMzktNC4yMDYtOC4xNjMtMy42Yy00LjEyLDAuNjA0LTcuMTUzLDMuMjAyLTYuNzY3LDUuNzk4CQkJYzAuMjc3LDEuODgzLDIuMjcxLDMuMjQ2LDQuOTE5LDMuNjIzYzAsMCwxLjAyOSwwLjQ2MiwwLjExNCwxLjI0OWMtMC41NTEsMC40NzYtMS40NjcsMC40MjktMS40NjcsMC40MjlsLTEzLjM3LDEuOTc1CQkJbDIuMDE1LDEzLjY1YzAsMCwwLjE0NywxLjYyMywwLjk5NiwxLjY4NmMwLjUyNSwwLjAzNSwwLjg3LTAuNjc5LDAuODctMC42NzljMC40NjItMi4zMjYsMS43MjgtNC4wMzksMy40NTItNC4zMTcJCQljMi41OTItMC40MTksNS4yNDUsMi41NjMsNS45MTcsNi42NjNjMC42NjksNC4xMDQtMC44ODksNy43NzMtMy40ODcsOC4xOTVjLTEuODgzLDAuMzA4LTMuNzg5LTEuMTc2LTQuOTU1LTMuNTc1CQkJYzAsMC0wLjc1Mi0wLjgzOS0xLjIyNiwwLjI2N2MtMC4yODksMC42NzEtMC4xMTgsMS41OTMtMC4xMTgsMS41OTNsMi4yMTUsMTUuMjg5bDM4Ljg3Mi01LjY2NGwtNS42NzgtMzguNzcyCQkJQzk0LjMxMiw1NC40OTQsODUuODEsNTUuNzA3LDc4LjYxMyw1Ni43NTh6Ii8+CTwvZz4JCQk8cmFkaWFsR3JhZGllbnQgaWQ9IlNWR0lEXzRfIiBjeD0iMjkzNC4xMDUyIiBjeT0iLTMyOTYuMjg5OCIgcj0iMTAuNTczOCIgZ3JhZGllbnRUcmFuc2Zvcm09Im1hdHJpeCgtMC41NTIgLTAuODEzOCAwLjgwNzcgLTAuNTU2MiA0MzA2LjUxMzIgNjIzLjE3MTgpIiBncmFkaWVudFVuaXRzPSJ1c2VyU3BhY2VPblVzZSI+CQk8c3RvcCAgb2Zmc2V0PSIwIiBzdHlsZT0ic3RvcC1jb2xvcjojODBFMEVGIi8+CQk8c3RvcCAgb2Zmc2V0PSIwLjQ5NjkiIHN0eWxlPSJzdG9wLWNvbG9yOiM2NUIxRDkiLz4JCTxzdG9wICBvZmZzZXQ9IjAuNjA2NSIgc3R5bGU9InN0b3AtY29sb3I6IzVGQTZEMyIvPgkJPHN0b3AgIG9mZnNldD0iMC44MDEyIiBzdHlsZT0ic3RvcC1jb2xvcjojNEQ4N0MyIi8+CQk8c3RvcCAgb2Zmc2V0PSIxIiBzdHlsZT0ic3RvcC1jb2xvcjojMzg2MkFFIi8+CTwvcmFkaWFsR3JhZGllbnQ+CTxwYXRoIHN0eWxlPSJmaWxsOnVybCgjU1ZHSURfNF8pOyIgZD0iTTE4LjYzNiw2MC4xODhjNC43Mi0zLjI0OCwxMS4xNTMtMi4wMzEsMTQuMzc2LDIuNzIyYzMuMjE4LDQuNzU1LDIuMDE4LDExLjIzOC0yLjcsMTQuNDg3CQljLTQuNzEsMy4yNDUtMTEuMTU0LDIuMDI4LTE0LjM4NC0yLjczQzEyLjcwNiw2OS45MjEsMTMuOTIyLDYzLjQzMiwxOC42MzYsNjAuMTg4eiIvPgk8cGF0aCBzdHlsZT0iZmlsbDpub25lO3N0cm9rZTojMkUzMTkyO3N0cm9rZS13aWR0aDowLjkyODsiIGQ9Ik0xOC42MzYsNjAuMTg4YzQuNzItMy4yNDgsMTEuMTUzLTIuMDMxLDE0LjM3NiwyLjcyMgkJYzMuMjE4LDQuNzU1LDIuMDE4LDExLjIzOC0yLjcsMTQuNDg3Yy00LjcxLDMuMjQ1LTExLjE1NCwyLjAyOC0xNC4zODQtMi43M0MxMi43MDYsNjkuOTIxLDEzLjkyMiw2My40MzIsMTguNjM2LDYwLjE4OHoiLz4JCQk8bGluZWFyR3JhZGllbnQgaWQ9IlNWR0lEXzVfIiBncmFkaWVudFVuaXRzPSJ1c2VyU3BhY2VPblVzZSIgeDE9Ii00NjQuMDkzOCIgeTE9IjM0NS42MjEiIHgyPSItNDY0LjA5MzgiIHkyPSIzMzQuMDE0IiBncmFkaWVudFRyYW5zZm9ybT0ibWF0cml4KDAuOTk5NiAwLjAyNzEgLTAuMDI3MSAwLjk5OTYgNDk3Ljc0MDUgLTI2MS4yNTk4KSI+CQk8c3RvcCAgb2Zmc2V0PSIwIiBzdHlsZT0ic3RvcC1jb2xvcjojNjVCMUQ5Ii8+CQk8c3RvcCAgb2Zmc2V0PSIwLjE1OTYiIHN0eWxlPSJzdG9wLWNvbG9yOiM2REJDREUiLz4JCTxzdG9wICBvZmZzZXQ9IjAuNDQyNCIgc3R5bGU9InN0b3AtY29sb3I6IzgxREJFRCIvPgkJPHN0b3AgIG9mZnNldD0iMC42NDQyIiBzdHlsZT0ic3RvcC1jb2xvcjojOTJGNEY5Ii8+CTwvbGluZWFyR3JhZGllbnQ+CTxwYXRoIHN0eWxlPSJmaWxsOnVybCgjU1ZHSURfNV8pOyIgZD0iTTMyLjYyNCw2Ni4zOThjLTAuMDY5LDMuMDQzLTMuNzA4LDUuMzgzLTguMTM4LDUuMjQ4Yy00LjQyLTAuMTQxLTcuOTQ1LTIuNzE2LTcuODgtNS43NDMJCWMwLjA2NS0zLjAzOSwzLjc5Ni01Ljk5OSw4LjIxNS01Ljg1OEMyOS4yNDcsNjAuMTgzLDMyLjY5OCw2My4zNjksMzIuNjI0LDY2LjM5OHoiLz4JCQk8cmFkaWFsR3JhZGllbnQgaWQ9IlNWR0lEXzZfIiBjeD0iMjk1NS40MjY1IiBjeT0iLTMyNTkuODE3OSIgcj0iMTAuNTczOSIgZ3JhZGllbnRUcmFuc2Zvcm09Im1hdHJpeCgtMC41NTIgLTAuODEzOCAwLjgwNzcgLTAuNTU2MiA0MzA2LjUxMzIgNjIzLjE3MTgpIiBncmFkaWVudFVuaXRzPSJ1c2VyU3BhY2VPblVzZSI+CQk8c3RvcCAgb2Zmc2V0PSIwIiBzdHlsZT0ic3RvcC1jb2xvcjojODBFMEVGIi8+CQk8c3RvcCAgb2Zmc2V0PSIwLjQ5NjkiIHN0eWxlPSJzdG9wLWNvbG9yOiM2NUIxRDkiLz4JCTxzdG9wICBvZmZzZXQ9IjAuNjA2NSIgc3R5bGU9InN0b3AtY29sb3I6IzVGQTZEMyIvPgkJPHN0b3AgIG9mZnNldD0iMC44MDEyIiBzdHlsZT0ic3RvcC1jb2xvcjojNEQ4N0MyIi8+CQk8c3RvcCAgb2Zmc2V0PSIxIiBzdHlsZT0ic3RvcC1jb2xvcjojMzg2MkFFIi8+CTwvcmFkaWFsR3JhZGllbnQ+CTxwYXRoIHN0eWxlPSJmaWxsOnVybCgjU1ZHSURfNl8pOyIgZD0iTTM2LjMyNSwyMi41NTFjNC43Mi0zLjI0OCwxMS4xNTMtMi4wMzEsMTQuMzc3LDIuNzIzYzMuMjE3LDQuNzUzLDIuMDE3LDExLjIzOC0yLjcsMTQuNDg2CQljLTQuNzExLDMuMjQ3LTExLjE1NCwyLjAyOC0xNC4zODQtMi43MjlDMzAuMzk2LDMyLjI4NCwzMS42MTIsMjUuNzk1LDM2LjMyNSwyMi41NTF6Ii8+CTxwYXRoIHN0eWxlPSJmaWxsOm5vbmU7c3Ryb2tlOiMyRTMxOTI7c3Ryb2tlLXdpZHRoOjAuOTI4OyIgZD0iTTM2LjMyNSwyMi41NTFjNC43Mi0zLjI0OCwxMS4xNTMtMi4wMzEsMTQuMzc3LDIuNzIzCQljMy4yMTcsNC43NTMsMi4wMTcsMTEuMjM4LTIuNywxNC40ODZjLTQuNzExLDMuMjQ3LTExLjE1NCwyLjAyOC0xNC4zODQtMi43MjlDMzAuMzk2LDMyLjI4NCwzMS42MTIsMjUuNzk1LDM2LjMyNSwyMi41NTF6Ii8+CQkJPGxpbmVhckdyYWRpZW50IGlkPSJTVkdJRF83XyIgZ3JhZGllbnRVbml0cz0idXNlclNwYWNlT25Vc2UiIHgxPSItNDQ3LjQzIiB5MT0iMzA3LjUxNjUiIHgyPSItNDQ3LjQzIiB5Mj0iMjk1LjkwOTUiIGdyYWRpZW50VHJhbnNmb3JtPSJtYXRyaXgoMC45OTk2IDAuMDI3MSAtMC4wMjcxIDAuOTk5NiA0OTcuNzQwNSAtMjYxLjI1OTgpIj4JCTxzdG9wICBvZmZzZXQ9IjAiIHN0eWxlPSJzdG9wLWNvbG9yOiM2NUIxRDkiLz4JCTxzdG9wICBvZmZzZXQ9IjAuMTU5NiIgc3R5bGU9InN0b3AtY29sb3I6IzZEQkNERSIvPgkJPHN0b3AgIG9mZnNldD0iMC40NDI0IiBzdHlsZT0ic3RvcC1jb2xvcjojODFEQkVEIi8+CQk8c3RvcCAgb2Zmc2V0PSIwLjY0NDIiIHN0eWxlPSJzdG9wLWNvbG9yOiM5MkY0RjkiLz4JPC9saW5lYXJHcmFkaWVudD4JPHBhdGggc3R5bGU9ImZpbGw6dXJsKCNTVkdJRF83Xyk7IiBkPSJNNTAuMzEzLDI4Ljc2MmMtMC4wNjksMy4wNDItMy43MDgsNS4zODMtOC4xMzgsNS4yNDdjLTQuNDItMC4xNDEtNy45NDYtMi43MTQtNy44NzktNS43NDIJCWMwLjA2NS0zLjAzOSwzLjc5Ni01Ljk5OSw4LjIxNC01Ljg1OUM0Ni45MzgsMjIuNTQ1LDUwLjM4NiwyNS43MzMsNTAuMzEzLDI4Ljc2MnoiLz4JCQk8cmFkaWFsR3JhZGllbnQgaWQ9IlNWR0lEXzhfIiBjeD0iNDQ4Mi40MTM2IiBjeT0iLTIxNTEuMTcxNiIgcj0iMTAuNTczNSIgZ3JhZGllbnRUcmFuc2Zvcm09Im1hdHJpeCgtMC45MTIxIC0wLjM3MTIgMC4zNjIzIC0wLjkwOTkgNDk0OS41MjkzIC0yMTcuNTA5MykiIGdyYWRpZW50VW5pdHM9InVzZXJTcGFjZU9uVXNlIj4JCTxzdG9wICBvZmZzZXQ9IjAiIHN0eWxlPSJzdG9wLWNvbG9yOiM4MEUwRUYiLz4JCTxzdG9wICBvZmZzZXQ9IjAuNDk2OSIgc3R5bGU9InN0b3AtY29sb3I6IzY1QjFEOSIvPgkJPHN0b3AgIG9mZnNldD0iMC42MDY1IiBzdHlsZT0ic3RvcC1jb2xvcjojNUZBNkQzIi8+CQk8c3RvcCAgb2Zmc2V0PSIwLjgwMTIiIHN0eWxlPSJzdG9wLWNvbG9yOiM0RDg3QzIiLz4JCTxzdG9wICBvZmZzZXQ9IjEiIHN0eWxlPSJzdG9wLWNvbG9yOiMzODYyQUUiLz4JPC9yYWRpYWxHcmFkaWVudD4JPHBhdGggc3R5bGU9ImZpbGw6dXJsKCNTVkdJRF84Xyk7IiBkPSJNNzIuMTA1LDcyLjA0NGMyLjExNy01LjMxMiw4LjE0Ni03Ljg2MiwxMy40NzUtNS42OTRjNS4zMjEsMi4xNzMsNy45MzEsOC4yMzEsNS44MTUsMTMuNTQ1CQljLTIuMTEyLDUuMzA5LTguMTQ5LDcuODYzLTEzLjQ4Miw1LjY5MkM3Mi41ODksODMuNDI1LDY5Ljk4OSw3Ny4zNTMsNzIuMTA1LDcyLjA0NHoiLz4JPHBhdGggc3R5bGU9ImZpbGw6bm9uZTtzdHJva2U6IzJFMzE5MjtzdHJva2Utd2lkdGg6MC45Mjg7IiBkPSJNNzIuMTA1LDcyLjA0NGMyLjExNy01LjMxMiw4LjE0Ni03Ljg2MiwxMy40NzUtNS42OTQJCWM1LjMyMSwyLjE3Myw3LjkzMSw4LjIzMSw1LjgxNSwxMy41NDVjLTIuMTEyLDUuMzA5LTguMTQ5LDcuODYzLTEzLjQ4Miw1LjY5MkM3Mi41ODksODMuNDI1LDY5Ljk4OSw3Ny4zNTMsNzIuMTA1LDcyLjA0NHoiLz4JCQk8bGluZWFyR3JhZGllbnQgaWQ9IlNWR0lEXzlfIiBncmFkaWVudFVuaXRzPSJ1c2VyU3BhY2VPblVzZSIgeDE9Ii00NDYuMzcwNiIgeTE9Ii0xNTQ3LjI5NzkiIHgyPSItNDQ2LjM3MDYiIHkyPSItMTU1OC45MTIxIiBncmFkaWVudFRyYW5zZm9ybT0ibWF0cml4KDAuODQ2NSAtMC41MzI0IDAuNTMyNCAwLjg0NjUgMTI4NC45NTg3IDExNTAuNDkwOCkiPgkJPHN0b3AgIG9mZnNldD0iMCIgc3R5bGU9InN0b3AtY29sb3I6IzY1QjFEOSIvPgkJPHN0b3AgIG9mZnNldD0iMC4xNTk2IiBzdHlsZT0ic3RvcC1jb2xvcjojNkRCQ0RFIi8+CQk8c3RvcCAgb2Zmc2V0PSIwLjQ0MjQiIHN0eWxlPSJzdG9wLWNvbG9yOiM4MURCRUQiLz4JCTxzdG9wICBvZmZzZXQ9IjAuNjQ0MiIgc3R5bGU9InN0b3AtY29sb3I6IzkyRjRGOSIvPgk8L2xpbmVhckdyYWRpZW50Pgk8cGF0aCBzdHlsZT0iZmlsbDp1cmwoI1NWR0lEXzlfKTsiIGQ9Ik04Ny4xOTUsNjkuNDY3YzEuNjM3LDIuNTY1LTAuMDg2LDYuNTMtMy44NDksOC44N2MtMy43NTYsMi4zMjktOC4xMTksMi4xNDItOS43NS0wLjQxNQkJYy0xLjYzNy0yLjU2Mi0wLjE4LTcuMDksMy41NzEtOS40MTlDODAuOTI5LDY2LjE2Niw4NS41NzEsNjYuOTA2LDg3LjE5NSw2OS40Njd6Ii8+PC9nPjwvc3ZnPg\x3d\x3d",
        UNDO: "PHN2ZyB2ZXJzaW9uPSIxLjEiIGlkPSJMYXllcl8xIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHhtbG5zOnhsaW5rPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5L3hsaW5rIiB4PSIwcHgiIHk9IjBweCIJIHZpZXdCb3g9IjAgMCAxMDAgMTAwIiBzdHlsZT0iZW5hYmxlLWJhY2tncm91bmQ6bmV3IDAgMCAxMDAgMTAwOyIgeG1sOnNwYWNlPSJwcmVzZXJ2ZSI+PGc+CTxnPgkJCQkJPGxpbmVhckdyYWRpZW50IGlkPSJTVkdJRF8xXyIgZ3JhZGllbnRVbml0cz0idXNlclNwYWNlT25Vc2UiIHgxPSIyODQuNjE1NSIgeTE9Ii00NjguODg4OCIgeDI9IjI4NC42MTU1IiB5Mj0iLTQzNS4xNjYyIiBncmFkaWVudFRyYW5zZm9ybT0ibWF0cml4KC0wLjkyNTggLTAuNDA4NyAwLjQ0ODIgLTEuMDE1MSA1MzUuMDU3NiAtMzE3LjM3NDUpIj4JCQk8c3RvcCAgb2Zmc2V0PSIwIiBzdHlsZT0ic3RvcC1jb2xvcjojQjAyQTI1Ii8+CQkJPHN0b3AgIG9mZnNldD0iMC4xMzE2IiBzdHlsZT0ic3RvcC1jb2xvcjojQTUyNzIyIi8+CQkJPHN0b3AgIG9mZnNldD0iMC4zNjU4IiBzdHlsZT0ic3RvcC1jb2xvcjojODYyMDFDIi8+CQkJPHN0b3AgIG9mZnNldD0iMC42NzUzIiBzdHlsZT0ic3RvcC1jb2xvcjojNTUxNDExIi8+CQkJPHN0b3AgIG9mZnNldD0iMSIgc3R5bGU9InN0b3AtY29sb3I6IzFBMDUwNCIvPgkJPC9saW5lYXJHcmFkaWVudD4JCTxwYXRoIHN0eWxlPSJmaWxsOnVybCgjU1ZHSURfMV8pO3N0cm9rZTojN0ExOTFEO3N0cm9rZS13aWR0aDoyLjQ5NDQ7IiBkPSJNMzQuMDI4LDEwLjA4NQkJCWM0NC45NzEtMjIuMzkyLDYxLjg2MiwyMC4yMzYsNjEuODYyLDIwLjIzNnM1Ljk5NiwxNi4yMzEsMC40ODQsMjYuODU0Yy0yLjExLDQuMDc0LTIuNTAxLTI4LjEzMS0yNS42NjYtMzAuMTY0CQkJQzQ3LjMwMywyNC45NiwzNC4wMjgsMTAuMDg1LDM0LjAyOCwxMC4wODV6Ii8+CQk8bGluZWFyR3JhZGllbnQgaWQ9IlNWR0lEXzJfIiBncmFkaWVudFVuaXRzPSJ1c2VyU3BhY2VPblVzZSIgeDE9IjEuMTUxIiB5MT0iNDkuOTUzNyIgeDI9Ijk1Ljg5MDYiIHkyPSI0OS45NTM3Ij4JCQk8c3RvcCAgb2Zmc2V0PSIwIiBzdHlsZT0ic3RvcC1jb2xvcjojQkYyNDFCIi8+CQkJPHN0b3AgIG9mZnNldD0iMC4yNyIgc3R5bGU9InN0b3AtY29sb3I6I0FCMjIxQiIvPgkJCTxzdG9wICBvZmZzZXQ9IjAuNzM2NiIgc3R5bGU9InN0b3AtY29sb3I6IzhDMjAxQiIvPgkJCTxzdG9wICBvZmZzZXQ9IjEiIHN0eWxlPSJzdG9wLWNvbG9yOiM4MTFGMUIiLz4JCTwvbGluZWFyR3JhZGllbnQ+CQk8cGF0aCBzdHlsZT0iZmlsbDp1cmwoI1NWR0lEXzJfKTtzdHJva2U6IzdBMTkxRDtzdHJva2Utd2lkdGg6Mi40OTQ0OyIgZD0iTTg4LjI1MywxNy45MzhDODIuOTA3LDExLjUsNzQuNTA1LDQuNTczLDYzLjk5NCwyLjEzMwkJCWMtOC4yMzQtMS45MS0xOC4wMy0xLTI5LjMzNyw1LjI0NUMyMi44ODYsMTMuODczLDE5LjczMSwyNi4xMywxNy4wNTYsMzIuNTIzbC03LjIwNC0zLjE3NWMtNS40MjctMi4zODgtOS4zMTksMC4zNjMtOC42MTksNi4xMjQJCQlsNi44NjgsNTcuMjQ1YzAuNjgsNS43NjEsNS4xODYsNy42NzEsOS45OTYsNC4yNDRsNDYuNzYzLTMzLjMyYzQuODEyLTMuNDIsNC4yOTYtOC4xOC0xLjEzLTEwLjU3bC03Ljk0Ny0zLjUJCQljMS40OC00LjUwMSw2LjYzNC0xMy44ODksMTQuNTA1LTIwLjAyNmMxOC45Ni0xNC44MjksMjUuNjA0LDAuNzc3LDI1LjYwNCwwLjc3N1M5My41OTEsMjQuMzc1LDg4LjI1MywxNy45Mzh6Ii8+CTwvZz4JPHBhdGggc3R5bGU9ImZpbGw6I0UyNTk0MzsiIGQ9Ik0xNS42MTEsMzkuMzA4Yy00LjU5OC0yLjQ0NC04LjE5Mi00LjcxOC03LjYwMy0xLjMxMmMwLjk4Niw1LjkwOSw0LjMyOCw1NS45OTksNC4zMjgsNTUuOTk5CQlzMCwxLjk2Ni0wLjk4NS0zLjQ0NmMtMC45OTMtNS40MjEtNS45NDktNTIuNjc0LTUuOTQ5LTU0LjE1MmMwLTEuNDc4LTAuOTk1LTMuNDQ1LDAuNDk4LTMuOTM0CQljMS40NjgtMC40OTcsMTEuODk2LDQuOTIxLDExLjg5Niw0LjkyMXM1Ljk5NC0xOS45MzksMTUuNzE1LTI2LjkxMmM5Ljk5My03LjE3NiwyMC43MjctOC40MDYsMjkuMzUzLTYuNjQzCQljMTEuNDYyLDIuMzQ0LDE5LjMxNyw5Ljc5MywxOS4zMTcsOS43OTNzLTguNTA1LTUuODkyLTE5LjQ3OC03LjgyNkM1Mi41Miw0LjAwMiwzOC40MzUsNi43MDIsMzEuNTIyLDE2LjA3OQkJYy03LjU5OCwxMC4zMDktOC43NTgsMTkuMTctMTEuNTY3LDIzLjQ0QzE4LjYxMiw0MS41NTEsMTguMTgyLDQwLjY4MSwxNS42MTEsMzkuMzA4eiIvPjwvZz48L3N2Zz4\x3d",
        VARIABLE_ATTACHMENT_POINTS: "PHN2ZyBmaWxsLW9wYWNpdHk9IjEiIHhtbG5zOnhsaW5rPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5L3hsaW5rIiBjb2xvci1yZW5kZXJpbmc9ImF1dG8iIGNvbG9yLWludGVycG9sYXRpb249ImF1dG8iIHRleHQtcmVuZGVyaW5nPSJhdXRvIiBzdHJva2U9ImJsYWNrIiBzdHJva2UtbGluZWNhcD0ic3F1YXJlIiB3aWR0aD0iMjAiIHN0cm9rZS1taXRlcmxpbWl0PSIxMCIgc2hhcGUtcmVuZGVyaW5nPSJhdXRvIiBzdHJva2Utb3BhY2l0eT0iMSIgZmlsbD0iYmxhY2siIHN0cm9rZS1kYXNoYXJyYXk9Im5vbmUiIGZvbnQtd2VpZ2h0PSJub3JtYWwiIHN0cm9rZS13aWR0aD0iMSIgdmlld0JveD0iMCAwIDIwLjAgMjAuMCIgaGVpZ2h0PSIyMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIiBmb250LWZhbWlseT0iJmFwb3M7RGlhbG9nJmFwb3M7IiBmb250LXN0eWxlPSJub3JtYWwiIHN0cm9rZS1saW5lam9pbj0ibWl0ZXIiIGZvbnQtc2l6ZT0iMTIiIHN0cm9rZS1kYXNob2Zmc2V0PSIwIiBpbWFnZS1yZW5kZXJpbmc9ImF1dG8iPjxkZWZzIGlkPSJnZW5lcmljRGVmcyIgIC8+PGcgID48ZyB0ZXh0LXJlbmRlcmluZz0iZ2VvbWV0cmljUHJlY2lzaW9uIiBjb2xvci1yZW5kZXJpbmc9Im9wdGltaXplUXVhbGl0eSIgY29sb3ItaW50ZXJwb2xhdGlvbj0ibGluZWFyUkdCIiBpbWFnZS1yZW5kZXJpbmc9Im9wdGltaXplU3BlZWQiICAgID48cGF0aCBmaWxsPSJub25lIiBkPSJNNyA2IEwxMyAxMCBMMTMgMTYgTDcgMjAgTDEgMTYgTDEgMTAgWiIgICAgICAvPjxjaXJjbGUgZmlsbD0ibm9uZSIgcj0iMyIgY3g9IjciIGN5PSIxMyIgICAgICAvPjxsaW5lIHkyPSI3IiBmaWxsPSJub25lIiB4MT0iNyIgeDI9IjEzIiB5MT0iMTMiICAgICAgLz48cGF0aCBkPSJNMTQuMjE1MyA2IEwxNi4yOTgzIDIuNzk2NCBMMTQuMzA3NiAtMC41MDM5IEwxNS44ODUzIC0wLjUwMzkgTDE3LjIwOCAxLjY4NDYgTDE4LjY0MDYgLTAuNTAzOSBMMTkuNzM0OSAtMC41MDM5IEwxNy43Mzk3IDIuNTYzNSBMMTkuODA1MiA2IEwxOC4yMzE5IDYgTDE2LjgyMTMgMy42NzUzIEwxNS4zMDk2IDYgWiIgc3Ryb2tlPSJub25lIiAgICAvPjwvZyAgPjwvZz48L3N2Zz4\x3d",
        ZOOM_IN: "PHN2ZyB2ZXJzaW9uPSIxLjEiIGlkPSJMYXllcl8xIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHhtbG5zOnhsaW5rPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5L3hsaW5rIiB4PSIwcHgiIHk9IjBweCIJIHZpZXdCb3g9IjAgMCAyMCAyMCIgc3R5bGU9ImVuYWJsZS1iYWNrZ3JvdW5kOm5ldyAwIDAgMjAgMjA7IiB4bWw6c3BhY2U9InByZXNlcnZlIj48Zz4JPGc+CQk8Zz4JCQk8Zz4JCQkJPGc+CQkJCQkJCQkJCQk8bGluZWFyR3JhZGllbnQgaWQ9IlNWR0lEXzFfIiBncmFkaWVudFVuaXRzPSJ1c2VyU3BhY2VPblVzZSIgeDE9IjM0OS4wOTE0IiB5MT0iLTE0OS4xNzQiIHgyPSIzNTEuNzk4IiB5Mj0iLTE0OS4xNzQiIGdyYWRpZW50VHJhbnNmb3JtPSJtYXRyaXgoLTAuNjgyNiAwLjczMDggMC43MzA4IDAuNjgyNiAzNTkuOTUyMSAtMTQyLjEzNDMpIj4JCQkJCQk8c3RvcCAgb2Zmc2V0PSIwLjA5MzQiIHN0eWxlPSJzdG9wLWNvbG9yOiNDNUMyQzIiLz4JCQkJCQk8c3RvcCAgb2Zmc2V0PSIwLjE3MTciIHN0eWxlPSJzdG9wLWNvbG9yOiNDRkNDQ0MiLz4JCQkJCQk8c3RvcCAgb2Zmc2V0PSIwLjMwNjEiIHN0eWxlPSJzdG9wLWNvbG9yOiNFOUU4RTgiLz4JCQkJCQk8c3RvcCAgb2Zmc2V0PSIwLjM5ODgiIHN0eWxlPSJzdG9wLWNvbG9yOiNGRkZGRkYiLz4JCQkJCQk8c3RvcCAgb2Zmc2V0PSIwLjUyOTUiIHN0eWxlPSJzdG9wLWNvbG9yOiNCN0I3QjciLz4JCQkJCQk8c3RvcCAgb2Zmc2V0PSIwLjY0NDQiIHN0eWxlPSJzdG9wLWNvbG9yOiM3RDdEN0QiLz4JCQkJCQk8c3RvcCAgb2Zmc2V0PSIwLjY5OTQiIHN0eWxlPSJzdG9wLWNvbG9yOiM2NzY3NjciLz4JCQkJCTwvbGluZWFyR3JhZGllbnQ+CQkJCQk8cG9seWdvbiBzdHlsZT0iZmlsbDp1cmwoI1NWR0lEXzFfKTtzdHJva2U6IzhEOEQ4RDtzdHJva2Utd2lkdGg6MC40MDAxOyIgcG9pbnRzPSIxMy4xNjksMTUuMzM2IDE1LjAxMywxMy4zNjYgMTAuMjc2LDguOTUzIAkJCQkJCTguNDMyLDEwLjkyMyAJCQkJCSIvPgkJCQkJCQkJCQkJPGxpbmVhckdyYWRpZW50IGlkPSJTVkdJRF8yXyIgZ3JhZGllbnRVbml0cz0idXNlclNwYWNlT25Vc2UiIHgxPSIzNDguNTQzOCIgeTE9Ii0xNDIuNzAwNiIgeDI9IjM1Mi4zMzA0IiB5Mj0iLTE0Mi43MDA2IiBncmFkaWVudFRyYW5zZm9ybT0ibWF0cml4KC0wLjY4MjYgMC43MzA4IDAuNzMwOCAwLjY4MjYgMzU5Ljk1MjEgLTE0Mi4xMzQzKSI+CQkJCQkJPHN0b3AgIG9mZnNldD0iMCIgc3R5bGU9InN0b3AtY29sb3I6IzM2QkQwMCIvPgkJCQkJCTxzdG9wICBvZmZzZXQ9IjAuMDU2NyIgc3R5bGU9InN0b3AtY29sb3I6IzJCQkMxOCIvPgkJCQkJCTxzdG9wICBvZmZzZXQ9IjAuMTgyMSIgc3R5bGU9InN0b3AtY29sb3I6IzE0QkI0OSIvPgkJCQkJCTxzdG9wICBvZmZzZXQ9IjAuMjc3NiIgc3R5bGU9InN0b3AtY29sb3I6IzA1QkE2OCIvPgkJCQkJCTxzdG9wICBvZmZzZXQ9IjAuMzMxMyIgc3R5bGU9InN0b3AtY29sb3I6IzAwQkE3MyIvPgkJCQkJCTxzdG9wICBvZmZzZXQ9IjAuMzkwOCIgc3R5bGU9InN0b3AtY29sb3I6IzAxQUY2MCIvPgkJCQkJCTxzdG9wICBvZmZzZXQ9IjAuNTEwOCIgc3R5bGU9InN0b3AtY29sb3I6IzAyOTQyRiIvPgkJCQkJCTxzdG9wICBvZmZzZXQ9IjAuNjEzNSIgc3R5bGU9InN0b3AtY29sb3I6IzA0N0EwMCIvPgkJCQkJCTxzdG9wICBvZmZzZXQ9IjAuNzI1NiIgc3R5bGU9InN0b3AtY29sb3I6IzA0NzgwMyIvPgkJCQkJCTxzdG9wICBvZmZzZXQ9IjAuODE1NiIgc3R5bGU9InN0b3AtY29sb3I6IzAzNzEwRCIvPgkJCQkJCTxzdG9wICBvZmZzZXQ9IjAuODk3OSIgc3R5bGU9InN0b3AtY29sb3I6IzAyNjUxRSIvPgkJCQkJCTxzdG9wICBvZmZzZXQ9IjAuOTc1MiIgc3R5bGU9InN0b3AtY29sb3I6IzAxNTUzNiIvPgkJCQkJCTxzdG9wICBvZmZzZXQ9IjEiIHN0eWxlPSJzdG9wLWNvbG9yOiMwMDRGM0YiLz4JCQkJCTwvbGluZWFyR3JhZGllbnQ+CQkJCQk8cGF0aCBzdHlsZT0iZmlsbDp1cmwoI1NWR0lEXzJfKTsiIGQ9Ik0xNS4wODYsMTIuNjk3bDQuNTQyLDQuMjI5YzAuNDM2LDAuNDA2LDAuNDU5LDEuMDg5LDAuMDUxLDEuNTI0bC0xLjEwNiwxLjE4MgkJCQkJCWMtMC40MDUsMC40MzQtMS4wOTIsMC40NTctMS41MjUsMC4wNTNsLTQuNTQyLTQuMjNMMTUuMDg2LDEyLjY5N3oiLz4JCQkJPC9nPgkJCQk8Zz4JCQkJCQkJCQkJCTxsaW5lYXJHcmFkaWVudCBpZD0iU1ZHSURfM18iIGdyYWRpZW50VW5pdHM9InVzZXJTcGFjZU9uVXNlIiB4MT0iNDI3LjI0MDUiIHkxPSItNDUuMTE5MiIgeDI9IjQ0MC45Mzg4IiB5Mj0iLTQ1LjExOTIiIGdyYWRpZW50VHJhbnNmb3JtPSJtYXRyaXgoLTAuOTcyOCAwLjIzMTQgMC4yMzE0IDAuOTcyOCA0MzkuODA3OCAtNDkuNTA5OSkiPgkJCQkJCTxzdG9wICBvZmZzZXQ9IjAuMDExIiBzdHlsZT0ic3RvcC1jb2xvcjojNjM2MzYzIi8+CQkJCQkJPHN0b3AgIG9mZnNldD0iMC4wNDY0IiBzdHlsZT0ic3RvcC1jb2xvcjojNTc1NzU3Ii8+CQkJCQkJPHN0b3AgIG9mZnNldD0iMC4xNDI0IiBzdHlsZT0ic3RvcC1jb2xvcjojM0IzQjNCIi8+CQkJCQkJPHN0b3AgIG9mZnNldD0iMC4yMjYyIiBzdHlsZT0ic3RvcC1jb2xvcjojMkEyQTJBIi8+CQkJCQkJPHN0b3AgIG9mZnNldD0iMC4yODgzIiBzdHlsZT0ic3RvcC1jb2xvcjojMjQyNDI0Ii8+CQkJCQkJPHN0b3AgIG9mZnNldD0iMC40ODc2IiBzdHlsZT0ic3RvcC1jb2xvcjojNjk2OTY5Ii8+CQkJCQkJPHN0b3AgIG9mZnNldD0iMC42NTAzIiBzdHlsZT0ic3RvcC1jb2xvcjojOUU5RTlFIi8+CQkJCQkJPHN0b3AgIG9mZnNldD0iMSIgc3R5bGU9InN0b3AtY29sb3I6IzM2MzYzNiIvPgkJCQkJPC9saW5lYXJHcmFkaWVudD4JCQkJCTxwYXRoIHN0eWxlPSJmaWxsOnVybCgjU1ZHSURfM18pO3N0cm9rZTojOEQ4RDhEO3N0cm9rZS13aWR0aDowLjQwMDE7IiBkPSJNMC40LDguNTM2YzAuODI2LDMuNjg0LDQuNDg4LDYuMDAxLDguMTgsNS4xNzgJCQkJCQljMy42OTEtMC44MjYsNi4wMTQtNC40NzcsNS4xODktOC4xNjJjLTAuODI1LTMuNjc4LTQuNDg3LTUuOTk1LTguMTgtNS4xNzNDMS44OTYsMS4yMDUtMC40MjYsNC44NTUsMC40LDguNTM2eiIvPgkJCQkJCQkJCQkJPGxpbmVhckdyYWRpZW50IGlkPSJTVkdJRF80XyIgZ3JhZGllbnRVbml0cz0idXNlclNwYWNlT25Vc2UiIHgxPSI0MzQuMDg3NyIgeTE9Ii01MC40OTQxIiB4Mj0iNDM0LjA4NzciIHkyPSItMzkuNzQ3MSIgZ3JhZGllbnRUcmFuc2Zvcm09Im1hdHJpeCgtMC45NzI4IDAuMjMxNCAwLjIzMTQgMC45NzI4IDQzOS44MDc4IC00OS41MDk5KSI+CQkJCQkJPHN0b3AgIG9mZnNldD0iMCIgc3R5bGU9InN0b3AtY29sb3I6I0RCRUJGNCIvPgkJCQkJCTxzdG9wICBvZmZzZXQ9IjAuMTE3NiIgc3R5bGU9InN0b3AtY29sb3I6I0QyRTdGMyIvPgkJCQkJCTxzdG9wICBvZmZzZXQ9IjAuMzA1OSIgc3R5bGU9InN0b3AtY29sb3I6I0JCREFFRiIvPgkJCQkJCTxzdG9wICBvZmZzZXQ9IjAuNTQxMyIgc3R5bGU9InN0b3AtY29sb3I6Izk1QzZFOSIvPgkJCQkJCTxzdG9wICBvZmZzZXQ9IjAuODEyIiBzdHlsZT0ic3RvcC1jb2xvcjojNjFBQkUxIi8+CQkJCQkJPHN0b3AgIG9mZnNldD0iMSIgc3R5bGU9InN0b3AtY29sb3I6IzM4OTZEQiIvPgkJCQkJPC9saW5lYXJHcmFkaWVudD4JCQkJCTxwYXRoIHN0eWxlPSJmaWxsOnVybCgjU1ZHSURfNF8pOyIgZD0iTTEuODI5LDguMjE4YzAuNjQ3LDIuODk1LDMuNTI3LDQuNzE3LDYuNDMxLDQuMDdjMi45MDQtMC42NDYsNC43MzEtMy41MTksNC4wODQtNi40MTYJCQkJCQljLTAuNjUxLTIuODk0LTMuNTMyLTQuNzE1LTYuNDM1LTQuMDY5QzMuMDAzLDIuNDUxLDEuMTc4LDUuMzIzLDEuODI5LDguMjE4eiIvPgkJCQkJCQkJCQkJPGxpbmVhckdyYWRpZW50IGlkPSJTVkdJRF81XyIgZ3JhZGllbnRVbml0cz0idXNlclNwYWNlT25Vc2UiIHgxPSI0MzQuMDg3NSIgeTE9Ii01MC40OTQxIiB4Mj0iNDM0LjA4NzUiIHkyPSItNDQuNzU2MyIgZ3JhZGllbnRUcmFuc2Zvcm09Im1hdHJpeCgtMC45NzI4IDAuMjMxNCAwLjIzMTQgMC45NzI4IDQzOS44MDc4IC00OS41MDk5KSI+CQkJCQkJPHN0b3AgIG9mZnNldD0iMCIgc3R5bGU9InN0b3AtY29sb3I6I0YzRkFGRiIvPgkJCQkJCTxzdG9wICBvZmZzZXQ9IjEiIHN0eWxlPSJzdG9wLWNvbG9yOiNBRkQzRjIiLz4JCQkJCTwvbGluZWFyR3JhZGllbnQ+CQkJCQk8cGF0aCBzdHlsZT0iZmlsbDp1cmwoI1NWR0lEXzVfKTsiIGQ9Ik0xLjgyOSw4LjIxOGMtMC42NTEtMi44OTUsMS4xNzQtNS43NjgsNC4wOC02LjQxNmMyLjkwMy0wLjY0Niw1Ljc4NCwxLjE3NSw2LjQzNSw0LjA2OQkJCQkJCWMwLDAtMS4xLDAuOTMyLTMuMDE1LDAuNzEzQzcuNDE1LDYuMzY3LDUuODc1LDUuNzEsNC4xOTEsNi40MThTMS44MjksOC4yMTgsMS44MjksOC4yMTh6Ii8+CQkJCQk8cGF0aCBzdHlsZT0iZmlsbDpub25lOyIgZD0iTTEuODI5LDguMjE4YzAuNjQ3LDIuODk1LDMuNTI3LDQuNzE3LDYuNDMxLDQuMDdjMi45MDQtMC42NDYsNC43MzEtMy41MTksNC4wODQtNi40MTYJCQkJCQljLTAuNjUxLTIuODk0LTMuNTMyLTQuNzE1LTYuNDM1LTQuMDY5QzMuMDAzLDIuNDUxLDEuMTc4LDUuMzIzLDEuODI5LDguMjE4eiIvPgkJCQk8L2c+CQkJPC9nPgkJPC9nPgkJPGc+CQkJPHJlY3QgeD0iNS44MzMiIHk9IjMuMDU4IiB3aWR0aD0iMi4yODUiIGhlaWdodD0iNy45NzkiLz4JCQk8cmVjdCB4PSIyLjk3MyIgeT0iNS45MDkiIHdpZHRoPSI4LjAwNCIgaGVpZ2h0PSIyLjI4Ii8+CQk8L2c+CTwvZz4JCQk8bGluZSBzdHlsZT0iZmlsbDpub25lO3N0cm9rZTojQ0ZGRkQ3O3N0cm9rZS13aWR0aDowLjYwMDE7c3Ryb2tlLWxpbmVjYXA6cm91bmQ7c3Ryb2tlLWxpbmVqb2luOnJvdW5kOyIgeDE9IjE5LjE0NSIgeTE9IjE3LjU3NyIgeDI9IjE0LjkzOSIgeTI9IjEzLjczMSIvPgkJCTxsaW5lIHN0eWxlPSJmaWxsOm5vbmU7c3Ryb2tlOiNGRkZGRkY7c3Ryb2tlLXdpZHRoOjAuNjAwMTtzdHJva2UtbGluZWNhcDpyb3VuZDtzdHJva2UtbGluZWpvaW46cm91bmQ7IiB4MT0iMTMuODE0IiB5MT0iMTMuNDU4IiB4Mj0iMTIuNDMzIiB5Mj0iMTIuMTkyIi8+PC9nPjwvc3ZnPg\x3d\x3d",
        ZOOM_OUT: "PHN2ZyB2ZXJzaW9uPSIxLjEiIGlkPSJMYXllcl8xIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHhtbG5zOnhsaW5rPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5L3hsaW5rIiB4PSIwcHgiIHk9IjBweCIJIHZpZXdCb3g9IjAgMCAxMDAgMTAwIiBzdHlsZT0iZW5hYmxlLWJhY2tncm91bmQ6bmV3IDAgMCAxMDAgMTAwOyIgeG1sOnNwYWNlPSJwcmVzZXJ2ZSI+PGc+CTxnPgkJPGc+CQkJPGc+CQkJCTxnPgkJCQkJCQkJCQkJPGxpbmVhckdyYWRpZW50IGlkPSJTVkdJRF8xXyIgZ3JhZGllbnRVbml0cz0idXNlclNwYWNlT25Vc2UiIHgxPSIzODUuMjIxNiIgeTE9Ii05OC4zNjk1IiB4Mj0iMzk4Ljc4NDgiIHkyPSItOTguMzY5NSIgZ3JhZGllbnRUcmFuc2Zvcm09Im1hdHJpeCgtMC42ODI2IDAuNzMwOCAwLjczMDggMC42ODI2IDM5OC4wMjQxIC0xNTguNjcwMykiPgkJCQkJCTxzdG9wICBvZmZzZXQ9IjAuMDkzNCIgc3R5bGU9InN0b3AtY29sb3I6I0M1QzJDMiIvPgkJCQkJCTxzdG9wICBvZmZzZXQ9IjAuMTcxNyIgc3R5bGU9InN0b3AtY29sb3I6I0NGQ0NDQyIvPgkJCQkJCTxzdG9wICBvZmZzZXQ9IjAuMzA2MSIgc3R5bGU9InN0b3AtY29sb3I6I0U5RThFOCIvPgkJCQkJCTxzdG9wICBvZmZzZXQ9IjAuMzk4OCIgc3R5bGU9InN0b3AtY29sb3I6I0ZGRkZGRiIvPgkJCQkJCTxzdG9wICBvZmZzZXQ9IjAuNTI5NSIgc3R5bGU9InN0b3AtY29sb3I6I0I3QjdCNyIvPgkJCQkJCTxzdG9wICBvZmZzZXQ9IjAuNjQ0NCIgc3R5bGU9InN0b3AtY29sb3I6IzdEN0Q3RCIvPgkJCQkJCTxzdG9wICBvZmZzZXQ9IjAuNjk5NCIgc3R5bGU9InN0b3AtY29sb3I6IzY3Njc2NyIvPgkJCQkJPC9saW5lYXJHcmFkaWVudD4JCQkJCTxwb2x5Z29uIHN0eWxlPSJmaWxsOnVybCgjU1ZHSURfMV8pO3N0cm9rZTojNUE1QTVBO3N0cm9rZS13aWR0aDoyLjAwMDU7IiBwb2ludHM9IjY1Ljc5NCw3Ni42MDQgNzUuMDI4LDY2Ljc2NSA1MS4zMTUsNDQuNzE0IAkJCQkJCTQyLjA4NCw1NC41NTMgCQkJCQkiLz4JCQkJCQkJCQkJCTxsaW5lYXJHcmFkaWVudCBpZD0iU1ZHSURfMl8iIGdyYWRpZW50VW5pdHM9InVzZXJTcGFjZU9uVXNlIiB4MT0iMzgyLjQ1NzUiIHkxPSItNjUuOTk4MiIgeDI9IjQwMS40MTY1IiB5Mj0iLTY1Ljk5ODIiIGdyYWRpZW50VHJhbnNmb3JtPSJtYXRyaXgoLTAuNjgyNiAwLjczMDggMC43MzA4IDAuNjgyNiAzOTguMDI0MSAtMTU4LjY3MDMpIj4JCQkJCQk8c3RvcCAgb2Zmc2V0PSIwIiBzdHlsZT0ic3RvcC1jb2xvcjojMzZCRDAwIi8+CQkJCQkJPHN0b3AgIG9mZnNldD0iMC4wNTY3IiBzdHlsZT0ic3RvcC1jb2xvcjojMkJCQzE4Ii8+CQkJCQkJPHN0b3AgIG9mZnNldD0iMC4xODIxIiBzdHlsZT0ic3RvcC1jb2xvcjojMTRCQjQ5Ii8+CQkJCQkJPHN0b3AgIG9mZnNldD0iMC4yNzc2IiBzdHlsZT0ic3RvcC1jb2xvcjojMDVCQTY4Ii8+CQkJCQkJPHN0b3AgIG9mZnNldD0iMC4zMzEzIiBzdHlsZT0ic3RvcC1jb2xvcjojMDBCQTczIi8+CQkJCQkJPHN0b3AgIG9mZnNldD0iMC4zOTA4IiBzdHlsZT0ic3RvcC1jb2xvcjojMDFBRjYwIi8+CQkJCQkJPHN0b3AgIG9mZnNldD0iMC41MTA4IiBzdHlsZT0ic3RvcC1jb2xvcjojMDI5NDJGIi8+CQkJCQkJPHN0b3AgIG9mZnNldD0iMC42MTM1IiBzdHlsZT0ic3RvcC1jb2xvcjojMDQ3QTAwIi8+CQkJCQkJPHN0b3AgIG9mZnNldD0iMC43MjU2IiBzdHlsZT0ic3RvcC1jb2xvcjojMDQ3ODAzIi8+CQkJCQkJPHN0b3AgIG9mZnNldD0iMC44MTU2IiBzdHlsZT0ic3RvcC1jb2xvcjojMDM3MTBEIi8+CQkJCQkJPHN0b3AgIG9mZnNldD0iMC44OTc5IiBzdHlsZT0ic3RvcC1jb2xvcjojMDI2NTFFIi8+CQkJCQkJPHN0b3AgIG9mZnNldD0iMC45NzUyIiBzdHlsZT0ic3RvcC1jb2xvcjojMDE1NTM2Ii8+CQkJCQkJPHN0b3AgIG9mZnNldD0iMSIgc3R5bGU9InN0b3AtY29sb3I6IzAwNEYzRiIvPgkJCQkJPC9saW5lYXJHcmFkaWVudD4JCQkJCTxwYXRoIHN0eWxlPSJmaWxsOnVybCgjU1ZHSURfMl8pOyIgZD0iTTc1LjM4Myw2My40MTRMOTguMTE5LDg0LjU1YzIuMTgyLDIuMDM1LDIuMyw1LjQ0LDAuMjU4LDcuNjE0bC01LjU0LDUuODk5CQkJCQkJYy0yLjAzNCwyLjE3NC01LjQ2LDIuMjg4LTcuNjM3LDAuMjYyTDYyLjQ2Miw3Ny4xODhMNzUuMzgzLDYzLjQxNHoiLz4JCQkJPC9nPgkJCQk8Zz4JCQkJCQkJCQkJCTxsaW5lYXJHcmFkaWVudCBpZD0iU1ZHSURfM18iIGdyYWRpZW50VW5pdHM9InVzZXJTcGFjZU9uVXNlIiB4MT0iNDQ4LjQ5MTUiIHkxPSItMTkuMzc2MyIgeDI9IjUxNy4wNDg0IiB5Mj0iLTE5LjM3NjIiIGdyYWRpZW50VHJhbnNmb3JtPSJtYXRyaXgoLTAuOTcyOCAwLjIzMTQgMC4yMzE0IDAuOTcyOCA1MDkuNDYzOCAtNTcuNjc3OSkiPgkJCQkJCTxzdG9wICBvZmZzZXQ9IjAuMDExIiBzdHlsZT0ic3RvcC1jb2xvcjojNjM2MzYzIi8+CQkJCQkJPHN0b3AgIG9mZnNldD0iMC4wNDY0IiBzdHlsZT0ic3RvcC1jb2xvcjojNTc1NzU3Ii8+CQkJCQkJPHN0b3AgIG9mZnNldD0iMC4xNDI0IiBzdHlsZT0ic3RvcC1jb2xvcjojM0IzQjNCIi8+CQkJCQkJPHN0b3AgIG9mZnNldD0iMC4yMjYyIiBzdHlsZT0ic3RvcC1jb2xvcjojMkEyQTJBIi8+CQkJCQkJPHN0b3AgIG9mZnNldD0iMC4yODgzIiBzdHlsZT0ic3RvcC1jb2xvcjojMjQyNDI0Ii8+CQkJCQkJPHN0b3AgIG9mZnNldD0iMC40ODc2IiBzdHlsZT0ic3RvcC1jb2xvcjojNjk2OTY5Ii8+CQkJCQkJPHN0b3AgIG9mZnNldD0iMC42NTAzIiBzdHlsZT0ic3RvcC1jb2xvcjojOUU5RTlFIi8+CQkJCQkJPHN0b3AgIG9mZnNldD0iMSIgc3R5bGU9InN0b3AtY29sb3I6IzM2MzYzNiIvPgkJCQkJPC9saW5lYXJHcmFkaWVudD4JCQkJCTxwYXRoIHN0eWxlPSJmaWxsOnVybCgjU1ZHSURfM18pO3N0cm9rZTojNTg1ODU4O3N0cm9rZS13aWR0aDoyLjAwMDU7IiBkPSJNMS44ODMsNDIuNjM3CQkJCQkJQzYuMDIsNjEuMDMzLDI0LjM0Niw3Mi42MDQsNDIuODI1LDY4LjQ5MWMxOC40ODEtNC4xMTksMzAuMS0yMi4zNjQsMjUuOTcyLTQwLjc2MkM2NC42NjUsOS4zNDUsNDYuMzM0LTIuMjI5LDI3Ljg1LDEuODgJCQkJCQlDOS4zNzYsNS45OTQtMi4yNSwyNC4yMzksMS44ODMsNDIuNjM3eiIvPgkJCQkJCQkJCQkJPGxpbmVhckdyYWRpZW50IGlkPSJTVkdJRF80XyIgZ3JhZGllbnRVbml0cz0idXNlclNwYWNlT25Vc2UiIHgxPSI0ODIuNzU5MiIgeTE9Ii00Ni4yMzAzIiB4Mj0iNDgyLjc1OTIiIHkyPSI3LjQ3MSIgZ3JhZGllbnRUcmFuc2Zvcm09Im1hdHJpeCgtMC45NzI4IDAuMjMxNCAwLjIzMTQgMC45NzI4IDUwOS40NjM4IC01Ny42Nzc5KSI+CQkJCQkJPHN0b3AgIG9mZnNldD0iMCIgc3R5bGU9InN0b3AtY29sb3I6I0RCRUJGNCIvPgkJCQkJCTxzdG9wICBvZmZzZXQ9IjAuMTE3NiIgc3R5bGU9InN0b3AtY29sb3I6I0QyRTdGMyIvPgkJCQkJCTxzdG9wICBvZmZzZXQ9IjAuMzA1OSIgc3R5bGU9InN0b3AtY29sb3I6I0JCREFFRiIvPgkJCQkJCTxzdG9wICBvZmZzZXQ9IjAuNTQxMyIgc3R5bGU9InN0b3AtY29sb3I6Izk1QzZFOSIvPgkJCQkJCTxzdG9wICBvZmZzZXQ9IjAuODEyIiBzdHlsZT0ic3RvcC1jb2xvcjojNjFBQkUxIi8+CQkJCQkJPHN0b3AgIG9mZnNldD0iMSIgc3R5bGU9InN0b3AtY29sb3I6IzM4OTZEQiIvPgkJCQkJPC9saW5lYXJHcmFkaWVudD4JCQkJCTxwYXRoIHN0eWxlPSJmaWxsOnVybCgjU1ZHSURfNF8pOyIgZD0iTTkuMDM5LDQxLjA0MmMzLjIzOCwxNC40NzIsMTcuNjU0LDIzLjU3MiwzMi4xODQsMjAuMzM2CQkJCQkJYzE0LjU0LTMuMjQyLDIzLjY3NC0xNy41ODMsMjAuNDQyLTMyLjA2M0M1OC40MDEsMTQuODU4LDQzLjk4NCw1Ljc1OCwyOS40NTYsOC45ODdDMTQuOTE2LDEyLjIyOSw1Ljc3OCwyNi41NzgsOS4wMzksNDEuMDQyeiIJCQkJCQkvPgkJCQkJCQkJCQkJPGxpbmVhckdyYWRpZW50IGlkPSJTVkdJRF81XyIgZ3JhZGllbnRVbml0cz0idXNlclNwYWNlT25Vc2UiIHgxPSI0ODIuNzU4IiB5MT0iLTQ2LjIzMDMiIHgyPSI0ODIuNzU4IiB5Mj0iLTE3LjU1MzciIGdyYWRpZW50VHJhbnNmb3JtPSJtYXRyaXgoLTAuOTcyOCAwLjIzMTQgMC4yMzE0IDAuOTcyOCA1MDkuNDYzOCAtNTcuNjc3OSkiPgkJCQkJCTxzdG9wICBvZmZzZXQ9IjAiIHN0eWxlPSJzdG9wLWNvbG9yOiNGM0ZBRkYiLz4JCQkJCQk8c3RvcCAgb2Zmc2V0PSIxIiBzdHlsZT0ic3RvcC1jb2xvcjojQUZEM0YyIi8+CQkJCQk8L2xpbmVhckdyYWRpZW50PgkJCQkJPHBhdGggc3R5bGU9ImZpbGw6dXJsKCNTVkdJRF81Xyk7IiBkPSJNOS4wMzksNDEuMDQyQzUuNzc4LDI2LjU3OCwxNC45MTYsMTIuMjI5LDI5LjQ1Niw4Ljk4NwkJCQkJCWMxNC41MjgtMy4yMjksMjguOTQ1LDUuODcxLDMyLjIwOCwyMC4zMjljMCwwLTUuNDk5LDQuNjU4LTE1LjA4OCwzLjU2NWMtOS41ODQtMS4wODctMTcuMjg4LTQuMzc2LTI1LjcxOS0wLjgzNgkJCQkJCUMxMi40MywzNS41ODMsOS4wMzksNDEuMDQyLDkuMDM5LDQxLjA0MnoiLz4JCQkJCTxwYXRoIHN0eWxlPSJmaWxsOm5vbmU7IiBkPSJNOS4wMzksNDEuMDQyYzMuMjM4LDE0LjQ3MiwxNy42NTQsMjMuNTcyLDMyLjE4NCwyMC4zMzZjMTQuNTQtMy4yNDIsMjMuNjc0LTE3LjU4MywyMC40NDItMzIuMDYzCQkJCQkJQzU4LjQwMSwxNC44NTgsNDMuOTg0LDUuNzU4LDI5LjQ1Niw4Ljk4N0MxNC45MTYsMTIuMjI5LDUuNzc4LDI2LjU3OCw5LjAzOSw0MS4wNDJ6Ii8+CQkJCTwvZz4JCQk8L2c+CQk8L2c+CQk8Zz4JCQk8cmVjdCB4PSIxNC43NjYiIHk9IjI5LjUwMiIgd2lkdGg9IjQwLjA1OCIgaGVpZ2h0PSIxMS4zOTMiLz4JCTwvZz4JPC9nPgkJCTxsaW5lIHN0eWxlPSJmaWxsOm5vbmU7c3Ryb2tlOiNEOUZGRDk7c3Ryb2tlLXdpZHRoOjMuMDAwNztzdHJva2UtbGluZWNhcDpyb3VuZDtzdHJva2UtbGluZWpvaW46cm91bmQ7IiB4MT0iOTUuNzA0IiB5MT0iODcuNzk3IiB4Mj0iNzQuNjU4IiB5Mj0iNjguNTg2Ii8+CQkJPGxpbmUgc3R5bGU9ImZpbGw6bm9uZTtzdHJva2U6I0ZGRkZGRjtzdHJva2Utd2lkdGg6My4wMDA3O3N0cm9rZS1saW5lY2FwOnJvdW5kO3N0cm9rZS1saW5lam9pbjpyb3VuZDsiIHgxPSI2OS40MDMiIHkxPSI2Ni45NzQiIHgyPSI2Mi40NzUiIHkyPSI2MC42NDciLz48L2c+PC9zdmc+"
    }
}(ChemDoodle.extensions);
ChemDoodle.uis.gui.templateDepot = function(g, a, p) {
    p = [];
    let f = {
        name: "Functional Groups",
        templates: []
    };
    f.templates.push({
        name: "Alkenyl",
        data: {
            a: [{
                x: 194.002,
                y: 263.998
            }, {
                x: 214,
                y: 263.998
            }, {
                x: 184,
                y: 246.68
            }, {
                x: 184,
                y: 281.32
            }, {
                x: 224.002,
                y: 281.32
            }, {
                x: 224.002,
                y: 246.68
            }],
            b: [{
                b: 0,
                e: 1,
                o: 2
            }, {
                b: 0,
                e: 2
            }, {
                b: 0,
                e: 3
            }, {
                b: 1,
                e: 5
            }, {
                b: 1,
                e: 4
            }]
        }
    });
    f.templates.push({
        name: "Alkynyl",
        data: {
            a: [{
                    x: 193.998,
                    y: 264
                }, {
                    x: 174,
                    y: 264
                }, {
                    x: 213.998,
                    y: 264
                },
                {
                    x: 234,
                    y: 264
                }
            ],
            b: [{
                b: 0,
                e: 2,
                o: 3
            }, {
                b: 0,
                e: 1
            }, {
                b: 2,
                e: 3
            }]
        }
    });
    f.templates.push({
        name: "Amine",
        data: {
            a: [{
                x: 204.002,
                y: 259.002,
                l: "N"
            }, {
                x: 221.32,
                y: 249
            }, {
                x: 204.002,
                y: 279
            }, {
                x: 186.68,
                y: 249
            }],
            b: [{
                b: 0,
                e: 1
            }, {
                b: 0,
                e: 3
            }, {
                b: 0,
                e: 2
            }]
        }
    });
    f.templates.push({
        name: "Ammonium",
        data: {
            a: [{
                c: 1,
                x: 203.998,
                y: 265.342,
                l: "N"
            }, {
                x: 186.68,
                y: 275.34
            }, {
                x: 203.998,
                y: 245.34
            }, {
                x: 194,
                y: 282.66
            }, {
                x: 221.32,
                y: 275.34
            }],
            b: [{
                b: 0,
                e: 2
            }, {
                b: 0,
                e: 4
            }, {
                b: 0,
                e: 1
            }, {
                b: 0,
                e: 3
            }]
        }
    });
    f.templates.push({
        name: "Azide",
        data: {
            a: [{
                x: 178.02,
                y: 263.998
            }, {
                x: 195.34,
                y: 254,
                l: "N"
            }, {
                c: 1,
                x: 212.662,
                y: 263.998,
                l: "N"
            }, {
                c: -1,
                x: 229.98,
                y: 274,
                l: "N"
            }],
            b: [{
                b: 0,
                e: 1
            }, {
                b: 1,
                e: 2,
                o: 2
            }, {
                b: 2,
                e: 3,
                o: 2
            }]
        }
    });
    f.templates.push({
        name: "Azo",
        data: {
            a: [{
                x: 184,
                y: 246.68
            }, {
                x: 194,
                y: 264.002,
                l: "N"
            }, {
                x: 214,
                y: 264.002,
                l: "N"
            }, {
                x: 224,
                y: 281.32
            }],
            b: [{
                b: 0,
                e: 1
            }, {
                b: 1,
                e: 2,
                o: 2
            }, {
                b: 2,
                e: 3
            }]
        }
    });
    f.templates.push({
        name: "Benzyl",
        data: {
            a: [{
                x: 169.36,
                y: 254
            }, {
                x: 186.678,
                y: 244
            }, {
                x: 204,
                y: 254
            }, {
                x: 204,
                y: 274
            }, {
                x: 221.32,
                y: 244
            }, {
                x: 221.32,
                y: 284
            }, {
                x: 238.64,
                y: 254
            }, {
                x: 238.64,
                y: 274
            }],
            b: [{
                b: 0,
                e: 1
            }, {
                b: 1,
                e: 2
            }, {
                b: 2,
                e: 4,
                o: 2
            }, {
                b: 2,
                e: 3
            }, {
                b: 4,
                e: 6
            }, {
                b: 5,
                e: 3,
                o: 2
            }, {
                b: 6,
                e: 7,
                o: 2
            }, {
                b: 7,
                e: 5
            }]
        }
    });
    f.templates.push({
        name: "Carbonate Ester",
        data: {
            a: [{
                x: 186.678,
                y: 279,
                l: "O"
            }, {
                x: 169.36,
                y: 269.002
            }, {
                x: 204,
                y: 269.002
            }, {
                x: 221.32,
                y: 279,
                l: "O"
            }, {
                x: 204,
                y: 249,
                l: "O"
            }, {
                x: 238.642,
                y: 269.002
            }],
            b: [{
                b: 0,
                e: 2
            }, {
                b: 0,
                e: 1
            }, {
                b: 2,
                e: 4,
                o: 2
            }, {
                b: 2,
                e: 3
            }, {
                b: 3,
                e: 5
            }]
        }
    });
    f.templates.push({
        name: "Carbonyl",
        data: {
            a: [{
                x: 186.68,
                y: 279
            }, {
                x: 204.002,
                y: 268.998
            }, {
                x: 204.002,
                y: 249,
                l: "O"
            }, {
                x: 221.32,
                y: 279
            }],
            b: [{
                b: 0,
                e: 1
            }, {
                b: 1,
                e: 2,
                o: 2
            }, {
                b: 1,
                e: 3
            }]
        }
    });
    f.templates.push({
        name: "Carboxamide",
        data: {
            a: [{
                    x: 178.02,
                    y: 269
                },
                {
                    x: 195.34,
                    y: 259
                }, {
                    x: 195.34,
                    y: 239,
                    l: "O"
                }, {
                    x: 212.662,
                    y: 269,
                    l: "N"
                }, {
                    x: 212.662,
                    y: 289
                }, {
                    x: 229.98,
                    y: 259
                }
            ],
            b: [{
                b: 0,
                e: 1
            }, {
                b: 1,
                e: 2,
                o: 2
            }, {
                b: 1,
                e: 3
            }, {
                b: 3,
                e: 5
            }, {
                b: 3,
                e: 4
            }]
        }
    });
    f.templates.push({
        name: "Cyanate",
        data: {
            a: [{
                x: 178.02,
                y: 263.998
            }, {
                x: 195.338,
                y: 254,
                l: "O"
            }, {
                x: 212.66,
                y: 263.998
            }, {
                x: 229.98,
                y: 274,
                l: "N"
            }],
            b: [{
                b: 0,
                e: 1
            }, {
                b: 1,
                e: 2
            }, {
                b: 2,
                e: 3,
                o: 3
            }]
        }
    });
    f.templates.push({
        name: "Disulfide",
        data: {
            a: [{
                x: 184,
                y: 246.68
            }, {
                x: 194,
                y: 263.998,
                l: "S"
            }, {
                x: 214,
                y: 263.998,
                l: "S"
            }, {
                x: 224,
                y: 281.32
            }],
            b: [{
                b: 0,
                e: 1
            }, {
                b: 1,
                e: 2
            }, {
                b: 2,
                e: 3
            }]
        }
    });
    f.templates.push({
        name: "Ester",
        data: {
            a: [{
                x: 178.02,
                y: 279
            }, {
                x: 195.34,
                y: 269.002
            }, {
                x: 212.66,
                y: 279,
                l: "O"
            }, {
                x: 195.34,
                y: 249,
                l: "O"
            }, {
                x: 229.98,
                y: 269.002
            }],
            b: [{
                b: 0,
                e: 1
            }, {
                b: 1,
                e: 3,
                o: 2
            }, {
                b: 1,
                e: 2
            }, {
                b: 2,
                e: 4
            }]
        }
    });
    f.templates.push({
        name: "Ether",
        data: {
            a: [{
                x: 186.68,
                y: 269
            }, {
                x: 204.002,
                y: 259,
                l: "O"
            }, {
                x: 221.32,
                y: 269
            }],
            b: [{
                b: 0,
                e: 1
            }, {
                b: 1,
                e: 2
            }]
        }
    });
    f.templates.push({
        name: "Imide",
        data: {
            a: [{
                x: 169.36,
                y: 269.002
            }, {
                x: 186.678,
                y: 258.998
            }, {
                x: 186.678,
                y: 239.002,
                l: "O"
            }, {
                x: 204,
                y: 269.002,
                l: "N"
            }, {
                x: 204,
                y: 288.998
            }, {
                x: 221.32,
                y: 258.998
            }, {
                x: 238.64,
                y: 269.002
            }, {
                x: 221.32,
                y: 239.002,
                l: "O"
            }],
            b: [{
                b: 0,
                e: 1
            }, {
                b: 1,
                e: 3
            }, {
                b: 1,
                e: 2,
                o: 2
            }, {
                b: 3,
                e: 5
            }, {
                b: 3,
                e: 4
            }, {
                b: 5,
                e: 6
            }, {
                b: 5,
                e: 7,
                o: 2
            }]
        }
    });
    f.templates.push({
        name: "Isocyanate",
        data: {
            a: [{
                x: 178.02,
                y: 264.002
            }, {
                x: 195.34,
                y: 254,
                l: "N"
            }, {
                x: 212.662,
                y: 264.002
            }, {
                x: 229.98,
                y: 274,
                l: "O"
            }],
            b: [{
                b: 0,
                e: 1
            }, {
                b: 1,
                e: 2,
                o: 2
            }, {
                b: 2,
                e: 3,
                o: 2
            }]
        }
    });
    f.templates.push({
        name: "Isocyanide",
        data: {
            a: [{
                x: 184,
                y: 264
            }, {
                c: 1,
                x: 204.002,
                y: 264,
                l: "N"
            }, {
                c: -1,
                x: 224,
                y: 264
            }],
            b: [{
                b: 0,
                e: 1
            }, {
                b: 1,
                e: 2,
                o: 3
            }]
        }
    });
    f.templates.push({
        name: "Isothiocyanate",
        data: {
            a: [{
                x: 178.02,
                y: 264
            }, {
                x: 195.34,
                y: 254,
                l: "N"
            }, {
                x: 212.662,
                y: 264
            }, {
                x: 229.98,
                y: 274,
                l: "S"
            }],
            b: [{
                b: 0,
                e: 1
            }, {
                b: 1,
                e: 2,
                o: 2
            }, {
                b: 2,
                e: 3,
                o: 2
            }]
        }
    });
    f.templates.push({
        name: "Ketimine",
        data: {
            a: [{
                x: 204,
                y: 273.998
            }, {
                x: 204,
                y: 254.002,
                l: "N"
            }, {
                x: 221.32,
                y: 284.002
            }, {
                x: 186.68,
                y: 284.002
            }, {
                x: 221.32,
                y: 243.998
            }],
            b: [{
                b: 0,
                e: 1,
                o: 2
            }, {
                b: 0,
                e: 3
            }, {
                b: 0,
                e: 2
            }, {
                b: 1,
                e: 4
            }]
        }
    });
    f.templates.push({
        name: "Nitrate",
        data: {
            a: [{
                x: 178.02,
                y: 269
            }, {
                x: 195.338,
                y: 279,
                l: "O"
            }, {
                c: 1,
                x: 212.66,
                y: 269,
                l: "N"
            }, {
                c: -1,
                x: 229.98,
                y: 279,
                l: "O"
            }, {
                x: 212.66,
                y: 249,
                l: "O"
            }],
            b: [{
                b: 0,
                e: 1
            }, {
                b: 1,
                e: 2
            }, {
                b: 2,
                e: 3
            }, {
                b: 2,
                e: 4,
                o: 2
            }]
        }
    });
    f.templates.push({
        name: "Nitrile",
        data: {
            a: [{
                x: 184,
                y: 264
            }, {
                x: 204.002,
                y: 264
            }, {
                x: 224,
                y: 264,
                l: "N"
            }],
            b: [{
                b: 0,
                e: 1
            }, {
                b: 1,
                e: 2,
                o: 3
            }]
        }
    });
    f.templates.push({
        name: "Nitro",
        data: {
            a: [{
                x: 189,
                y: 263.998
            }, {
                c: 1,
                x: 209.002,
                y: 263.998,
                l: "N"
            }, {
                c: -1,
                x: 219,
                y: 281.32,
                l: "O"
            }, {
                x: 219,
                y: 246.68,
                l: "O"
            }],
            b: [{
                b: 0,
                e: 1
            }, {
                b: 1,
                e: 3,
                o: 2
            }, {
                b: 1,
                e: 2
            }]
        }
    });
    f.templates.push({
        name: "Nitroso",
        data: {
            a: [{
                x: 186.68,
                y: 269
            }, {
                x: 203.998,
                y: 259,
                l: "N"
            }, {
                x: 221.32,
                y: 269,
                l: "O"
            }],
            b: [{
                b: 0,
                e: 1
            }, {
                b: 1,
                e: 2,
                o: 2
            }]
        }
    });
    f.templates.push({
        name: "Nitrosooxy",
        data: {
            a: [{
                x: 178.018,
                y: 259
            }, {
                x: 195.34,
                y: 269,
                l: "O"
            }, {
                x: 212.66,
                y: 259,
                l: "N"
            }, {
                x: 229.982,
                y: 269,
                l: "O"
            }],
            b: [{
                b: 0,
                e: 1
            }, {
                b: 1,
                e: 2
            }, {
                b: 2,
                e: 3,
                o: 2
            }]
        }
    });
    f.templates.push({
        name: "Peroxy",
        data: {
            a: [{
                x: 183.998,
                y: 246.68
            }, {
                x: 194.002,
                y: 264.002,
                l: "O"
            }, {
                x: 213.998,
                y: 264.002,
                l: "O"
            }, {
                x: 224.002,
                y: 281.32
            }],
            b: [{
                b: 0,
                e: 1
            }, {
                b: 1,
                e: 2
            }, {
                b: 2,
                e: 3
            }]
        }
    });
    f.templates.push({
        name: "Phosphate",
        data: {
            a: [{
                x: 204,
                y: 265.342,
                l: "P"
            }, {
                x: 221.322,
                y: 275.34,
                l: "O"
            }, {
                x: 204,
                y: 245.34,
                l: "O"
            }, {
                x: 186.682,
                y: 275.34,
                l: "O"
            }, {
                x: 194.002,
                y: 282.66,
                l: "O"
            }, {
                x: 238.642,
                y: 265.342
            }, {
                x: 169.36,
                y: 265.342
            }, {
                x: 174,
                y: 282.66
            }],
            b: [{
                b: 0,
                e: 2,
                o: 2
            }, {
                b: 0,
                e: 1
            }, {
                b: 0,
                e: 3
            }, {
                b: 0,
                e: 4
            }, {
                b: 1,
                e: 5
            }, {
                b: 3,
                e: 6
            }, {
                b: 4,
                e: 7
            }]
        }
    });
    f.templates.push({
        name: "Phosphino",
        data: {
            a: [{
                x: 204,
                y: 255.34,
                l: "P"
            }, {
                x: 194.002,
                y: 272.66
            }, {
                x: 186.678,
                y: 265.34
            }, {
                x: 221.322,
                y: 265.34
            }],
            b: [{
                b: 0,
                e: 2
            }, {
                b: 0,
                e: 3
            }, {
                b: 0,
                e: 1
            }]
        }
    });
    f.templates.push({
        name: "Pyridyl",
        data: {
            a: [{
                x: 178.018,
                y: 244
            }, {
                x: 195.34,
                y: 254
            }, {
                x: 212.66,
                y: 244
            }, {
                x: 195.34,
                y: 274
            }, {
                x: 229.982,
                y: 254
            }, {
                x: 212.66,
                y: 284
            }, {
                x: 229.982,
                y: 274,
                l: "N"
            }],
            b: [{
                b: 0,
                e: 1
            }, {
                b: 1,
                e: 2,
                o: 2
            }, {
                b: 1,
                e: 3
            }, {
                b: 2,
                e: 4
            }, {
                b: 5,
                e: 3,
                o: 2
            }, {
                b: 4,
                e: 6,
                o: 2
            }, {
                b: 6,
                e: 5
            }]
        }
    });
    f.templates.push({
        name: "Sulfide",
        data: {
            a: [{
                x: 203.998,
                y: 259,
                l: "S"
            }, {
                x: 186.68,
                y: 269
            }, {
                x: 221.32,
                y: 269
            }],
            b: [{
                b: 0,
                e: 1
            }, {
                b: 0,
                e: 2
            }]
        }
    });
    f.templates.push({
        name: "Sulfinyl",
        data: {
            a: [{
                x: 186.68,
                y: 279
            }, {
                x: 203.998,
                y: 268.998,
                l: "S"
            }, {
                x: 203.998,
                y: 249,
                l: "O"
            }, {
                x: 221.32,
                y: 279
            }],
            b: [{
                b: 0,
                e: 1
            }, {
                b: 1,
                e: 3
            }, {
                b: 1,
                e: 2,
                o: 2
            }]
        }
    });
    f.templates.push({
        name: "Sulfonyl",
        data: {
            a: [{
                x: 204,
                y: 267.66,
                l: "S"
            }, {
                x: 194.002,
                y: 250.342,
                l: "O"
            }, {
                x: 213.998,
                y: 250.342,
                l: "O"
            }, {
                x: 186.68,
                y: 277.658
            }, {
                x: 221.32,
                y: 277.658
            }],
            b: [{
                b: 0,
                e: 3
            }, {
                b: 0,
                e: 4
            }, {
                b: 0,
                e: 1,
                o: 2
            }, {
                b: 0,
                e: 2,
                o: 2
            }]
        }
    });
    f.templates.push({
        name: "Thiocyanate",
        data: {
            a: [{
                x: 178.018,
                y: 264.002
            }, {
                x: 195.34,
                y: 254,
                l: "S"
            }, {
                x: 212.66,
                y: 264.002
            }, {
                x: 229.982,
                y: 274,
                l: "N"
            }],
            b: [{
                b: 0,
                e: 1
            }, {
                b: 1,
                e: 2
            }, {
                b: 2,
                e: 3,
                o: 3
            }]
        }
    });
    p.push(f);
    f = {
        name: "Sugars (Hexoses)",
        templates: []
    };
    f.templates.push({
        name: "Allose \x3ci\x3eFisher Projection\x3c/i\x3e",
        data: {
            a: [{
                x: 0,
                y: -50,
                l: "CHO"
            }, {
                x: 0,
                y: -30
            }, {
                x: 0,
                y: -10
            }, {
                x: 20,
                y: -30,
                l: "O"
            }, {
                x: -20,
                y: -30,
                l: "H"
            }, {
                x: -20,
                y: -10,
                l: "H"
            }, {
                x: 20,
                y: -10,
                l: "O"
            }, {
                x: 0,
                y: 10
            }, {
                x: 20,
                y: 10,
                l: "O"
            }, {
                x: -20,
                y: 10,
                l: "H"
            }, {
                x: 0,
                y: 30
            }, {
                x: -20,
                y: 30,
                l: "H"
            }, {
                x: 20,
                y: 30,
                l: "O"
            }, {
                x: 0,
                y: 50,
                l: "CH2OH"
            }],
            b: [{
                b: 0,
                e: 1
            }, {
                b: 1,
                e: 4
            }, {
                b: 1,
                e: 3
            }, {
                b: 1,
                e: 2
            }, {
                b: 2,
                e: 5
            }, {
                b: 2,
                e: 6
            }, {
                b: 2,
                e: 7
            }, {
                b: 7,
                e: 9
            }, {
                b: 7,
                e: 8
            }, {
                b: 7,
                e: 10
            }, {
                b: 10,
                e: 11
            }, {
                b: 10,
                e: 12
            }, {
                b: 10,
                e: 13
            }]
        }
    });
    f.templates.push({
        name: "Allose \x3ci\x3eFuranose Form\x3c/i\x3e",
        data: {
            a: [{
                    x: 7.3205,
                    y: -13.6239,
                    l: "O"
                }, {
                    x: -27.7677,
                    y: -1.3055
                }, {
                    x: 42.4087,
                    y: -1.3055
                }, {
                    x: -14.3652,
                    y: 18.6261
                }, {
                    x: -27.7677,
                    y: -21.3055
                }, {
                    x: -27.7677,
                    y: 18.6945,
                    l: "H"
                }, {
                    x: 29.0062,
                    y: 18.6261
                }, {
                    x: 62.4087,
                    y: -1.3055,
                    l: "O"
                }, {
                    x: -14.3652,
                    y: 38.6261,
                    l: "O"
                }, {
                    x: -14.3652,
                    y: -1.3739,
                    l: "H"
                }, {
                    x: -17.7677,
                    y: -38.6261,
                    l: "O"
                },
                {
                    x: -45.0882,
                    y: -31.3055
                }, {
                    x: -9.2969,
                    y: -28.9755,
                    l: "H"
                }, {
                    x: 29.0062,
                    y: 38.6261,
                    l: "O"
                }, {
                    x: 29.0062,
                    y: -1.3739,
                    l: "H"
                }, {
                    x: -62.4087,
                    y: -21.3055,
                    l: "O"
                }
            ],
            b: [{
                b: 0,
                e: 1
            }, {
                b: 1,
                e: 3
            }, {
                b: 3,
                e: 6,
                o: 1
            }, {
                b: 2,
                e: 6
            }, {
                b: 2,
                e: 0
            }, {
                b: 3,
                e: 9
            }, {
                b: 3,
                e: 8
            }, {
                b: 6,
                e: 14
            }, {
                b: 6,
                e: 13
            }, {
                b: 1,
                e: 4
            }, {
                b: 1,
                e: 5
            }, {
                b: 4,
                e: 11
            }, {
                b: 11,
                e: 15
            }, {
                b: 4,
                e: 10
            }, {
                b: 4,
                e: 12
            }, {
                b: 2,
                e: 7,
                o: 1
            }]
        }
    });
    f.templates.push({
        name: "Allose \x3ci\x3ePyranose Form\x3c/i\x3e",
        data: {
            a: [{
                x: -36.6654,
                y: -9.7292
            }, {
                x: -22.0845,
                y: 15.5237
            }, {
                x: -36.6654,
                y: -29.7292,
                l: "H"
            }, {
                x: -8.6254,
                y: -2.3409
            }, {
                x: -54.1679,
                y: -.0514,
                l: "O"
            }, {
                x: -22.0845,
                y: 35.5237,
                l: "O"
            }, {
                x: -41.6882,
                y: 11.5623,
                l: "H"
            }, {
                x: 6.1279,
                y: 8.1324
            }, {
                x: -8.6254,
                y: 24.8818,
                l: "H"
            }, {
                x: -23.6658,
                y: -15.5237
            }, {
                x: 19.5899,
                y: -9.7292,
                l: "O"
            }, {
                x: 34.1679,
                y: 15.5237
            }, {
                x: 6.1279,
                y: -11.8676,
                l: "H"
            }, {
                x: 20.3041,
                y: 22.2404,
                l: "O"
            }, {
                x: -23.6658,
                y: -35.5237,
                l: "O"
            }, {
                x: 54.1679,
                y: 15.5237,
                l: "O"
            }],
            b: [{
                b: 0,
                e: 1
            }, {
                b: 3,
                e: 0
            }, {
                b: 10,
                e: 3
            }, {
                b: 11,
                e: 7
            }, {
                b: 11,
                e: 10
            }, {
                b: 3,
                e: 8
            }, {
                b: 7,
                e: 12
            }, {
                b: 7,
                e: 13
            }, {
                b: 3,
                e: 9
            }, {
                b: 9,
                e: 14
            }, {
                b: 0,
                e: 2
            }, {
                b: 0,
                e: 4
            }, {
                b: 1,
                e: 5
            }, {
                b: 1,
                e: 6
            }, {
                b: 1,
                e: 7,
                o: 1
            }, {
                b: 11,
                e: 15,
                o: 1
            }]
        }
    });
    f.templates.push({
        name: "Altrose \x3ci\x3eFisher Projection\x3c/i\x3e",
        data: {
            a: [{
                x: 0,
                y: -50,
                l: "CHO"
            }, {
                x: 0,
                y: -30
            }, {
                x: -20,
                y: -30,
                l: "O"
            }, {
                x: 0,
                y: -10
            }, {
                x: 20,
                y: -30,
                l: "H"
            }, {
                x: -20,
                y: -10,
                l: "H"
            }, {
                x: 20,
                y: -10,
                l: "O"
            }, {
                x: 0,
                y: 10
            }, {
                x: 20,
                y: 10,
                l: "O"
            }, {
                x: -20,
                y: 10,
                l: "H"
            }, {
                x: 0,
                y: 30
            }, {
                x: -20,
                y: 30,
                l: "H"
            }, {
                x: 0,
                y: 50,
                l: "CH2OH"
            }, {
                x: 20,
                y: 30,
                l: "O"
            }],
            b: [{
                b: 0,
                e: 1
            }, {
                b: 1,
                e: 2
            }, {
                b: 1,
                e: 4
            }, {
                b: 1,
                e: 3
            }, {
                b: 3,
                e: 5
            }, {
                b: 3,
                e: 6
            }, {
                b: 3,
                e: 7
            }, {
                b: 7,
                e: 9
            }, {
                b: 7,
                e: 8
            }, {
                b: 7,
                e: 10
            }, {
                b: 10,
                e: 11
            }, {
                b: 10,
                e: 13
            }, {
                b: 10,
                e: 12
            }]
        }
    });
    f.templates.push({
        name: "Altrose \x3ci\x3eFuranose Form\x3c/i\x3e",
        data: {
            a: [{
                x: 7.3205,
                y: -13.6239,
                l: "O"
            }, {
                x: -27.7677,
                y: -1.3055
            }, {
                x: 42.4087,
                y: -1.3055
            }, {
                x: -27.7677,
                y: 18.6945,
                l: "H"
            }, {
                x: -14.3652,
                y: 18.6261
            }, {
                x: -27.7677,
                y: -21.3055
            }, {
                x: 29.0062,
                y: 18.6261
            }, {
                x: 62.4087,
                y: -1.3055,
                l: "O"
            }, {
                x: -14.3652,
                y: 38.6261,
                l: "O"
            }, {
                x: -14.3652,
                y: -1.3739,
                l: "H"
            }, {
                x: -9.2969,
                y: -28.9755,
                l: "H"
            }, {
                x: -45.0882,
                y: -31.3055
            }, {
                x: -17.7677,
                y: -38.6261,
                l: "O"
            }, {
                x: 29.0062,
                y: -1.3739,
                l: "O"
            }, {
                x: 29.0062,
                y: 38.6261,
                l: "H"
            }, {
                x: -62.4087,
                y: -21.3055,
                l: "O"
            }],
            b: [{
                b: 0,
                e: 1
            }, {
                b: 1,
                e: 4
            }, {
                b: 4,
                e: 6,
                o: 1
            }, {
                b: 2,
                e: 6
            }, {
                b: 2,
                e: 0
            }, {
                b: 4,
                e: 9
            }, {
                b: 4,
                e: 8
            }, {
                b: 6,
                e: 13
            }, {
                b: 6,
                e: 14
            }, {
                b: 1,
                e: 5
            }, {
                b: 1,
                e: 3
            }, {
                b: 5,
                e: 11
            }, {
                b: 11,
                e: 15
            }, {
                b: 5,
                e: 12
            }, {
                b: 5,
                e: 10
            }, {
                b: 2,
                e: 7,
                o: 1
            }]
        }
    });
    f.templates.push({
        name: "Altrose \x3ci\x3ePyranose Form\x3c/i\x3e",
        data: {
            a: [{
                    x: -36.6654,
                    y: -9.7292
                }, {
                    x: -22.0845,
                    y: 15.5237
                }, {
                    x: -36.6654,
                    y: -29.7292,
                    l: "H"
                }, {
                    x: -8.6254,
                    y: -2.3409
                }, {
                    x: -54.1679,
                    y: -.0514,
                    l: "O"
                }, {
                    x: -22.0845,
                    y: 35.5237,
                    l: "O"
                }, {
                    x: 6.1279,
                    y: 8.1324
                }, {
                    x: -41.6882,
                    y: 11.5623,
                    l: "H"
                }, {
                    x: -8.6254,
                    y: 24.8818,
                    l: "H"
                }, {
                    x: 19.5899,
                    y: -9.7292,
                    l: "O"
                }, {
                    x: -23.6658,
                    y: -15.5237
                }, {
                    x: 20.3041,
                    y: 22.2404,
                    l: "H"
                }, {
                    x: 34.1679,
                    y: 15.5237
                }, {
                    x: 6.1279,
                    y: -11.8676,
                    l: "O"
                },
                {
                    x: -23.6658,
                    y: -35.5237,
                    l: "O"
                }, {
                    x: 54.1679,
                    y: 15.5237,
                    l: "O"
                }
            ],
            b: [{
                b: 0,
                e: 1
            }, {
                b: 3,
                e: 0
            }, {
                b: 9,
                e: 3
            }, {
                b: 12,
                e: 6
            }, {
                b: 12,
                e: 9
            }, {
                b: 3,
                e: 8
            }, {
                b: 6,
                e: 13
            }, {
                b: 6,
                e: 11
            }, {
                b: 3,
                e: 10
            }, {
                b: 10,
                e: 14
            }, {
                b: 0,
                e: 2
            }, {
                b: 0,
                e: 4
            }, {
                b: 1,
                e: 5
            }, {
                b: 1,
                e: 7
            }, {
                b: 1,
                e: 6,
                o: 1
            }, {
                b: 12,
                e: 15,
                o: 1
            }]
        }
    });
    f.templates.push({
        name: "Galactose \x3ci\x3eFisher Projection\x3c/i\x3e",
        data: {
            a: [{
                    x: 0,
                    y: -50,
                    l: "CHO"
                }, {
                    x: 0,
                    y: -30
                }, {
                    x: 20,
                    y: -30,
                    l: "O"
                }, {
                    x: 0,
                    y: -10
                }, {
                    x: -20,
                    y: -30,
                    l: "H"
                }, {
                    x: -20,
                    y: -10,
                    l: "O"
                }, {
                    x: 20,
                    y: -10,
                    l: "H"
                }, {
                    x: 0,
                    y: 10
                }, {
                    x: -20,
                    y: 10,
                    l: "O"
                }, {
                    x: 20,
                    y: 10,
                    l: "H"
                }, {
                    x: 0,
                    y: 30
                },
                {
                    x: 20,
                    y: 30,
                    l: "O"
                }, {
                    x: 0,
                    y: 50,
                    l: "CH2OH"
                }, {
                    x: -20,
                    y: 30,
                    l: "H"
                }
            ],
            b: [{
                b: 0,
                e: 1
            }, {
                b: 1,
                e: 4
            }, {
                b: 1,
                e: 2
            }, {
                b: 1,
                e: 3
            }, {
                b: 3,
                e: 5
            }, {
                b: 3,
                e: 6
            }, {
                b: 3,
                e: 7
            }, {
                b: 7,
                e: 8
            }, {
                b: 7,
                e: 9
            }, {
                b: 7,
                e: 10
            }, {
                b: 10,
                e: 13
            }, {
                b: 10,
                e: 11
            }, {
                b: 10,
                e: 12
            }]
        }
    });
    f.templates.push({
        name: "Galactose \x3ci\x3eFuranose Form\x3c/i\x3e",
        data: {
            a: [{
                    x: 8.6603,
                    y: -22.3184,
                    l: "O"
                }, {
                    x: 43.7485,
                    y: -10
                }, {
                    x: -26.428,
                    y: -10
                }, {
                    x: 30.346,
                    y: 9.9316
                }, {
                    x: 63.7485,
                    y: -10,
                    l: "O"
                }, {
                    x: -43.7485,
                    y: 0
                }, {
                    x: -13.0255,
                    y: 9.9316
                }, {
                    x: -26.428,
                    y: -30,
                    l: "H"
                }, {
                    x: 30.346,
                    y: -10.0684,
                    l: "H"
                }, {
                    x: 30.346,
                    y: 29.9316,
                    l: "O"
                },
                {
                    x: -63.7485,
                    y: 0,
                    l: "O"
                }, {
                    x: -53.7485,
                    y: -17.3205,
                    l: "H"
                }, {
                    x: -43.7485,
                    y: 20
                }, {
                    x: -13.0255,
                    y: -10.0684,
                    l: "O"
                }, {
                    x: -13.0255,
                    y: 29.9316,
                    l: "H"
                }, {
                    x: -61.069,
                    y: 30,
                    l: "O"
                }
            ],
            b: [{
                b: 6,
                e: 3,
                o: 1
            }, {
                b: 1,
                e: 3
            }, {
                b: 1,
                e: 0
            }, {
                b: 6,
                e: 13
            }, {
                b: 6,
                e: 14
            }, {
                b: 3,
                e: 8
            }, {
                b: 3,
                e: 9
            }, {
                b: 1,
                e: 4,
                o: 1
            }, {
                b: 0,
                e: 2
            }, {
                b: 2,
                e: 6
            }, {
                b: 2,
                e: 7
            }, {
                b: 2,
                e: 5
            }, {
                b: 5,
                e: 12
            }, {
                b: 12,
                e: 15
            }, {
                b: 5,
                e: 11
            }, {
                b: 5,
                e: 10
            }]
        }
    });
    f.templates.push({
        name: "Galactose \x3ci\x3ePyranose Form\x3c/i\x3e",
        data: {
            a: [{
                x: -36.6654,
                y: -9.7292
            }, {
                x: -36.6654,
                y: -29.7292,
                l: "O"
            }, {
                x: -54.1679,
                y: -.0514,
                l: "H"
            }, {
                x: -22.0845,
                y: 15.5237
            }, {
                x: -8.6254,
                y: -2.3409
            }, {
                x: -41.6882,
                y: 11.5623,
                l: "O"
            }, {
                x: 6.1279,
                y: 8.1324
            }, {
                x: -22.0845,
                y: 35.5237,
                l: "H"
            }, {
                x: -8.6254,
                y: 24.8818,
                l: "H"
            }, {
                x: -23.6658,
                y: -15.5237
            }, {
                x: 19.5899,
                y: -9.7292,
                l: "O"
            }, {
                x: 34.1679,
                y: 15.5237
            }, {
                x: 6.1279,
                y: -11.8676,
                l: "H"
            }, {
                x: 20.3041,
                y: 22.2404,
                l: "O"
            }, {
                x: -23.6658,
                y: -35.5237,
                l: "O"
            }, {
                x: 54.1679,
                y: 15.5237,
                l: "O"
            }],
            b: [{
                b: 0,
                e: 3
            }, {
                b: 4,
                e: 0
            }, {
                b: 10,
                e: 4
            }, {
                b: 11,
                e: 6
            }, {
                b: 11,
                e: 10
            }, {
                b: 4,
                e: 8
            }, {
                b: 6,
                e: 12
            }, {
                b: 6,
                e: 13
            }, {
                b: 4,
                e: 9
            }, {
                b: 9,
                e: 14
            }, {
                b: 0,
                e: 1
            }, {
                b: 0,
                e: 2
            }, {
                b: 3,
                e: 7
            }, {
                b: 3,
                e: 5
            }, {
                b: 3,
                e: 6,
                o: 1
            }, {
                b: 11,
                e: 15,
                o: 1
            }]
        }
    });
    f.templates.push({
        name: "Glucose \x3ci\x3eFisher Projection\x3c/i\x3e",
        data: {
            a: [{
                x: 0,
                y: -50,
                l: "CHO"
            }, {
                x: 0,
                y: -30
            }, {
                x: -20,
                y: -30,
                l: "H"
            }, {
                x: 20,
                y: -30,
                l: "O"
            }, {
                x: 0,
                y: -10
            }, {
                x: 20,
                y: -10,
                l: "H"
            }, {
                x: -20,
                y: -10,
                l: "O"
            }, {
                x: 0,
                y: 10
            }, {
                x: -20,
                y: 10,
                l: "H"
            }, {
                x: 20,
                y: 10,
                l: "O"
            }, {
                x: 0,
                y: 30
            }, {
                x: -20,
                y: 30,
                l: "H"
            }, {
                x: 20,
                y: 30,
                l: "O"
            }, {
                x: 0,
                y: 50,
                l: "CH2OH"
            }],
            b: [{
                b: 0,
                e: 1
            }, {
                b: 1,
                e: 2
            }, {
                b: 1,
                e: 3
            }, {
                b: 1,
                e: 4
            }, {
                b: 4,
                e: 6
            }, {
                b: 4,
                e: 5
            }, {
                b: 4,
                e: 7
            }, {
                b: 7,
                e: 8
            }, {
                b: 7,
                e: 9
            }, {
                b: 7,
                e: 10
            }, {
                b: 10,
                e: 11
            }, {
                b: 10,
                e: 12
            }, {
                b: 10,
                e: 13
            }]
        }
    });
    f.templates.push({
        name: "Glucose \x3ci\x3eFuranose Form\x3c/i\x3e",
        data: {
            a: [{
                x: 7.3205,
                y: -13.6239,
                l: "O"
            }, {
                x: 42.4087,
                y: -1.3055
            }, {
                x: -27.7677,
                y: -1.3055
            }, {
                x: 29.0062,
                y: 18.6261
            }, {
                x: 62.4087,
                y: -1.3055,
                l: "O"
            }, {
                x: -27.7677,
                y: 18.6945,
                l: "H"
            }, {
                x: -14.3652,
                y: 18.6261
            }, {
                x: -27.7677,
                y: -21.3055
            }, {
                x: 29.0062,
                y: 38.6261,
                l: "O"
            }, {
                x: 29.0062,
                y: -1.3739,
                l: "H"
            }, {
                x: -14.3652,
                y: 38.6261,
                l: "H"
            }, {
                x: -14.3652,
                y: -1.3739,
                l: "O"
            }, {
                x: -9.2969,
                y: -28.9755,
                l: "H"
            }, {
                x: -17.7677,
                y: -38.6261,
                l: "O"
            }, {
                x: -45.0882,
                y: -31.3055
            }, {
                x: -62.4087,
                y: -21.3055,
                l: "O"
            }],
            b: [{
                    b: 0,
                    e: 2
                }, {
                    b: 2,
                    e: 6
                }, {
                    b: 6,
                    e: 3,
                    o: 1
                }, {
                    b: 1,
                    e: 3
                }, {
                    b: 1,
                    e: 0
                }, {
                    b: 6,
                    e: 11
                },
                {
                    b: 6,
                    e: 10
                }, {
                    b: 3,
                    e: 9
                }, {
                    b: 3,
                    e: 8
                }, {
                    b: 2,
                    e: 7
                }, {
                    b: 2,
                    e: 5
                }, {
                    b: 7,
                    e: 14
                }, {
                    b: 14,
                    e: 15
                }, {
                    b: 7,
                    e: 13
                }, {
                    b: 7,
                    e: 12
                }, {
                    b: 1,
                    e: 4,
                    o: 1
                }
            ]
        }
    });
    f.templates.push({
        name: "Glucose \x3ci\x3ePyranose Form\x3c/i\x3e",
        data: {
            a: [{
                x: -36.6654,
                y: -9.7292
            }, {
                x: -54.1679,
                y: -.0514,
                l: "O"
            }, {
                x: -36.6654,
                y: -29.7292,
                l: "H"
            }, {
                x: -8.6254,
                y: -2.3409
            }, {
                x: -22.0845,
                y: 15.5237
            }, {
                x: 19.5899,
                y: -9.7292,
                l: "O"
            }, {
                x: -8.6254,
                y: 24.8818,
                l: "H"
            }, {
                x: -23.6658,
                y: -15.5237
            }, {
                x: -22.0845,
                y: 35.5237,
                l: "H"
            }, {
                x: 6.1279,
                y: 8.1324
            }, {
                x: -41.6882,
                y: 11.5623,
                l: "O"
            }, {
                x: 34.1679,
                y: 15.5237
            }, {
                x: -23.6658,
                y: -35.5237,
                l: "O"
            }, {
                x: 20.3041,
                y: 22.2404,
                l: "O"
            }, {
                x: 6.1279,
                y: -11.8676,
                l: "H"
            }, {
                x: 54.1679,
                y: 15.5237,
                l: "O"
            }],
            b: [{
                b: 0,
                e: 4
            }, {
                b: 3,
                e: 0
            }, {
                b: 5,
                e: 3
            }, {
                b: 11,
                e: 9
            }, {
                b: 11,
                e: 5
            }, {
                b: 3,
                e: 6
            }, {
                b: 9,
                e: 14
            }, {
                b: 9,
                e: 13
            }, {
                b: 3,
                e: 7
            }, {
                b: 7,
                e: 12
            }, {
                b: 0,
                e: 2
            }, {
                b: 0,
                e: 1
            }, {
                b: 4,
                e: 8
            }, {
                b: 4,
                e: 10
            }, {
                b: 4,
                e: 9,
                o: 1
            }, {
                b: 11,
                e: 15,
                o: 1
            }]
        }
    });
    f.templates.push({
        name: "Gulose \x3ci\x3eFisher Projection\x3c/i\x3e",
        data: {
            a: [{
                x: 0,
                y: -50,
                l: "CHO"
            }, {
                x: 0,
                y: -30
            }, {
                x: -20,
                y: -30,
                l: "H"
            }, {
                x: 20,
                y: -30,
                l: "O"
            }, {
                x: 0,
                y: -10
            }, {
                x: -20,
                y: -10,
                l: "H"
            }, {
                x: 20,
                y: -10,
                l: "O"
            }, {
                x: 0,
                y: 10
            }, {
                x: -20,
                y: 10,
                l: "O"
            }, {
                x: 20,
                y: 10,
                l: "H"
            }, {
                x: 0,
                y: 30
            }, {
                x: -20,
                y: 30,
                l: "H"
            }, {
                x: 20,
                y: 30,
                l: "O"
            }, {
                x: 0,
                y: 50,
                l: "CH2OH"
            }],
            b: [{
                b: 0,
                e: 1
            }, {
                b: 1,
                e: 2
            }, {
                b: 1,
                e: 3
            }, {
                b: 1,
                e: 4
            }, {
                b: 4,
                e: 5
            }, {
                b: 4,
                e: 6
            }, {
                b: 4,
                e: 7
            }, {
                b: 7,
                e: 8
            }, {
                b: 7,
                e: 9
            }, {
                b: 7,
                e: 10
            }, {
                b: 10,
                e: 11
            }, {
                b: 10,
                e: 12
            }, {
                b: 10,
                e: 13
            }]
        }
    });
    f.templates.push({
        name: "Gulose \x3ci\x3eFuranose Form\x3c/i\x3e",
        data: {
            a: [{
                x: 8.6603,
                y: -22.3184,
                l: "O"
            }, {
                x: 43.7485,
                y: -10
            }, {
                x: -26.428,
                y: -10
            }, {
                x: 63.7485,
                y: -10,
                l: "O"
            }, {
                x: 30.346,
                y: 9.9316
            }, {
                x: -43.7485,
                y: 0
            }, {
                x: -13.0255,
                y: 9.9316
            }, {
                x: -26.428,
                y: -30,
                l: "H"
            }, {
                x: 30.346,
                y: 29.9316,
                l: "O"
            }, {
                x: 30.346,
                y: -10.0684,
                l: "H"
            }, {
                x: -43.7485,
                y: 20
            }, {
                x: -53.7485,
                y: -17.3205,
                l: "H"
            }, {
                x: -63.7485,
                y: 0,
                l: "O"
            }, {
                x: -13.0255,
                y: 29.9316,
                l: "O"
            }, {
                x: -13.0255,
                y: -10.0684,
                l: "H"
            }, {
                x: -61.069,
                y: 30,
                l: "O"
            }],
            b: [{
                b: 6,
                e: 4,
                o: 1
            }, {
                b: 1,
                e: 4
            }, {
                b: 1,
                e: 0
            }, {
                b: 6,
                e: 14
            }, {
                b: 6,
                e: 13
            }, {
                b: 4,
                e: 9
            }, {
                b: 4,
                e: 8
            }, {
                b: 1,
                e: 3,
                o: 1
            }, {
                b: 0,
                e: 2
            }, {
                b: 2,
                e: 6
            }, {
                b: 2,
                e: 7
            }, {
                b: 2,
                e: 5
            }, {
                b: 5,
                e: 10
            }, {
                b: 10,
                e: 15
            }, {
                b: 5,
                e: 11
            }, {
                b: 5,
                e: 12
            }]
        }
    });
    f.templates.push({
        name: "Gulose \x3ci\x3ePyranose Form\x3c/i\x3e",
        data: {
            a: [{
                x: -36.6654,
                y: -9.7292
            }, {
                x: -22.0845,
                y: 15.5237
            }, {
                x: -36.6654,
                y: -29.7292,
                l: "O"
            }, {
                x: -54.1679,
                y: -.0514,
                l: "H"
            }, {
                x: -8.6254,
                y: -2.3409
            }, {
                x: -41.6882,
                y: 11.5623,
                l: "H"
            }, {
                x: -22.0845,
                y: 35.5237,
                l: "O"
            }, {
                x: 6.1279,
                y: 8.1324
            }, {
                x: -8.6254,
                y: 24.8818,
                l: "H"
            }, {
                x: 19.5899,
                y: -9.7292,
                l: "O"
            }, {
                x: -23.6658,
                y: -15.5237
            }, {
                x: 34.1679,
                y: 15.5237
            }, {
                x: 6.1279,
                y: -11.8676,
                l: "H"
            }, {
                x: 20.3041,
                y: 22.2404,
                l: "O"
            }, {
                x: -23.6658,
                y: -35.5237,
                l: "O"
            }, {
                x: 54.1679,
                y: 15.5237,
                l: "O"
            }],
            b: [{
                    b: 0,
                    e: 1
                }, {
                    b: 4,
                    e: 0
                }, {
                    b: 9,
                    e: 4
                }, {
                    b: 11,
                    e: 7
                }, {
                    b: 11,
                    e: 9
                }, {
                    b: 4,
                    e: 8
                }, {
                    b: 7,
                    e: 12
                }, {
                    b: 7,
                    e: 13
                }, {
                    b: 4,
                    e: 10
                }, {
                    b: 10,
                    e: 14
                }, {
                    b: 0,
                    e: 2
                }, {
                    b: 0,
                    e: 3
                }, {
                    b: 1,
                    e: 6
                },
                {
                    b: 1,
                    e: 5
                }, {
                    b: 1,
                    e: 7,
                    o: 1
                }, {
                    b: 11,
                    e: 15,
                    o: 1
                }
            ]
        }
    });
    f.templates.push({
        name: "Idose \x3ci\x3eFisher Projection\x3c/i\x3e",
        data: {
            a: [{
                x: 0,
                y: -50,
                l: "CHO"
            }, {
                x: 0,
                y: -30
            }, {
                x: 0,
                y: -10
            }, {
                x: 20,
                y: -30,
                l: "H"
            }, {
                x: -20,
                y: -30,
                l: "O"
            }, {
                x: 0,
                y: 10
            }, {
                x: -20,
                y: -10,
                l: "H"
            }, {
                x: 20,
                y: -10,
                l: "O"
            }, {
                x: 0,
                y: 30
            }, {
                x: -20,
                y: 10,
                l: "O"
            }, {
                x: 20,
                y: 10,
                l: "H"
            }, {
                x: -20,
                y: 30,
                l: "H"
            }, {
                x: 20,
                y: 30,
                l: "O"
            }, {
                x: 0,
                y: 50,
                l: "CH2OH"
            }],
            b: [{
                b: 0,
                e: 1
            }, {
                b: 1,
                e: 4
            }, {
                b: 1,
                e: 3
            }, {
                b: 1,
                e: 2
            }, {
                b: 2,
                e: 6
            }, {
                b: 2,
                e: 7
            }, {
                b: 2,
                e: 5
            }, {
                b: 5,
                e: 9
            }, {
                b: 5,
                e: 10
            }, {
                b: 5,
                e: 8
            }, {
                b: 8,
                e: 11
            }, {
                b: 8,
                e: 12
            }, {
                b: 8,
                e: 13
            }]
        }
    });
    f.templates.push({
        name: "Idose \x3ci\x3eFuranose Form\x3c/i\x3e",
        data: {
            a: [{
                x: 8.6603,
                y: -22.3184,
                l: "O"
            }, {
                x: 43.7485,
                y: -10
            }, {
                x: -26.428,
                y: -10
            }, {
                x: 30.346,
                y: 9.9316
            }, {
                x: 63.7485,
                y: -10,
                l: "O"
            }, {
                x: -43.7485,
                y: 0
            }, {
                x: -13.0255,
                y: 9.9316
            }, {
                x: -26.428,
                y: -30,
                l: "H"
            }, {
                x: 30.346,
                y: -10.0684,
                l: "O"
            }, {
                x: 30.346,
                y: 29.9316,
                l: "H"
            }, {
                x: -53.7485,
                y: -17.3205,
                l: "H"
            }, {
                x: -43.7485,
                y: 20
            }, {
                x: -63.7485,
                y: 0,
                l: "O"
            }, {
                x: -13.0255,
                y: -10.0684,
                l: "H"
            }, {
                x: -13.0255,
                y: 29.9316,
                l: "O"
            }, {
                x: -61.069,
                y: 30,
                l: "O"
            }],
            b: [{
                    b: 6,
                    e: 3,
                    o: 1
                }, {
                    b: 1,
                    e: 3
                }, {
                    b: 1,
                    e: 0
                }, {
                    b: 6,
                    e: 13
                },
                {
                    b: 6,
                    e: 14
                }, {
                    b: 3,
                    e: 8
                }, {
                    b: 3,
                    e: 9
                }, {
                    b: 1,
                    e: 4,
                    o: 1
                }, {
                    b: 0,
                    e: 2
                }, {
                    b: 2,
                    e: 6
                }, {
                    b: 2,
                    e: 7
                }, {
                    b: 2,
                    e: 5
                }, {
                    b: 5,
                    e: 11
                }, {
                    b: 11,
                    e: 15
                }, {
                    b: 5,
                    e: 10
                }, {
                    b: 5,
                    e: 12
                }
            ]
        }
    });
    f.templates.push({
        name: "Idose \x3ci\x3ePyranose Form\x3c/i\x3e",
        data: {
            a: [{
                x: -36.6654,
                y: -9.7292
            }, {
                x: -22.0845,
                y: 15.5237
            }, {
                x: -54.1679,
                y: -.0514,
                l: "H"
            }, {
                x: -8.6254,
                y: -2.3409
            }, {
                x: -36.6654,
                y: -29.7292,
                l: "O"
            }, {
                x: -41.6882,
                y: 11.5623,
                l: "H"
            }, {
                x: -22.0845,
                y: 35.5237,
                l: "O"
            }, {
                x: 6.1279,
                y: 8.1324
            }, {
                x: -8.6254,
                y: 24.8818,
                l: "H"
            }, {
                x: 19.5899,
                y: -9.7292,
                l: "O"
            }, {
                x: -23.6658,
                y: -15.5237
            }, {
                x: 20.3041,
                y: 22.2404,
                l: "H"
            }, {
                x: 6.1279,
                y: -11.8676,
                l: "O"
            }, {
                x: 34.1679,
                y: 15.5237
            }, {
                x: -23.6658,
                y: -35.5237,
                l: "O"
            }, {
                x: 54.1679,
                y: 15.5237,
                l: "O"
            }],
            b: [{
                b: 0,
                e: 1
            }, {
                b: 3,
                e: 0
            }, {
                b: 9,
                e: 3
            }, {
                b: 13,
                e: 7
            }, {
                b: 13,
                e: 9
            }, {
                b: 3,
                e: 8
            }, {
                b: 7,
                e: 12
            }, {
                b: 7,
                e: 11
            }, {
                b: 3,
                e: 10
            }, {
                b: 10,
                e: 14
            }, {
                b: 0,
                e: 4
            }, {
                b: 0,
                e: 2
            }, {
                b: 1,
                e: 6
            }, {
                b: 1,
                e: 5
            }, {
                b: 1,
                e: 7,
                o: 1
            }, {
                b: 13,
                e: 15,
                o: 1
            }]
        }
    });
    f.templates.push({
        name: "Mannose \x3ci\x3eFisher Projection\x3c/i\x3e",
        data: {
            a: [{
                x: 0,
                y: -50,
                l: "CHO"
            }, {
                x: 0,
                y: -30
            }, {
                x: 20,
                y: -30,
                l: "H"
            }, {
                x: -20,
                y: -30,
                l: "O"
            }, {
                x: 0,
                y: -10
            }, {
                x: 20,
                y: -10,
                l: "H"
            }, {
                x: -20,
                y: -10,
                l: "O"
            }, {
                x: 0,
                y: 10
            }, {
                x: 0,
                y: 30
            }, {
                x: -20,
                y: 10,
                l: "H"
            }, {
                x: 20,
                y: 10,
                l: "O"
            }, {
                x: -20,
                y: 30,
                l: "H"
            }, {
                x: 0,
                y: 50,
                l: "CH2OH"
            }, {
                x: 20,
                y: 30,
                l: "O"
            }],
            b: [{
                b: 0,
                e: 1
            }, {
                b: 1,
                e: 3
            }, {
                b: 1,
                e: 2
            }, {
                b: 1,
                e: 4
            }, {
                b: 4,
                e: 6
            }, {
                b: 4,
                e: 5
            }, {
                b: 4,
                e: 7
            }, {
                b: 7,
                e: 9
            }, {
                b: 7,
                e: 10
            }, {
                b: 7,
                e: 8
            }, {
                b: 8,
                e: 11
            }, {
                b: 8,
                e: 13
            }, {
                b: 8,
                e: 12
            }]
        }
    });
    f.templates.push({
        name: "Mannose \x3ci\x3eFuranose Form\x3c/i\x3e",
        data: {
            a: [{
                x: 7.3205,
                y: -13.6239,
                l: "O"
            }, {
                x: 42.4087,
                y: -1.3055
            }, {
                x: -27.7677,
                y: -1.3055
            }, {
                x: 29.0062,
                y: 18.6261
            }, {
                x: 62.4087,
                y: -1.3055,
                l: "O"
            }, {
                x: -14.3652,
                y: 18.6261
            }, {
                x: -27.7677,
                y: 18.6945,
                l: "H"
            }, {
                x: -27.7677,
                y: -21.3055
            }, {
                x: 29.0062,
                y: 38.6261,
                l: "H"
            }, {
                x: 29.0062,
                y: -1.3739,
                l: "O"
            }, {
                x: -14.3652,
                y: -1.3739,
                l: "O"
            }, {
                x: -14.3652,
                y: 38.6261,
                l: "H"
            }, {
                x: -9.2969,
                y: -28.9755,
                l: "H"
            }, {
                x: -45.0882,
                y: -31.3055
            }, {
                x: -17.7677,
                y: -38.6261,
                l: "O"
            }, {
                x: -62.4087,
                y: -21.3055,
                l: "O"
            }],
            b: [{
                b: 0,
                e: 2
            }, {
                b: 2,
                e: 5
            }, {
                b: 5,
                e: 3,
                o: 1
            }, {
                b: 1,
                e: 3
            }, {
                b: 1,
                e: 0
            }, {
                b: 5,
                e: 10
            }, {
                b: 5,
                e: 11
            }, {
                b: 3,
                e: 9
            }, {
                b: 3,
                e: 8
            }, {
                b: 2,
                e: 7
            }, {
                b: 2,
                e: 6
            }, {
                b: 7,
                e: 13
            }, {
                b: 13,
                e: 15
            }, {
                b: 7,
                e: 14
            }, {
                b: 7,
                e: 12
            }, {
                b: 1,
                e: 4,
                o: 1
            }]
        }
    });
    f.templates.push({
        name: "Mannose \x3ci\x3ePyranose Form\x3c/i\x3e",
        data: {
            a: [{
                x: -36.6654,
                y: -9.7292
            }, {
                x: -8.6254,
                y: -2.3409
            }, {
                x: -36.6654,
                y: -29.7292,
                l: "H"
            }, {
                x: -54.1679,
                y: -.0514,
                l: "O"
            }, {
                x: -22.0845,
                y: 15.5237
            }, {
                x: 19.5899,
                y: -9.7292,
                l: "O"
            }, {
                x: -8.6254,
                y: 24.8818,
                l: "H"
            }, {
                x: -23.6658,
                y: -15.5237
            }, {
                x: 6.1279,
                y: 8.1324
            }, {
                x: -22.0845,
                y: 35.5237,
                l: "H"
            }, {
                x: -41.6882,
                y: 11.5623,
                l: "O"
            }, {
                x: 34.1679,
                y: 15.5237
            }, {
                x: -23.6658,
                y: -35.5237,
                l: "O"
            }, {
                x: 6.1279,
                y: -11.8676,
                l: "O"
            }, {
                x: 20.3041,
                y: 22.2404,
                l: "H"
            }, {
                x: 54.1679,
                y: 15.5237,
                l: "O"
            }],
            b: [{
                    b: 0,
                    e: 4
                }, {
                    b: 1,
                    e: 0
                }, {
                    b: 5,
                    e: 1
                }, {
                    b: 11,
                    e: 8
                }, {
                    b: 11,
                    e: 5
                }, {
                    b: 1,
                    e: 6
                }, {
                    b: 8,
                    e: 13
                },
                {
                    b: 8,
                    e: 14
                }, {
                    b: 1,
                    e: 7
                }, {
                    b: 7,
                    e: 12
                }, {
                    b: 0,
                    e: 2
                }, {
                    b: 0,
                    e: 3
                }, {
                    b: 4,
                    e: 9
                }, {
                    b: 4,
                    e: 10
                }, {
                    b: 4,
                    e: 8,
                    o: 1
                }, {
                    b: 11,
                    e: 15,
                    o: 1
                }
            ]
        }
    });
    f.templates.push({
        name: "Talose \x3ci\x3eFisher Projection\x3c/i\x3e",
        data: {
            a: [{
                x: 0,
                y: -50,
                l: "CHO"
            }, {
                x: 0,
                y: -30
            }, {
                x: 0,
                y: -10
            }, {
                x: -20,
                y: -30,
                l: "O"
            }, {
                x: 20,
                y: -30,
                l: "H"
            }, {
                x: -20,
                y: -10,
                l: "O"
            }, {
                x: 20,
                y: -10,
                l: "H"
            }, {
                x: 0,
                y: 10
            }, {
                x: 20,
                y: 10,
                l: "H"
            }, {
                x: 0,
                y: 30
            }, {
                x: -20,
                y: 10,
                l: "O"
            }, {
                x: 20,
                y: 30,
                l: "O"
            }, {
                x: 0,
                y: 50,
                l: "CH2OH"
            }, {
                x: -20,
                y: 30,
                l: "H"
            }],
            b: [{
                b: 0,
                e: 1
            }, {
                b: 1,
                e: 3
            }, {
                b: 1,
                e: 4
            }, {
                b: 1,
                e: 2
            }, {
                b: 2,
                e: 5
            }, {
                b: 2,
                e: 6
            }, {
                b: 2,
                e: 7
            }, {
                b: 7,
                e: 10
            }, {
                b: 7,
                e: 8
            }, {
                b: 7,
                e: 9
            }, {
                b: 9,
                e: 13
            }, {
                b: 9,
                e: 11
            }, {
                b: 9,
                e: 12
            }]
        }
    });
    f.templates.push({
        name: "Talose \x3ci\x3eFuranose Form\x3c/i\x3e",
        data: {
            a: [{
                x: 8.6603,
                y: -22.3184,
                l: "O"
            }, {
                x: 43.7485,
                y: -10
            }, {
                x: -26.428,
                y: -10
            }, {
                x: 30.346,
                y: 9.9316
            }, {
                x: 63.7485,
                y: -10,
                l: "O"
            }, {
                x: -13.0255,
                y: 9.9316
            }, {
                x: -26.428,
                y: -30,
                l: "H"
            }, {
                x: -43.7485,
                y: 0
            }, {
                x: 30.346,
                y: 29.9316,
                l: "H"
            }, {
                x: 30.346,
                y: -10.0684,
                l: "O"
            }, {
                x: -13.0255,
                y: 29.9316,
                l: "H"
            }, {
                x: -13.0255,
                y: -10.0684,
                l: "O"
            }, {
                x: -43.7485,
                y: 20
            }, {
                x: -53.7485,
                y: -17.3205,
                l: "H"
            }, {
                x: -63.7485,
                y: 0,
                l: "O"
            }, {
                x: -61.069,
                y: 30,
                l: "O"
            }],
            b: [{
                b: 5,
                e: 3,
                o: 1
            }, {
                b: 1,
                e: 3
            }, {
                b: 1,
                e: 0
            }, {
                b: 5,
                e: 11
            }, {
                b: 5,
                e: 10
            }, {
                b: 3,
                e: 9
            }, {
                b: 3,
                e: 8
            }, {
                b: 1,
                e: 4,
                o: 1
            }, {
                b: 0,
                e: 2
            }, {
                b: 2,
                e: 5
            }, {
                b: 2,
                e: 6
            }, {
                b: 2,
                e: 7
            }, {
                b: 7,
                e: 12
            }, {
                b: 12,
                e: 15
            }, {
                b: 7,
                e: 13
            }, {
                b: 7,
                e: 14
            }]
        }
    });
    f.templates.push({
        name: "Talose \x3ci\x3ePyranose Form\x3c/i\x3e",
        data: {
            a: [{
                    x: -36.6654,
                    y: -9.7292
                }, {
                    x: -22.0845,
                    y: 15.5237
                }, {
                    x: -54.1679,
                    y: -.0514,
                    l: "H"
                }, {
                    x: -36.6654,
                    y: -29.7292,
                    l: "O"
                }, {
                    x: -8.6254,
                    y: -2.3409
                }, {
                    x: -41.6882,
                    y: 11.5623,
                    l: "O"
                }, {
                    x: -22.0845,
                    y: 35.5237,
                    l: "H"
                }, {
                    x: 6.1279,
                    y: 8.1324
                }, {
                    x: 19.5899,
                    y: -9.7292,
                    l: "O"
                },
                {
                    x: -8.6254,
                    y: 24.8818,
                    l: "H"
                }, {
                    x: -23.6658,
                    y: -15.5237
                }, {
                    x: 34.1679,
                    y: 15.5237
                }, {
                    x: 20.3041,
                    y: 22.2404,
                    l: "H"
                }, {
                    x: 6.1279,
                    y: -11.8676,
                    l: "O"
                }, {
                    x: -23.6658,
                    y: -35.5237,
                    l: "O"
                }, {
                    x: 54.1679,
                    y: 15.5237,
                    l: "O"
                }
            ],
            b: [{
                b: 0,
                e: 1
            }, {
                b: 4,
                e: 0
            }, {
                b: 8,
                e: 4
            }, {
                b: 11,
                e: 7
            }, {
                b: 11,
                e: 8
            }, {
                b: 4,
                e: 9
            }, {
                b: 7,
                e: 13
            }, {
                b: 7,
                e: 12
            }, {
                b: 4,
                e: 10
            }, {
                b: 10,
                e: 14
            }, {
                b: 0,
                e: 3
            }, {
                b: 0,
                e: 2
            }, {
                b: 1,
                e: 6
            }, {
                b: 1,
                e: 5
            }, {
                b: 1,
                e: 7,
                o: 1
            }, {
                b: 11,
                e: 15,
                o: 1
            }]
        }
    });
    p.push(f);
    f = {
        name: "Sugars (Other Monosaccharides)",
        templates: []
    };
    f.templates.push({
        name: "Glyceraldehyde \x3ci\x3eFisher Projection\x3c/i\x3e",
        data: {
            a: [{
                x: 0,
                y: 0
            }, {
                x: 0,
                y: -20,
                l: "CHO"
            }, {
                x: 0,
                y: 20,
                l: "CH2OH"
            }, {
                x: -20,
                y: 0,
                l: "H"
            }, {
                x: 20,
                y: 0,
                l: "O"
            }],
            b: [{
                b: 0,
                e: 1
            }, {
                b: 0,
                e: 2
            }, {
                b: 0,
                e: 3
            }, {
                b: 0,
                e: 4
            }]
        }
    });
    f.templates.push({
        name: "Erythrose \x3ci\x3eFisher Projection\x3c/i\x3e",
        data: {
            a: [{
                x: 0,
                y: -30,
                l: "CHO"
            }, {
                x: 0,
                y: -10
            }, {
                x: 20,
                y: -10,
                l: "O"
            }, {
                x: 0,
                y: 10
            }, {
                x: -20,
                y: -10,
                l: "H"
            }, {
                x: 20,
                y: 10,
                l: "O"
            }, {
                x: 0,
                y: 30,
                l: "CH2OH"
            }, {
                x: -20,
                y: 10,
                l: "H"
            }],
            b: [{
                b: 0,
                e: 1
            }, {
                b: 1,
                e: 3
            }, {
                b: 3,
                e: 6
            }, {
                b: 3,
                e: 5
            }, {
                b: 1,
                e: 2
            }, {
                b: 1,
                e: 4
            }, {
                b: 3,
                e: 7
            }]
        }
    });
    f.templates.push({
        name: "Threose \x3ci\x3eFisher Projection\x3c/i\x3e",
        data: {
            a: [{
                x: 0,
                y: -30,
                l: "CHO"
            }, {
                x: 0,
                y: -10
            }, {
                x: 0,
                y: 10
            }, {
                x: 20,
                y: -10,
                l: "H"
            }, {
                x: -20,
                y: -10,
                l: "O"
            }, {
                x: -20,
                y: 10,
                l: "H"
            }, {
                x: 20,
                y: 10,
                l: "O"
            }, {
                x: 0,
                y: 30,
                l: "CH2OH"
            }],
            b: [{
                b: 0,
                e: 1
            }, {
                b: 1,
                e: 2
            }, {
                b: 2,
                e: 7
            }, {
                b: 2,
                e: 6
            }, {
                b: 1,
                e: 3
            }, {
                b: 1,
                e: 4
            }, {
                b: 2,
                e: 5
            }]
        }
    });
    f.templates.push({
        name: "Ribose \x3ci\x3eFisher Projection\x3c/i\x3e",
        data: {
            a: [{
                x: 0,
                y: -20
            }, {
                x: 20,
                y: -20,
                l: "O"
            }, {
                x: 0,
                y: 0
            }, {
                x: 0,
                y: -40,
                l: "CHO"
            }, {
                x: -20,
                y: -20,
                l: "H"
            }, {
                x: 20,
                y: 0,
                l: "O"
            }, {
                x: -20,
                y: 0,
                l: "H"
            }, {
                x: 0,
                y: 20
            }, {
                x: 0,
                y: 40,
                l: "CH2OH"
            }, {
                x: 20,
                y: 20,
                l: "O"
            }, {
                x: -20,
                y: 20,
                l: "H"
            }],
            b: [{
                    b: 0,
                    e: 3
                },
                {
                    b: 0,
                    e: 2
                }, {
                    b: 2,
                    e: 7
                }, {
                    b: 7,
                    e: 8
                }, {
                    b: 0,
                    e: 4
                }, {
                    b: 0,
                    e: 1
                }, {
                    b: 2,
                    e: 6
                }, {
                    b: 2,
                    e: 5
                }, {
                    b: 7,
                    e: 10
                }, {
                    b: 7,
                    e: 9
                }
            ]
        }
    });
    f.templates.push({
        name: "Arabinose \x3ci\x3eFisher Projection\x3c/i\x3e",
        data: {
            a: [{
                x: 0,
                y: -20
            }, {
                x: 0,
                y: -40,
                l: "CHO"
            }, {
                x: -20,
                y: -20,
                l: "O"
            }, {
                x: 0,
                y: 0
            }, {
                x: 20,
                y: -20,
                l: "H"
            }, {
                x: -20,
                y: 0,
                l: "H"
            }, {
                x: 20,
                y: 0,
                l: "O"
            }, {
                x: 0,
                y: 20
            }, {
                x: 0,
                y: 40,
                l: "CH2OH"
            }, {
                x: -20,
                y: 20,
                l: "H"
            }, {
                x: 20,
                y: 20,
                l: "O"
            }],
            b: [{
                b: 0,
                e: 1
            }, {
                b: 0,
                e: 3
            }, {
                b: 3,
                e: 7
            }, {
                b: 7,
                e: 8
            }, {
                b: 0,
                e: 2
            }, {
                b: 0,
                e: 4
            }, {
                b: 3,
                e: 5
            }, {
                b: 3,
                e: 6
            }, {
                b: 7,
                e: 9
            }, {
                b: 7,
                e: 10
            }]
        }
    });
    f.templates.push({
        name: "Xylose \x3ci\x3eFisher Projection\x3c/i\x3e",
        data: {
            a: [{
                x: 0,
                y: -20
            }, {
                x: 0,
                y: -40,
                l: "CHO"
            }, {
                x: 0,
                y: 0
            }, {
                x: -20,
                y: -20,
                l: "H"
            }, {
                x: 20,
                y: -20,
                l: "O"
            }, {
                x: 20,
                y: 0,
                l: "H"
            }, {
                x: 0,
                y: 20
            }, {
                x: -20,
                y: 0,
                l: "O"
            }, {
                x: 20,
                y: 20,
                l: "O"
            }, {
                x: -20,
                y: 20,
                l: "H"
            }, {
                x: 0,
                y: 40,
                l: "CH2OH"
            }],
            b: [{
                b: 0,
                e: 1
            }, {
                b: 0,
                e: 2
            }, {
                b: 2,
                e: 6
            }, {
                b: 6,
                e: 10
            }, {
                b: 0,
                e: 3
            }, {
                b: 0,
                e: 4
            }, {
                b: 2,
                e: 7
            }, {
                b: 2,
                e: 5
            }, {
                b: 6,
                e: 9
            }, {
                b: 6,
                e: 8
            }]
        }
    });
    f.templates.push({
        name: "Lyxose \x3ci\x3eFisher Projection\x3c/i\x3e",
        data: {
            a: [{
                x: 0,
                y: -20
            }, {
                x: -20,
                y: -20,
                l: "O"
            }, {
                x: 0,
                y: -40,
                l: "CHO"
            }, {
                x: 20,
                y: -20,
                l: "H"
            }, {
                x: 0,
                y: 0
            }, {
                x: 20,
                y: 0,
                l: "H"
            }, {
                x: 0,
                y: 20
            }, {
                x: -20,
                y: 0,
                l: "O"
            }, {
                x: 20,
                y: 20,
                l: "O"
            }, {
                x: -20,
                y: 20,
                l: "H"
            }, {
                x: 0,
                y: 40,
                l: "CH2OH"
            }],
            b: [{
                b: 0,
                e: 2
            }, {
                b: 0,
                e: 4
            }, {
                b: 4,
                e: 6
            }, {
                b: 6,
                e: 10
            }, {
                b: 0,
                e: 1
            }, {
                b: 0,
                e: 3
            }, {
                b: 4,
                e: 7
            }, {
                b: 4,
                e: 5
            }, {
                b: 6,
                e: 9
            }, {
                b: 6,
                e: 8
            }]
        }
    });
    p.push(f);
    f = {
        name: "Nucleotides",
        templates: []
    };
    f.templates.push({
        name: "Adenine",
        data: {
            a: [{
                x: -32.709,
                y: 10
            }, {
                x: -20.9532,
                y: 26.1804,
                l: "N"
            }, {
                x: -20.9532,
                y: -6.1803,
                l: "N"
            }, {
                x: -1.9321,
                y: 20
            }, {
                x: -1.9321,
                y: 0
            }, {
                x: 15.3884,
                y: 30.0001,
                l: "N"
            }, {
                x: 15.3884,
                y: -10
            }, {
                x: 32.709,
                y: 20
            }, {
                x: 15.3884,
                y: -30,
                l: "N"
            }, {
                x: 32.709,
                y: 0,
                l: "N"
            }],
            b: [{
                    b: 0,
                    e: 1
                }, {
                    b: 1,
                    e: 3
                },
                {
                    b: 3,
                    e: 4,
                    o: 2
                }, {
                    b: 4,
                    e: 2
                }, {
                    b: 2,
                    e: 0,
                    o: 2
                }, {
                    b: 3,
                    e: 5
                }, {
                    b: 5,
                    e: 7,
                    o: 2
                }, {
                    b: 7,
                    e: 9
                }, {
                    b: 9,
                    e: 6,
                    o: 2
                }, {
                    b: 6,
                    e: 4
                }, {
                    b: 6,
                    e: 8
                }
            ]
        }
    });
    f.templates.push({
        name: "Guanine",
        data: {
            a: [{
                x: -41.3692,
                y: 10
            }, {
                x: -29.6135,
                y: -6.1804,
                l: "N"
            }, {
                x: -29.6135,
                y: 26.1803,
                l: "N"
            }, {
                x: -10.5924,
                y: -0
            }, {
                x: -10.5924,
                y: 20
            }, {
                x: 6.7282,
                y: -10.0001
            }, {
                x: 6.7282,
                y: 30,
                l: "N"
            }, {
                x: 6.7282,
                y: -30,
                l: "O"
            }, {
                x: 24.0487,
                y: -0,
                l: "N"
            }, {
                x: 24.0487,
                y: 20
            }, {
                x: 41.3692,
                y: 30,
                l: "N"
            }],
            b: [{
                b: 0,
                e: 2
            }, {
                b: 2,
                e: 4
            }, {
                b: 4,
                e: 3,
                o: 2
            }, {
                b: 3,
                e: 1
            }, {
                b: 1,
                e: 0,
                o: 2
            }, {
                b: 4,
                e: 6
            }, {
                b: 6,
                e: 9,
                o: 2
            }, {
                b: 9,
                e: 8
            }, {
                b: 8,
                e: 5
            }, {
                b: 5,
                e: 3
            }, {
                b: 5,
                e: 7,
                o: 2
            }, {
                b: 9,
                e: 10
            }]
        }
    });
    f.templates.push({
        name: "Cytosine",
        data: {
            a: [{
                x: -8.6603,
                y: -10
            }, {
                x: -8.6603,
                y: -30,
                l: "N"
            }, {
                x: -25.9808,
                y: 0
            }, {
                x: 8.6603,
                y: 0,
                l: "N"
            }, {
                x: -25.9808,
                y: 20
            }, {
                x: 8.6603,
                y: 20
            }, {
                x: -8.6603,
                y: 30,
                l: "N"
            }, {
                x: 25.9808,
                y: 30,
                l: "O"
            }],
            b: [{
                b: 0,
                e: 2
            }, {
                b: 2,
                e: 4,
                o: 2
            }, {
                b: 4,
                e: 6
            }, {
                b: 6,
                e: 5
            }, {
                b: 5,
                e: 3
            }, {
                b: 3,
                e: 0,
                o: 2
            }, {
                b: 5,
                e: 7,
                o: 2
            }, {
                b: 0,
                e: 1
            }]
        }
    });
    f.templates.push({
        name: "Thymine",
        data: {
            a: [{
                    x: 0,
                    y: -10
                }, {
                    x: 17.3205,
                    y: 0,
                    l: "N"
                }, {
                    x: 0,
                    y: -30,
                    l: "O"
                }, {
                    x: -17.3205,
                    y: 0
                }, {
                    x: 17.3205,
                    y: 20
                }, {
                    x: -17.3205,
                    y: 20
                }, {
                    x: -34.641,
                    y: -10
                },
                {
                    x: 34.641,
                    y: 30,
                    l: "O"
                }, {
                    x: 0,
                    y: 30,
                    l: "N"
                }
            ],
            b: [{
                b: 0,
                e: 3
            }, {
                b: 3,
                e: 5,
                o: 2
            }, {
                b: 5,
                e: 8
            }, {
                b: 8,
                e: 4
            }, {
                b: 4,
                e: 1
            }, {
                b: 1,
                e: 0
            }, {
                b: 0,
                e: 2,
                o: 2
            }, {
                b: 3,
                e: 6
            }, {
                b: 4,
                e: 7,
                o: 2
            }]
        }
    });
    f.templates.push({
        name: "Uracil",
        data: {
            a: [{
                x: -8.6603,
                y: -10
            }, {
                x: -25.9808,
                y: 0
            }, {
                x: -8.6603,
                y: -30,
                l: "O"
            }, {
                x: 8.6603,
                y: 0,
                l: "N"
            }, {
                x: -25.9808,
                y: 20
            }, {
                x: 8.6603,
                y: 20
            }, {
                x: -8.6603,
                y: 30,
                l: "N"
            }, {
                x: 25.9808,
                y: 30,
                l: "O"
            }],
            b: [{
                b: 0,
                e: 1
            }, {
                b: 1,
                e: 4,
                o: 2
            }, {
                b: 4,
                e: 6
            }, {
                b: 6,
                e: 5
            }, {
                b: 5,
                e: 3
            }, {
                b: 3,
                e: 0
            }, {
                b: 0,
                e: 2,
                o: 2
            }, {
                b: 5,
                e: 7,
                o: 2
            }]
        }
    });
    f.templates.push({
        name: "Ribonucleoside",
        data: {
            a: [{
                x: -14.2796,
                y: -14.9551
            }, {
                c: -1,
                x: -34.2796,
                y: -14.9551,
                l: "O"
            }, {
                x: -14.2796,
                y: 5.0449
            }, {
                x: 9.5513,
                y: -2.7359,
                l: "O"
            }, {
                x: -5.177,
                y: 17.6345
            }, {
                x: 33.3822,
                y: 5.045
            }, {
                x: 24.2796,
                y: 17.6345
            }, {
                x: -15.177,
                y: 34.955,
                l: "O"
            }, {
                x: 33.3822,
                y: -34.955,
                l: "N"
            }, {
                x: 34.2796,
                y: 34.955,
                l: "O"
            }],
            b: [{
                b: 3,
                e: 2
            }, {
                b: 2,
                e: 4
            }, {
                b: 4,
                e: 6,
                o: 1
            }, {
                b: 5,
                e: 6
            }, {
                b: 5,
                e: 3
            }, {
                b: 4,
                e: 7
            }, {
                b: 5,
                e: 8
            }, {
                b: 2,
                e: 0
            }, {
                b: 0,
                e: 1
            }, {
                b: 6,
                e: 9
            }]
        }
    });
    f.templates.push({
        name: "Ribonucleoside Monophosphate",
        data: {
            a: [{
                x: 5.7204,
                y: -14.955
            }, {
                x: -14.2796,
                y: -14.955,
                l: "O"
            }, {
                x: 5.7204,
                y: 5.045
            }, {
                x: -34.2796,
                y: -14.955,
                l: "P"
            }, {
                x: 14.823,
                y: 17.6345
            }, {
                x: 29.5513,
                y: -2.7358,
                l: "O"
            }, {
                c: -1,
                x: -54.2796,
                y: -14.9551,
                l: "O"
            }, {
                x: -34.2796,
                y: -34.955,
                l: "O"
            }, {
                c: -1,
                x: -34.2796,
                y: 5.045,
                l: "O"
            }, {
                x: 4.823,
                y: 34.955,
                l: "O"
            }, {
                x: 44.2796,
                y: 17.6345
            }, {
                x: 53.3822,
                y: 5.045
            }, {
                x: 54.2796,
                y: 34.955,
                l: "O"
            }, {
                x: 53.3822,
                y: -34.955,
                l: "N"
            }],
            b: [{
                b: 5,
                e: 2
            }, {
                b: 2,
                e: 4
            }, {
                b: 4,
                e: 10,
                o: 1
            }, {
                b: 11,
                e: 10
            }, {
                b: 11,
                e: 5
            }, {
                b: 4,
                e: 9
            }, {
                b: 11,
                e: 13
            }, {
                b: 2,
                e: 0
            }, {
                b: 0,
                e: 1
            }, {
                b: 1,
                e: 3
            }, {
                b: 3,
                e: 6
            }, {
                b: 3,
                e: 7,
                o: 2
            }, {
                b: 3,
                e: 8
            }, {
                b: 10,
                e: 12
            }]
        }
    });
    f.templates.push({
        name: "Ribonucleoside Diphosphate",
        data: {
            a: [{
                x: 25.7204,
                y: -14.955
            }, {
                x: 5.7204,
                y: -14.955,
                l: "O"
            }, {
                x: 25.7204,
                y: 5.045
            }, {
                x: -14.2796,
                y: -14.955,
                l: "P"
            }, {
                x: 49.5513,
                y: -2.7358,
                l: "O"
            }, {
                x: 34.823,
                y: 17.6345
            }, {
                c: -1,
                x: -14.2796,
                y: 5.045,
                l: "O"
            }, {
                x: -14.2796,
                y: -34.955,
                l: "O"
            }, {
                x: -34.2796,
                y: -14.955,
                l: "O"
            }, {
                x: 73.3822,
                y: 5.045
            }, {
                x: 64.2796,
                y: 17.6345
            }, {
                x: 24.823,
                y: 34.955,
                l: "O"
            }, {
                x: -54.2796,
                y: -14.955,
                l: "P"
            }, {
                x: 73.3822,
                y: -34.955,
                l: "N"
            }, {
                x: 74.2796,
                y: 34.9551,
                l: "O"
            }, {
                c: -1,
                x: -54.2796,
                y: 5.045,
                l: "O"
            }, {
                x: -54.2796,
                y: -34.955,
                l: "O"
            }, {
                c: -1,
                x: -74.2796,
                y: -14.955,
                l: "O"
            }],
            b: [{
                b: 4,
                e: 2
            }, {
                b: 2,
                e: 5
            }, {
                b: 5,
                e: 10,
                o: 1
            }, {
                b: 9,
                e: 10
            }, {
                b: 9,
                e: 4
            }, {
                b: 5,
                e: 11
            }, {
                b: 9,
                e: 13
            }, {
                b: 2,
                e: 0
            }, {
                b: 0,
                e: 1
            }, {
                b: 1,
                e: 3
            }, {
                b: 3,
                e: 8
            }, {
                b: 3,
                e: 7,
                o: 2
            }, {
                b: 3,
                e: 6
            }, {
                b: 10,
                e: 14
            }, {
                b: 8,
                e: 12
            }, {
                b: 12,
                e: 17
            }, {
                b: 12,
                e: 16,
                o: 2
            }, {
                b: 12,
                e: 15
            }]
        }
    });
    f.templates.push({
        name: "Ribonucleoside Triphosphate",
        data: {
            a: [{
                x: 45.7204,
                y: -14.955
            }, {
                x: 45.7204,
                y: 5.045
            }, {
                x: 25.7204,
                y: -14.955,
                l: "O"
            }, {
                x: 54.823,
                y: 17.6345
            }, {
                x: 69.5513,
                y: -2.7358,
                l: "O"
            }, {
                x: 5.7204,
                y: -14.955,
                l: "P"
            }, {
                x: 44.823,
                y: 34.955,
                l: "O"
            }, {
                x: 84.2796,
                y: 17.6345
            }, {
                x: 93.3822,
                y: 5.045
            }, {
                c: -1,
                x: 5.7204,
                y: 5.045,
                l: "O"
            }, {
                x: -14.2796,
                y: -14.955,
                l: "O"
            }, {
                x: 5.7204,
                y: -34.955,
                l: "O"
            }, {
                x: 94.2796,
                y: 34.9551,
                l: "O"
            }, {
                x: 93.3822,
                y: -34.955,
                l: "N"
            }, {
                x: -34.2796,
                y: -14.955,
                l: "P"
            }, {
                c: -1,
                x: -34.2796,
                y: 5.045,
                l: "O"
            }, {
                x: -34.2796,
                y: -34.955,
                l: "O"
            }, {
                x: -54.2796,
                y: -14.955,
                l: "O"
            }, {
                x: -74.2796,
                y: -14.955,
                l: "P"
            }, {
                x: -74.2796,
                y: -34.955,
                l: "O"
            }, {
                c: -1,
                x: -94.2796,
                y: -14.955,
                l: "O"
            }, {
                c: -1,
                x: -74.2796,
                y: 5.045,
                l: "O"
            }],
            b: [{
                b: 4,
                e: 1
            }, {
                b: 1,
                e: 3
            }, {
                b: 3,
                e: 7,
                o: 1
            }, {
                b: 8,
                e: 7
            }, {
                b: 8,
                e: 4
            }, {
                b: 3,
                e: 6
            }, {
                b: 8,
                e: 13
            }, {
                b: 1,
                e: 0
            }, {
                b: 0,
                e: 2
            }, {
                b: 2,
                e: 5
            }, {
                b: 5,
                e: 10
            }, {
                b: 5,
                e: 11,
                o: 2
            }, {
                b: 5,
                e: 9
            }, {
                b: 7,
                e: 12
            }, {
                b: 10,
                e: 14
            }, {
                b: 14,
                e: 17
            }, {
                b: 14,
                e: 16,
                o: 2
            }, {
                b: 14,
                e: 15
            }, {
                b: 17,
                e: 18
            }, {
                b: 18,
                e: 20
            }, {
                b: 18,
                e: 19,
                o: 2
            }, {
                b: 18,
                e: 21
            }]
        }
    });
    f.templates.push({
        name: "Ribonucleotide chain form",
        data: {
            a: [{
                x: -13.8309,
                y: -36.2948
            }, {
                x: -33.8309,
                y: -36.2948,
                l: "O"
            }, {
                x: -13.8309,
                y: -16.2948
            }, {
                x: 10,
                y: -24.0756,
                l: "O"
            }, {
                x: -4.7283,
                y: -3.7052
            }, {
                x: 33.8309,
                y: -16.2948
            }, {
                x: 24.7283,
                y: -3.7052
            }, {
                x: -4.7283,
                y: 16.2948,
                l: "O"
            }, {
                x: 33.8309,
                y: -56.2948,
                l: "N"
            }, {
                x: 24.7283,
                y: 16.2948,
                l: "O"
            }, {
                x: -4.7283,
                y: 36.2948,
                l: "P"
            }, {
                c: -1,
                x: -4.7283,
                y: 56.2948,
                l: "O"
            }, {
                c: -1,
                x: 15.2717,
                y: 36.2948,
                l: "O"
            }, {
                x: -24.7283,
                y: 36.2948,
                l: "O"
            }],
            b: [{
                b: 3,
                e: 2
            }, {
                b: 2,
                e: 4
            }, {
                b: 4,
                e: 6,
                o: 1
            }, {
                b: 5,
                e: 6
            }, {
                b: 5,
                e: 3
            }, {
                b: 4,
                e: 7
            }, {
                b: 5,
                e: 8
            }, {
                b: 2,
                e: 0
            }, {
                b: 0,
                e: 1
            }, {
                b: 6,
                e: 9
            }, {
                b: 7,
                e: 10
            }, {
                b: 10,
                e: 12
            }, {
                b: 10,
                e: 13,
                o: 2
            }, {
                b: 10,
                e: 11
            }]
        }
    });
    f.templates.push({
        name: "Deoxyribonucleoside",
        data: {
            a: [{
                x: -13.8309,
                y: -14.9551
            }, {
                c: -1,
                x: -33.8309,
                y: -14.9551,
                l: "O"
            }, {
                x: -13.8309,
                y: 5.0449
            }, {
                x: 10,
                y: -2.7359,
                l: "O"
            }, {
                x: -4.7283,
                y: 17.6345
            }, {
                x: 33.8309,
                y: 5.045
            }, {
                x: 24.7283,
                y: 17.6345
            }, {
                x: -14.7283,
                y: 34.955,
                l: "O"
            }, {
                x: 33.8309,
                y: -34.955,
                l: "N"
            }],
            b: [{
                    b: 3,
                    e: 2
                }, {
                    b: 2,
                    e: 4
                },
                {
                    b: 4,
                    e: 6,
                    o: 1
                }, {
                    b: 5,
                    e: 6
                }, {
                    b: 5,
                    e: 3
                }, {
                    b: 4,
                    e: 7
                }, {
                    b: 5,
                    e: 8
                }, {
                    b: 2,
                    e: 0
                }, {
                    b: 0,
                    e: 1
                }
            ]
        }
    });
    f.templates.push({
        name: "Deoxyribonucleoside Monophosphate",
        data: {
            a: [{
                x: 6.1691,
                y: -14.955
            }, {
                x: -13.8309,
                y: -14.955,
                l: "O"
            }, {
                x: 6.1691,
                y: 5.045
            }, {
                x: -33.8309,
                y: -14.955,
                l: "P"
            }, {
                x: 30,
                y: -2.7358,
                l: "O"
            }, {
                x: 15.2717,
                y: 17.6345
            }, {
                x: -33.8309,
                y: -34.955,
                l: "O"
            }, {
                c: -1,
                x: -53.8309,
                y: -14.9551,
                l: "O"
            }, {
                c: -1,
                x: -33.8309,
                y: 5.045,
                l: "O"
            }, {
                x: 53.8309,
                y: 5.045
            }, {
                x: 5.2717,
                y: 34.955,
                l: "O"
            }, {
                x: 44.7283,
                y: 17.6345
            }, {
                x: 53.8309,
                y: -34.955,
                l: "N"
            }],
            b: [{
                    b: 4,
                    e: 2
                }, {
                    b: 2,
                    e: 5
                },
                {
                    b: 5,
                    e: 11,
                    o: 1
                }, {
                    b: 9,
                    e: 11
                }, {
                    b: 9,
                    e: 4
                }, {
                    b: 5,
                    e: 10
                }, {
                    b: 9,
                    e: 12
                }, {
                    b: 2,
                    e: 0
                }, {
                    b: 0,
                    e: 1
                }, {
                    b: 1,
                    e: 3
                }, {
                    b: 3,
                    e: 7
                }, {
                    b: 3,
                    e: 6,
                    o: 2
                }, {
                    b: 3,
                    e: 8
                }
            ]
        }
    });
    f.templates.push({
        name: "Deoxyribonucleoside Diphosphate",
        data: {
            a: [{
                x: 26.1691,
                y: -14.955
            }, {
                x: 6.1691,
                y: -14.955,
                l: "O"
            }, {
                x: 26.1691,
                y: 5.045
            }, {
                x: -13.8309,
                y: -14.955,
                l: "P"
            }, {
                x: 50,
                y: -2.7358,
                l: "O"
            }, {
                x: 35.2717,
                y: 17.6345
            }, {
                c: -1,
                x: -13.8309,
                y: 5.045,
                l: "O"
            }, {
                x: -13.8309,
                y: -34.955,
                l: "O"
            }, {
                x: -33.8309,
                y: -14.955,
                l: "O"
            }, {
                x: 73.8309,
                y: 5.045
            }, {
                x: 64.7283,
                y: 17.6345
            }, {
                x: 25.2717,
                y: 34.955,
                l: "O"
            }, {
                x: -53.8309,
                y: -14.955,
                l: "P"
            }, {
                x: 73.8309,
                y: -34.955,
                l: "N"
            }, {
                x: -53.8309,
                y: -34.955,
                l: "O"
            }, {
                c: -1,
                x: -53.8309,
                y: 5.045,
                l: "O"
            }, {
                c: -1,
                x: -73.8309,
                y: -14.955,
                l: "O"
            }],
            b: [{
                b: 4,
                e: 2
            }, {
                b: 2,
                e: 5
            }, {
                b: 5,
                e: 10,
                o: 1
            }, {
                b: 9,
                e: 10
            }, {
                b: 9,
                e: 4
            }, {
                b: 5,
                e: 11
            }, {
                b: 9,
                e: 13
            }, {
                b: 2,
                e: 0
            }, {
                b: 0,
                e: 1
            }, {
                b: 1,
                e: 3
            }, {
                b: 3,
                e: 8
            }, {
                b: 3,
                e: 7,
                o: 2
            }, {
                b: 3,
                e: 6
            }, {
                b: 8,
                e: 12
            }, {
                b: 12,
                e: 16
            }, {
                b: 12,
                e: 14,
                o: 2
            }, {
                b: 12,
                e: 15
            }]
        }
    });
    f.templates.push({
        name: "Deoxyribonucleoside Triphosphate",
        data: {
            a: [{
                    x: 46.1691,
                    y: -14.955
                }, {
                    x: 26.1691,
                    y: -14.955,
                    l: "O"
                }, {
                    x: 46.1691,
                    y: 5.045
                }, {
                    x: 6.1691,
                    y: -14.955,
                    l: "P"
                },
                {
                    x: 70,
                    y: -2.7358,
                    l: "O"
                }, {
                    x: 55.2717,
                    y: 17.6345
                }, {
                    c: -1,
                    x: 6.1691,
                    y: 5.045,
                    l: "O"
                }, {
                    x: -13.8309,
                    y: -14.955,
                    l: "O"
                }, {
                    x: 6.1691,
                    y: -34.955,
                    l: "O"
                }, {
                    x: 93.8309,
                    y: 5.045
                }, {
                    x: 84.7283,
                    y: 17.6345
                }, {
                    x: 45.2717,
                    y: 34.955,
                    l: "O"
                }, {
                    x: -33.8309,
                    y: -14.955,
                    l: "P"
                }, {
                    x: 93.8309,
                    y: -34.955,
                    l: "N"
                }, {
                    x: -33.8309,
                    y: -34.955,
                    l: "O"
                }, {
                    c: -1,
                    x: -33.8309,
                    y: 5.045,
                    l: "O"
                }, {
                    x: -53.8309,
                    y: -14.955,
                    l: "O"
                }, {
                    x: -73.8309,
                    y: -14.955,
                    l: "P"
                }, {
                    x: -73.8309,
                    y: -34.955,
                    l: "O"
                }, {
                    c: -1,
                    x: -93.8309,
                    y: -14.955,
                    l: "O"
                }, {
                    c: -1,
                    x: -73.8309,
                    y: 5.045,
                    l: "O"
                }
            ],
            b: [{
                b: 4,
                e: 2
            }, {
                b: 2,
                e: 5
            }, {
                b: 5,
                e: 10,
                o: 1
            }, {
                b: 9,
                e: 10
            }, {
                b: 9,
                e: 4
            }, {
                b: 5,
                e: 11
            }, {
                b: 9,
                e: 13
            }, {
                b: 2,
                e: 0
            }, {
                b: 0,
                e: 1
            }, {
                b: 1,
                e: 3
            }, {
                b: 3,
                e: 7
            }, {
                b: 3,
                e: 8,
                o: 2
            }, {
                b: 3,
                e: 6
            }, {
                b: 7,
                e: 12
            }, {
                b: 12,
                e: 16
            }, {
                b: 12,
                e: 14,
                o: 2
            }, {
                b: 12,
                e: 15
            }, {
                b: 16,
                e: 17
            }, {
                b: 17,
                e: 19
            }, {
                b: 17,
                e: 18,
                o: 2
            }, {
                b: 17,
                e: 20
            }]
        }
    });
    f.templates.push({
        name: "Deoxyribonucleotide chain form",
        data: {
            a: [{
                x: -13.8309,
                y: -36.2948
            }, {
                x: -13.8309,
                y: -16.2948
            }, {
                x: -33.8309,
                y: -36.2948,
                l: "O"
            }, {
                x: 10,
                y: -24.0756,
                l: "O"
            }, {
                x: -4.7284,
                y: -3.7052
            }, {
                x: 33.8309,
                y: -16.2948
            }, {
                x: 24.7283,
                y: -3.7052
            }, {
                x: -4.7284,
                y: 16.2948,
                l: "O"
            }, {
                x: 33.8309,
                y: -56.2948,
                l: "N"
            }, {
                x: -4.7284,
                y: 36.2948,
                l: "P"
            }, {
                x: -24.7284,
                y: 36.2948,
                l: "O"
            }, {
                c: -1,
                x: -4.7284,
                y: 56.2948,
                l: "O"
            }, {
                c: -1,
                x: 15.2716,
                y: 36.2948,
                l: "O"
            }],
            b: [{
                b: 3,
                e: 1
            }, {
                b: 1,
                e: 4
            }, {
                b: 4,
                e: 6,
                o: 1
            }, {
                b: 5,
                e: 6
            }, {
                b: 5,
                e: 3
            }, {
                b: 4,
                e: 7
            }, {
                b: 5,
                e: 8
            }, {
                b: 1,
                e: 0
            }, {
                b: 0,
                e: 2
            }, {
                b: 7,
                e: 9
            }, {
                b: 9,
                e: 12
            }, {
                b: 9,
                e: 10,
                o: 2
            }, {
                b: 9,
                e: 11
            }]
        }
    });
    f.templates.push({
        name: "Phosphate",
        data: {
            a: [{
                x: -18.6602,
                y: -.6571,
                l: "O"
            }, {
                x: 1.3398,
                y: -.6571,
                l: "P"
            }, {
                c: -1,
                x: 8.6025,
                y: 17.9776,
                l: "O"
            }, {
                x: 11.3398,
                y: -17.9776,
                l: "O"
            }, {
                c: -1,
                x: 18.6603,
                y: 9.3429,
                l: "O"
            }],
            b: [{
                b: 0,
                e: 1
            }, {
                b: 1,
                e: 2
            }, {
                b: 1,
                e: 3,
                o: 2
            }, {
                b: 1,
                e: 4
            }]
        }
    });
    p.push(f);
    f = {
        name: "Other",
        templates: []
    };
    f.templates.push({
        name: "Porphine",
        data: {
            a: [{
                    x: 40.7025,
                    y: 17.8205
                }, {
                    x: 20.9488,
                    y: 20.9488,
                    l: "N"
                }, {
                    x: 49.7832,
                    y: -0
                }, {
                    x: 49.7817,
                    y: 35.6396
                }, {
                    x: 17.8205,
                    y: 40.7024
                }, {
                    x: 40.7025,
                    y: -17.8205
                }, {
                    x: 35.6396,
                    y: 49.7817
                }, {
                    x: 0,
                    y: 49.7832
                }, {
                    x: 49.7817,
                    y: -35.6396
                }, {
                    x: 20.9487,
                    y: -20.9487,
                    l: "N"
                }, {
                    x: -17.8205,
                    y: 40.7025
                }, {
                    x: 35.6396,
                    y: -49.7818
                }, {
                    x: 17.8205,
                    y: -40.7025
                }, {
                    x: -35.6396,
                    y: 49.7818
                }, {
                    x: -20.9487,
                    y: 20.9488,
                    l: "N"
                }, {
                    x: -0,
                    y: -49.7832
                },
                {
                    x: -49.7817,
                    y: 35.6396
                }, {
                    x: -40.7025,
                    y: 17.8205
                }, {
                    x: -17.8205,
                    y: -40.7025
                }, {
                    x: -49.7832,
                    y: 0
                }, {
                    x: -35.6396,
                    y: -49.7817
                }, {
                    x: -20.9488,
                    y: -20.9487,
                    l: "N"
                }, {
                    x: -40.7024,
                    y: -17.8205
                }, {
                    x: -49.7818,
                    y: -35.6396
                }
            ],
            b: [{
                b: 0,
                e: 2
            }, {
                b: 2,
                e: 5,
                o: 2
            }, {
                b: 5,
                e: 8
            }, {
                b: 8,
                e: 11,
                o: 2
            }, {
                b: 5,
                e: 9
            }, {
                b: 9,
                e: 12
            }, {
                b: 12,
                e: 11
            }, {
                b: 12,
                e: 15,
                o: 2
            }, {
                b: 0,
                e: 1,
                o: 2
            }, {
                b: 1,
                e: 4
            }, {
                b: 4,
                e: 6
            }, {
                b: 6,
                e: 3,
                o: 2
            }, {
                b: 3,
                e: 0
            }, {
                b: 4,
                e: 7,
                o: 2
            }, {
                b: 7,
                e: 10
            }, {
                b: 10,
                e: 13,
                o: 2
            }, {
                b: 13,
                e: 16
            }, {
                b: 16,
                e: 17,
                o: 2
            }, {
                b: 17,
                e: 19
            }, {
                b: 19,
                e: 22,
                o: 2
            }, {
                b: 22,
                e: 23
            }, {
                b: 23,
                e: 20,
                o: 2
            }, {
                b: 20,
                e: 18
            }, {
                b: 18,
                e: 15
            }, {
                b: 18,
                e: 21,
                o: 2
            }, {
                b: 21,
                e: 22
            }, {
                b: 17,
                e: 14
            }, {
                b: 14,
                e: 10
            }]
        }
    });
    p.push(f);
    return p
}(JSON,
    localStorage);
(function(g, a, p, f) {
    g.Button = function(a, h, d, g) {
        this.id = a;
        this.icon = h;
        this.toggle = !1;
        this.tooltip = d ? d : "";
        this.func = g ? g : f
    };
    g = g.Button.prototype;
    g.getElement = function() {
        return p("#" + this.id)
    };
    g.getLabelElement = function() {
        return this.toggle ? p("#" + this.id + "_label") : f
    };
    g.getSource = function(f) {
        let h = [];
        this.toggle ? (h.push('\x3cinput type\x3d"radio" name\x3d"'), h.push(f), h.push('" id\x3d"'), h.push(this.id), h.push('" title\x3d"'), h.push(this.tooltip), h.push('" /\x3e\x3clabel id\x3d"'), h.push(this.id), h.push('_label" for\x3d"'),
            h.push(this.id), h.push('" style\x3d"'), h.push("box-sizing:border-box;margin-top:0px; margin-bottom:1px; padding:0px; height:28px; width:28px;"), h.push('"\x3e\x3cimg id\x3d"'), h.push(this.id), h.push('_icon" title\x3d"'), h.push(this.tooltip), h.push('" width\x3d"20" height\x3d"20'), this.icon && (h.push('" src\x3d"'), h.push(a.getURI(this.icon))), h.push('"\x3e\x3c/label\x3e')) : (h.push('\x3cbutton type\x3d"button" id\x3d"'), h.push(this.id), h.push('" onclick\x3d"return false;" title\x3d"'), h.push(this.tooltip),
            h.push('" style\x3d"'), h.push("box-sizing:border-box;margin-top:0px; margin-bottom:1px; padding:0px; height:28px; width:28px;"), h.push('"\x3e\x3cimg title\x3d"'), h.push(this.tooltip), h.push('" width\x3d"20" height\x3d"20'), this.icon && (h.push('" src\x3d"'), h.push(a.getURI(this.icon))), h.push('"\x3e\x3c/button\x3e'));
        return h.join("")
    };
    g.setup = function(a) {
        let f = this.getElement();
        this.toggle && !a || f.button();
        f.click(this.func)
    };
    g.disable = function() {
        let a = this.getElement();
        a.mouseout();
        a.button("disable")
    };
    g.enable = function() {
        this.getElement().button("enable")
    };
    g.select = function() {
        let a = this.getElement();
        a.attr("checked", !0);
        a.button("refresh");
        this.toggle && this.getLabelElement().click()
    }
})(ChemDoodle.uis.gui.desktop, ChemDoodle.uis.gui.imageDepot, ChemDoodle.lib.jQuery);
(function(g, a, p) {
    g.ButtonSet = function(a) {
        this.id = a;
        this.buttons = [];
        this.toggle = !0;
        this.columnCount = -1
    };
    p = g.ButtonSet.prototype;
    p.getElement = function() {
        return a("#" + this.id)
    };
    p.getSource = function(a) {
        let f = [];
        if (-1 === this.columnCount) {
            f.push('\x3cspan id\x3d"');
            f.push(this.id);
            f.push('"\x3e');
            for (let h = 0, d = this.buttons.length; h < d; h++) this.toggle && (this.buttons[h].toggle = !0), f.push(this.buttons[h].getSource(a));
            this.dropDown && f.push(this.dropDown.getButtonSource());
            f.push("\x3c/span\x3e");
            this.dropDown &&
                f.push(this.dropDown.getHiddenSource())
        } else {
            f.push('\x3ctable cellspacing\x3d"0" style\x3d"margin:1px -2px 0px 1px;"\x3e');
            let h = 0;
            for (let d = 0, g = this.buttons.length; d < g; d++) this.toggle && (this.buttons[d].toggle = !0), 0 === h && f.push("\x3ctr\x3e"), f.push('\x3ctd style\x3d"padding:0px;"\x3e'), f.push(this.buttons[d].getSource(a)), f.push("\x3c/td\x3e"), h++, h === this.columnCount && (f.push("\x3c/tr\x3e"), h = 0);
            f.push("\x3c/table\x3e")
        }
        return f.join("")
    };
    p.setup = function() {
        -1 === this.columnCount && this.getElement().buttonset();
        for (let a = 0, g = this.buttons.length; a < g; a++) this.buttons[a].setup(-1 !== this.columnCount);
        this.dropDown && this.dropDown.setup()
    };
    p.addDropDown = function(a) {
        this.dropDown = new g.DropDown(this.id + "_dd", a, this.buttons[this.buttons.length - 1])
    };
    p.disable = function() {
        for (let a = 0, g = this.buttons.length; a < g; a++) this.buttons[a].disable()
    };
    p.enable = function() {
        for (let a = 0, g = this.buttons.length; a < g; a++) this.buttons[a].enable()
    }
})(ChemDoodle.uis.gui.desktop, ChemDoodle.lib.jQuery);
(function(g, a, p) {
    g.CheckBox = function(a, g, h, d) {
        this.id = a;
        this.checked = d ? d : !1;
        this.tooltip = g ? g : "";
        this.func = h ? h : p
    };
    g = g.CheckBox.prototype = new g.Button;
    g.getSource = function() {
        let a = [];
        a.push('\x3cinput type\x3d"checkbox" id\x3d"');
        a.push(this.id);
        a.push('" ');
        this.checked && a.push('checked\x3d"" ');
        a.push('\x3e\x3clabel for\x3d"');
        a.push(this.id);
        a.push('"\x3e');
        a.push(this.tooltip);
        a.push("\x3c/label\x3e");
        return a.join("")
    };
    g.setup = function() {
        this.getElement().click(this.func)
    };
    g.check = function() {
        this.checked = !0;
        this.getElement().prop("checked", !0)
    };
    g.uncheck = function() {
        this.checked = !1;
        this.getElement().removeAttr("checked")
    }
})(ChemDoodle.uis.gui.desktop, ChemDoodle.lib.jQuery);
(function(g, a, p, f) {
    g.Dialog = function(a, f, d) {
        this.sketcherid = a;
        this.id = a + f;
        this.title = d ? d : "Information"
    };
    g = g.Dialog.prototype;
    g.buttons = f;
    g.message = f;
    g.afterMessage = f;
    g.includeTextArea = !1;
    g.includeTextField = !1;
    g.getElement = function() {
        return a("#" + this.id)
    };
    g.getTextArea = function() {
        return a("#" + this.id + "_ta")
    };
    g.getTextField = function() {
        return a("#" + this.id + "_tf")
    };
    g.setup = function() {
        let f = [];
        f.push('\x3cdiv style\x3d"font-size:12px;" id\x3d"');
        f.push(this.id);
        f.push('" title\x3d"');
        f.push(this.title);
        f.push('"\x3e');
        this.message && (f.push("\x3cp\x3e"), f.push(this.message), f.push("\x3c/p\x3e"));
        this.includeTextField && (f.push('\x3cinput type\x3d"text" style\x3d"font-family:\'Courier New\';" id\x3d"'), f.push(this.id), f.push('_tf" autofocus\x3e\x3c/input\x3e'));
        this.includeTextArea && (f.push('\x3ctextarea style\x3d"font-family:\'Courier New\';" id\x3d"'), f.push(this.id), f.push('_ta" cols\x3d"55" rows\x3d"10"\x3e\x3c/textarea\x3e'));
        this.afterMessage && (f.push("\x3cp\x3e"), f.push(this.afterMessage), f.push("\x3c/p\x3e"));
        f.push("\x3c/div\x3e");
        p.getElementById(this.sketcherid) ? a("#" + this.sketcherid).before(f.join("")) : p.writeln(f.join(""));
        this.getElement().dialog({
            autoOpen: !1,
            width: 435,
            buttons: this.buttons
        })
    };
    g.open = function() {
        this.getElement().dialog("open")
    }
})(ChemDoodle.uis.gui.desktop, ChemDoodle.lib.jQuery, document);
(function(g, a, p) {
    g.FloatingToolbar = function(a) {
        this.sketcher = a;
        this.components = []
    };
    g = g.FloatingToolbar.prototype;
    g.getElement = function() {
        return a("#" + this.id)
    };
    g.getSource = function(a) {
        let f = [];
        f.push('\x3cdiv id\x3d"');
        f.push(this.sketcher.id);
        f.push('_floating_toolbar" style\x3d"position:absolute;left:-50px;z-index:10;box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19);border:1px #C1C1C1 solid;background:#F5F5F5;padding:2px;"\x3e');
        f.push('\x3cdiv id\x3d"');
        f.push(this.sketcher.id);
        f.push('_floating_toolbar_handle" style\x3d"height:14px;"\x3e\x3cdiv style\x3d"box-sizing:border-box;padding:0px;height:4px;border-top:1px solid #999;border-bottom:1px solid #999;"\x3e');
        f.push("\x3c/div\x3e\x3c/div\x3e");
        for (let h = 0, d = this.components.length; h < d; h++) f.push(this.components[h].getSource(a)), f.push("\x3cbr\x3e");
        f.push("\x3c/div\x3e");
        return f.join("")
    };
    g.setup = function() {
        let f = this;
        a("#" + this.sketcher.id + "_floating_toolbar").draggable({
            handle: "#" + this.sketcher.id + "_floating_toolbar_handle",
            drag: function() {
                f.sketcher.openTray && f.sketcher.openTray.reposition()
            },
            containment: "document"
        });
        for (let a = 0, f = this.components.length; a < f; a++) this.components[a].setup(!0)
    }
})(ChemDoodle.uis.gui.desktop, ChemDoodle.lib.jQuery);
(function(g, a, p, f, m, h, d) {
    let l = function(a, d, f, h, g) {
        let e = ["\x3ctr\x3e"];
        e.push("\x3ctd\x3e"); - 1 === a.indexOf("_elements") && (e.push('\x3cinput type\x3d"checkbox" id\x3d"'), e.push(a), e.push('_include"\x3e'));
        e.push("\x3c/td\x3e");
        e.push("\x3ctd\x3e");
        e.push(d);
        f && (e.push("\x3cbr\x3e(\x3cstrong\x3e"), e.push(f), e.push("\x3c/strong\x3e)"));
        e.push("\x3c/td\x3e");
        e.push('\x3ctd style\x3d"padding-left:20px;padding-right:20px;"\x3e');
        e.push(h);
        g && (1 === g ? (e.push("\x3cbr\x3e"), e.push('\x3cinput type\x3d"text" id\x3d"'),
            e.push(a), e.push('_value"\x3e')) : e.push(g));
        e.push("\x3c/td\x3e");
        e.push('\x3ctd\x3e\x3cinput type\x3d"checkbox" id\x3d"');
        e.push(a);
        e.push('_not"\x3e\x3cbr\x3e\x3cstrong\x3eNOT\x3c/strong\x3e');
        e.push("\x3c/td\x3e");
        e.push("\x3c/tr\x3e");
        return e.join("")
    };
    f.AtomQueryDialog = function(a, d) {
        this.sketcher = a;
        this.id = a.id + d
    };
    f = f.AtomQueryDialog.prototype = new f.Dialog;
    f.title = "Atom Query";
    f.setAtom = function(f) {
        this.a = f;
        let h = f.query;
        h || (h = new a.Query(a.Query.TYPE_ATOM), h.elements.v.push(f.label));
        for (let a =
                0, d = this.periodicTable.cells.length; a < d; a++) this.periodicTable.cells[a].selected = -1 !== h.elements.v.indexOf(this.periodicTable.cells[a].element.symbol);
        this.periodicTable.repaint();
        m("#" + this.id + "_el_any").prop("checked", -1 !== h.elements.v.indexOf("a"));
        m("#" + this.id + "_el_noth").prop("checked", -1 !== h.elements.v.indexOf("r"));
        m("#" + this.id + "_el_het").prop("checked", -1 !== h.elements.v.indexOf("q"));
        m("#" + this.id + "_el_hal").prop("checked", -1 !== h.elements.v.indexOf("x"));
        m("#" + this.id + "_el_met").prop("checked",
            -1 !== h.elements.v.indexOf("m"));
        m("#" + this.id + "_elements_not").prop("checked", h.elements.not);
        m("#" + this.id + "_aromatic_include").prop("checked", h.aromatic !== d);
        m("#" + this.id + "_aromatic_not").prop("checked", h.aromatic !== d && h.aromatic.not);
        m("#" + this.id + "_charge_include").prop("checked", h.charge !== d);
        m("#" + this.id + "_charge_value").val(h.charge ? h.outputRange(h.charge.v) : "");
        m("#" + this.id + "_charge_not").prop("checked", h.charge !== d && h.charge.not);
        m("#" + this.id + "_hydrogens_include").prop("checked", h.hydrogens !==
            d);
        m("#" + this.id + "_hydrogens_value").val(h.hydrogens ? h.outputRange(h.hydrogens.v) : "");
        m("#" + this.id + "_hydrogens_not").prop("checked", h.charge !== d && h.charge.not);
        m("#" + this.id + "_ringCount_include").prop("checked", h.ringCount !== d);
        m("#" + this.id + "_ringCount_value").val(h.ringCount ? h.outputRange(h.ringCount.v) : "");
        m("#" + this.id + "_ringCount_not").prop("checked", h.ringCount !== d && h.ringCount.not);
        m("#" + this.id + "_saturation_include").prop("checked", h.saturation !== d);
        m("#" + this.id + "_saturation_not").prop("checked",
            h.saturation !== d && h.saturation.not);
        m("#" + this.id + "_connectivity_include").prop("checked", h.connectivity !== d);
        m("#" + this.id + "_connectivity_value").val(h.connectivity ? h.outputRange(h.connectivity.v) : "");
        m("#" + this.id + "_connectivity_not").prop("checked", h.connectivity !== d && h.connectivity.not);
        m("#" + this.id + "_connectivityNoH_include").prop("checked", h.connectivityNoH !== d);
        m("#" + this.id + "_connectivityNoH_value").val(h.connectivityNoH ? h.outputRange(h.connectivityNoH.v) : "");
        m("#" + this.id + "_connectivityNoH_not").prop("checked",
            h.connectivityNoH !== d && h.connectivityNoH.not);
        m("#" + this.id + "_chirality_include").prop("checked", h.chirality !== d);
        h.chirality && "R" !== h.chirality.v ? h.chirality && "S" !== h.chirality.v ? h.chirality && "A" !== h.chirality.v || m("#" + this.id + "_chiral_a").prop("checked", !0).button("refresh") : m("#" + this.id + "_chiral_s").prop("checked", !0).button("refresh") : m("#" + this.id + "_chiral_r").prop("checked", !0).button("refresh");
        m("#" + this.id + "_chirality_not").prop("checked", h.chirality !== d && h.chirality.not)
    };
    f.setup = function() {
        let f = [];
        f.push('\x3cdiv style\x3d"font-size:12px;text-align:center;height:300px;overflow-y:scroll;" id\x3d"');
        f.push(this.id);
        f.push('" title\x3d"');
        f.push(this.title);
        f.push('"\x3e');
        f.push("\x3cp\x3eSet the following form to define the atom query.\x3c/p\x3e");
        f.push("\x3ctable\x3e");
        f.push(l(this.id + "_elements", "Identity", d, "Select any number of elements and/or wildcards.", '\x3ccanvas class\x3d"ChemDoodleWebComponent" id\x3d"' + this.id + '_pt"\x3e\x3c/canvas\x3e\x3cbr\x3e\x3cinput type\x3d"checkbox" id\x3d"' +
            this.id + '_el_any"\x3eAny (a)\x3cinput type\x3d"checkbox" id\x3d"' + this.id + '_el_noth"\x3e!Hydrogen (r)\x3cinput type\x3d"checkbox" id\x3d"' + this.id + '_el_het"\x3eHeteroatom (q)\x3cbr\x3e\x3cinput type\x3d"checkbox" id\x3d"' + this.id + '_el_hal"\x3eHalide (x)\x3cinput type\x3d"checkbox" id\x3d"' + this.id + '_el_met"\x3eMetal (m)'));
        f.push('\x3ctr\x3e\x3ctd colspan\x3d"4"\x3e\x3chr style\x3d"width:100%"\x3e\x3c/td\x3e\x3c/tr\x3e');
        f.push(l(this.id + "_aromatic", "Aromatic", "A", "Specifies that the matched atom should be aromatic. Use the NOT modifier to specify not aromatic or anti-aromatic."));
        f.push(l(this.id + "_charge", "Charge", "C", "Defines the allowed charge for the matched atom.", 1));
        f.push(l(this.id + "_hydrogens", "Hydrogens", "H", "Defines the total number of hydrogens attached to the atom, implicit and explicit.", 1));
        f.push(l(this.id + "_ringCount", "Ring Count", "R", "Defines the total number of rings this atom is a member of. (SSSR)", 1));
        f.push(l(this.id + "_saturation", "Saturation", "S", "Specifies that the matched atom should be saturated. Use the NOT modifier to specify unsaturation."));
        f.push(l(this.id + "_connectivity", "Connectivity", "X", "Defines the total number of bonds connected to the atom, including all hydrogens.", 1));
        f.push(l(this.id + "_connectivityNoH", "Connectivity (No H)", "x", "Defines the total number of bonds connected to the atom, excluding all hydrogens.", 1));
        f.push(l(this.id + "_chirality", "Chirality", "@", "Defines the stereochemical configuration of the atom.", '\x3cdiv id\x3d"' + this.id + '_radio"\x3e\x3cinput type\x3d"radio" id\x3d"' + this.id + '_chiral_a" name\x3d"radio"\x3e\x3clabel for\x3d"' +
            this.id + '_chiral_a"\x3eAny (A)\x3c/label\x3e\x3cinput type\x3d"radio" id\x3d"' + this.id + '_chiral_r" name\x3d"radio"\x3e\x3clabel for\x3d"' + this.id + '_chiral_r"\x3eRectus (R)\x3c/label\x3e\x3cinput type\x3d"radio" id\x3d"' + this.id + '_chiral_s" name\x3d"radio"\x3e\x3clabel for\x3d"' + this.id + '_chiral_s"\x3eSinestra (S)\x3c/label\x3e\x3c/div\x3e'));
        f.push("\x3c/table\x3e");
        f.push("\x3c/div\x3e");
        h.getElementById(this.sketcher.id) ? m("#" + this.sketcher.id).before(f.join("")) : h.writeln(f.join(""));
        this.periodicTable =
            new g.PeriodicTableCanvas(this.id + "_pt", 16);
        this.periodicTable.allowMultipleSelections = !0;
        this.periodicTable.drawCell = function(a, d, f) {
            this.hovered === f ? (a.fillStyle = "blue", a.fillRect(f.x, f.y, f.dimension, f.dimension)) : f.selected && (a.fillStyle = "#c10000", a.fillRect(f.x, f.y, f.dimension, f.dimension));
            a.strokeStyle = "black";
            a.strokeRect(f.x, f.y, f.dimension, f.dimension);
            a.font = "10px Sans-serif";
            a.fillStyle = "black";
            a.textAlign = "center";
            a.textBaseline = "middle";
            a.fillText(f.element.symbol, f.x + f.dimension / 2, f.y +
                f.dimension / 2)
        };
        this.periodicTable.repaint();
        let q = this;
        m("#" + this.id + "_radio").buttonset();
        this.getElement().dialog({
            autoOpen: !1,
            width: 500,
            height: 300,
            buttons: {
                Cancel: function() {
                    m(this).dialog("close")
                },
                Remove: function() {
                    q.sketcher.historyManager.pushUndo(new p.ChangeQueryAction(q.a));
                    m(this).dialog("close")
                },
                Set: function() {
                    let d = new a.Query(a.Query.TYPE_ATOM);
                    m("#" + q.id + "_el_any").is(":checked") && d.elements.v.push("a");
                    m("#" + q.id + "_el_noth").is(":checked") && d.elements.v.push("r");
                    m("#" + q.id + "_el_het").is(":checked") &&
                        d.elements.v.push("q");
                    m("#" + q.id + "_el_hal").is(":checked") && d.elements.v.push("x");
                    m("#" + q.id + "_el_met").is(":checked") && d.elements.v.push("m");
                    for (let a = 0, f = q.periodicTable.cells.length; a < f; a++) q.periodicTable.cells[a].selected && d.elements.v.push(q.periodicTable.cells[a].element.symbol);
                    m("#" + q.id + "_elements_not").is(":checked") && (d.elements.not = !0);
                    m("#" + q.id + "_aromatic_include").is(":checked") && (d.aromatic = {
                        v: !0,
                        not: m("#" + q.id + "_aromatic_not").is(":checked")
                    });
                    m("#" + q.id + "_charge_include").is(":checked") &&
                        (d.charge = {
                            v: d.parseRange(m("#" + q.id + "_charge_value").val()),
                            not: m("#" + q.id + "_charge_not").is(":checked")
                        });
                    m("#" + q.id + "_hydrogens_include").is(":checked") && (d.hydrogens = {
                        v: d.parseRange(m("#" + q.id + "_hydrogens_value").val()),
                        not: m("#" + q.id + "_hydrogens_not").is(":checked")
                    });
                    m("#" + q.id + "_ringCount_include").is(":checked") && (d.ringCount = {
                        v: d.parseRange(m("#" + q.id + "_ringCount_value").val()),
                        not: m("#" + q.id + "_ringCount_not").is(":checked")
                    });
                    m("#" + q.id + "_saturation_include").is(":checked") && (d.saturation = {
                        v: !0,
                        not: m("#" + q.id + "_saturation_not").is(":checked")
                    });
                    m("#" + q.id + "_connectivity_include").is(":checked") && (d.connectivity = {
                        v: d.parseRange(m("#" + q.id + "_connectivity_value").val()),
                        not: m("#" + q.id + "_connectivity_not").is(":checked")
                    });
                    m("#" + q.id + "_connectivityNoH_include").is(":checked") && (d.connectivityNoH = {
                        v: d.parseRange(m("#" + q.id + "_connectivityNoH_value").val()),
                        not: m("#" + q.id + "_connectivityNoH_not").is(":checked")
                    });
                    if (m("#" + q.id + "_chirality_include").is(":checked")) {
                        let a = "R";
                        m("#" + q.id + "_chiral_a").is(":checked") ?
                            a = "A" : m("#" + q.id + "_chiral_s").is(":checked") && (a = "S");
                        d.chirality = {
                            v: a,
                            not: m("#" + q.id + "_chirity_not").is(":checked")
                        }
                    }
                    q.sketcher.historyManager.pushUndo(new p.ChangeQueryAction(q.a, d));
                    m(this).dialog("close")
                }
            },
            open: function(a, d) {
                m("#" + q.id).animate({
                    scrollTop: 0
                }, "fast")
            }
        })
    }
})(ChemDoodle, ChemDoodle.structures, ChemDoodle.uis.actions, ChemDoodle.uis.gui.desktop, ChemDoodle.lib.jQuery, document);
(function(g, a, p, f, m, h, d, l) {
    let t = function(a, d, f, h, e) {
        let g = ["\x3ctr\x3e"];
        g.push("\x3ctd\x3e"); - 1 === a.indexOf("_orders") && (g.push('\x3cinput type\x3d"checkbox" id\x3d"'), g.push(a), g.push('_include"\x3e'));
        g.push("\x3c/td\x3e");
        g.push("\x3ctd\x3e");
        g.push(d);
        f && (g.push("\x3cbr\x3e(\x3cstrong\x3e"), g.push(f), g.push("\x3c/strong\x3e)"));
        g.push("\x3c/td\x3e");
        g.push('\x3ctd style\x3d"padding-left:20px;padding-right:20px;"\x3e');
        g.push(h);
        e && (1 === e ? (g.push("\x3cbr\x3e"), g.push('\x3cinput type\x3d"text" id\x3d"'),
            g.push(a), g.push('_value"\x3e')) : g.push(e));
        g.push("\x3c/td\x3e");
        g.push('\x3ctd\x3e\x3cinput type\x3d"checkbox" id\x3d"');
        g.push(a);
        g.push('_not"\x3e\x3cbr\x3e\x3cstrong\x3eNOT\x3c/strong\x3e');
        g.push("\x3c/td\x3e");
        g.push("\x3c/tr\x3e");
        return g.join("")
    };
    f.BondQueryDialog = function(a, d) {
        this.sketcher = a;
        this.id = a.id + d
    };
    g = f.BondQueryDialog.prototype = new f.Dialog;
    g.title = "Bond Query";
    g.setBond = function(d) {
        this.b = d;
        let f = d.query;
        if (!f) switch (f = new a.Query(a.Query.TYPE_BOND), d.bondOrder) {
            case 0:
                f.orders.v.push("0");
                break;
            case .5:
                f.orders.v.push("h");
                break;
            case 1:
                f.orders.v.push("1");
                break;
            case 1.5:
                f.orders.v.push("r");
                break;
            case 2:
                f.orders.v.push("2");
                break;
            case 3:
                f.orders.v.push("3")
        }
        h("#" + this.id + "_type_0").prop("checked", -1 !== f.orders.v.indexOf("0")).button("refresh");
        h("#" + this.id + "_type_1").prop("checked", -1 !== f.orders.v.indexOf("1")).button("refresh");
        h("#" + this.id + "_type_2").prop("checked", -1 !== f.orders.v.indexOf("2")).button("refresh");
        h("#" + this.id + "_type_3").prop("checked", -1 !== f.orders.v.indexOf("3")).button("refresh");
        h("#" + this.id + "_type_4").prop("checked", -1 !== f.orders.v.indexOf("4")).button("refresh");
        h("#" + this.id + "_type_5").prop("checked", -1 !== f.orders.v.indexOf("5")).button("refresh");
        h("#" + this.id + "_type_6").prop("checked", -1 !== f.orders.v.indexOf("6")).button("refresh");
        h("#" + this.id + "_type_h").prop("checked", -1 !== f.orders.v.indexOf("h")).button("refresh");
        h("#" + this.id + "_type_r").prop("checked", -1 !== f.orders.v.indexOf("r")).button("refresh");
        h("#" + this.id + "_type_a").prop("checked", -1 !== f.orders.v.indexOf("a")).button("refresh");
        h("#" + this.id + "_orders_not").prop("checked", f.orders.not);
        h("#" + this.id + "_aromatic_include").prop("checked", f.aromatic !== l);
        h("#" + this.id + "_aromatic_not").prop("checked", f.aromatic !== l && f.aromatic.not);
        h("#" + this.id + "_ringCount_include").prop("checked", f.ringCount !== l);
        h("#" + this.id + "_ringCount_value").val(f.ringCount ? f.outputRange(f.ringCount.v) : "");
        h("#" + this.id + "_ringCount_not").prop("checked", f.ringCount !== l && f.ringCount.not);
        h("#" + this.id + "_stereo_include").prop("checked", f.stereo !== l);
        f.stereo &&
            "E" !== f.stereo.v ? f.stereo && "Z" !== f.stereo.v ? f.stereo && "A" !== f.stereo.v || h("#" + this.id + "_stereo_a").prop("checked", !0).button("refresh") : h("#" + this.id + "_stereo_z").prop("checked", !0).button("refresh") : h("#" + this.id + "_stereo_e").prop("checked", !0).button("refresh");
        h("#" + this.id + "_stereo_not").prop("checked", f.stereo !== l && f.stereo.not)
    };
    g.setup = function() {
        let f = [];
        f.push('\x3cdiv style\x3d"font-size:12px;text-align:center;height:300px;overflow-y:scroll;" id\x3d"');
        f.push(this.id);
        f.push('" title\x3d"');
        f.push(this.title);
        f.push('"\x3e');
        f.push("\x3cp\x3eSet the following form to define the bond query.\x3c/p\x3e");
        f.push("\x3ctable\x3e");
        f.push(t(this.id + "_orders", "Identity", l, "Select any number of bond types.", '\x3cdiv id\x3d"' + this.id + '_radioTypes"\x3e\x3cinput type\x3d"checkbox" id\x3d"' + this.id + '_type_0"\x3e\x3clabel for\x3d"' + this.id + '_type_0"\x3e\x3cimg width\x3d"20" height\x3d"20" src\x3d"' + m.getURI(m.BOND_ZERO) + '" /\x3e\x3c/label\x3e\x3cinput type\x3d"checkbox" id\x3d"' + this.id + '_type_1"\x3e\x3clabel for\x3d"' +
            this.id + '_type_1"\x3e\x3cimg width\x3d"20" height\x3d"20" src\x3d"' + m.getURI(m.BOND_SINGLE) + '" /\x3e\x3c/label\x3e\x3cinput type\x3d"checkbox" id\x3d"' + this.id + '_type_2"\x3e\x3clabel for\x3d"' + this.id + '_type_2"\x3e\x3cimg width\x3d"20" height\x3d"20" src\x3d"' + m.getURI(m.BOND_DOUBLE) + '" /\x3e\x3c/label\x3e\x3cinput type\x3d"checkbox" id\x3d"' + this.id + '_type_3"\x3e\x3clabel for\x3d"' + this.id + '_type_3"\x3e\x3cimg width\x3d"20" height\x3d"20" src\x3d"' + m.getURI(m.BOND_TRIPLE) + '" /\x3e\x3c/label\x3e\x3cinput type\x3d"checkbox" id\x3d"' +
            this.id + '_type_4"\x3e\x3clabel for\x3d"' + this.id + '_type_4"\x3e\x3cimg width\x3d"20" height\x3d"20" src\x3d"' + m.getURI(m.BOND_QUADRUPLE) + '" /\x3e\x3c/label\x3e\x3cinput type\x3d"checkbox" id\x3d"' + this.id + '_type_5"\x3e\x3clabel for\x3d"' + this.id + '_type_5"\x3e\x3cimg width\x3d"20" height\x3d"20" src\x3d"' + m.getURI(m.BOND_QUINTUPLE) + '" /\x3e\x3c/label\x3e\x3cinput type\x3d"checkbox" id\x3d"' + this.id + '_type_6"\x3e\x3clabel for\x3d"' + this.id + '_type_6"\x3e\x3cimg width\x3d"20" height\x3d"20" src\x3d"' +
            m.getURI(m.BOND_SEXTUPLE) + '" /\x3e\x3c/label\x3e\x3cinput type\x3d"checkbox" id\x3d"' + this.id + '_type_h"\x3e\x3clabel for\x3d"' + this.id + '_type_h"\x3e\x3cimg width\x3d"20" height\x3d"20" src\x3d"' + m.getURI(m.BOND_HALF) + '" /\x3e\x3c/label\x3e\x3cinput type\x3d"checkbox" id\x3d"' + this.id + '_type_r"\x3e\x3clabel for\x3d"' + this.id + '_type_r"\x3e\x3cimg width\x3d"20" height\x3d"20" src\x3d"' + m.getURI(m.BOND_RESONANCE) + '" /\x3e\x3c/label\x3e\x3cinput type\x3d"checkbox" id\x3d"' + this.id + '_type_a"\x3e\x3clabel for\x3d"' +
            this.id + '_type_a"\x3e\x3cimg width\x3d"20" height\x3d"20" src\x3d"' + m.getURI(m.BOND_ANY) + '" /\x3e\x3c/label\x3e\x3c/div\x3e'));
        f.push('\x3ctr\x3e\x3ctd colspan\x3d"4"\x3e\x3chr style\x3d"width:100%"\x3e\x3c/td\x3e\x3c/tr\x3e');
        f.push(t(this.id + "_aromatic", "Aromatic", "A", "Specifies that the matched bond should be aromatic. Use the NOT modifier to specify not aromatic or anti-aromatic."));
        f.push(t(this.id + "_ringCount", "Ring Count", "R", "Defines the total number of rings this bond is a member of. (SSSR)",
            1));
        f.push(t(this.id + "_stereo", "Stereochemistry", "@", "Defines the stereochemical configuration of the bond.", '\x3cdiv id\x3d"' + this.id + '_radio"\x3e\x3cinput type\x3d"radio" id\x3d"' + this.id + '_stereo_a" name\x3d"radio"\x3e\x3clabel for\x3d"' + this.id + '_stereo_a"\x3eAny (A)\x3c/label\x3e\x3cinput type\x3d"radio" id\x3d"' + this.id + '_stereo_e" name\x3d"radio"\x3e\x3clabel for\x3d"' + this.id + '_stereo_e"\x3eEntgegen (E)\x3c/label\x3e\x3cinput type\x3d"radio" id\x3d"' + this.id + '_stereo_z" name\x3d"radio"\x3e\x3clabel for\x3d"' +
            this.id + '_stereo_z"\x3eZusammen (Z)\x3c/label\x3e\x3c/div\x3e'));
        f.push("\x3c/table\x3e");
        f.push("\x3c/div\x3e");
        d.getElementById(this.sketcher.id) ? h("#" + this.sketcher.id).before(f.join("")) : d.writeln(f.join(""));
        let g = this;
        h("#" + this.id + "_radioTypes").buttonset();
        h("#" + this.id + "_radio").buttonset();
        this.getElement().dialog({
            autoOpen: !1,
            width: 520,
            height: 300,
            buttons: {
                Cancel: function() {
                    h(this).dialog("close")
                },
                Remove: function() {
                    g.sketcher.historyManager.pushUndo(new p.ChangeQueryAction(g.b));
                    h(this).dialog("close")
                },
                Set: function() {
                    let d = new a.Query(a.Query.TYPE_BOND);
                    h("#" + g.id + "_type_0").is(":checked") && d.orders.v.push("0");
                    h("#" + g.id + "_type_1").is(":checked") && d.orders.v.push("1");
                    h("#" + g.id + "_type_2").is(":checked") && d.orders.v.push("2");
                    h("#" + g.id + "_type_3").is(":checked") && d.orders.v.push("3");
                    h("#" + g.id + "_type_4").is(":checked") && d.orders.v.push("4");
                    h("#" + g.id + "_type_5").is(":checked") && d.orders.v.push("5");
                    h("#" + g.id + "_type_6").is(":checked") && d.orders.v.push("6");
                    h("#" + g.id + "_type_h").is(":checked") &&
                        d.orders.v.push("h");
                    h("#" + g.id + "_type_r").is(":checked") && d.orders.v.push("r");
                    h("#" + g.id + "_type_a").is(":checked") && d.orders.v.push("a");
                    h("#" + g.id + "_orders_not").is(":checked") && (d.orders.not = !0);
                    h("#" + g.id + "_aromatic_include").is(":checked") && (d.aromatic = {
                        v: !0,
                        not: h("#" + g.id + "_aromatic_not").is(":checked")
                    });
                    h("#" + g.id + "_ringCount_include").is(":checked") && (d.ringCount = {
                        v: d.parseRange(h("#" + g.id + "_ringCount_value").val()),
                        not: h("#" + g.id + "_ringCount_not").is(":checked")
                    });
                    if (h("#" + g.id + "_stereo_include").is(":checked")) {
                        let a =
                            "E";
                        h("#" + g.id + "_stereo_a").is(":checked") ? a = "A" : h("#" + g.id + "_stereo_z").is(":checked") && (a = "Z");
                        d.stereo = {
                            v: a,
                            not: h("#" + g.id + "_stereo_not").is(":checked")
                        }
                    }
                    g.sketcher.historyManager.pushUndo(new p.ChangeQueryAction(g.b, d));
                    h(this).dialog("close")
                }
            },
            open: function(a, d) {
                h("#" + g.id).animate({
                    scrollTop: 0
                }, "fast")
            }
        })
    }
})(ChemDoodle, ChemDoodle.structures, ChemDoodle.uis.actions, ChemDoodle.uis.gui.desktop, ChemDoodle.uis.gui.imageDepot, ChemDoodle.lib.jQuery, document);
(function(g, a, p, f, m) {
    a.MolGrabberDialog = function(a, d) {
        this.sketcherid = a;
        this.id = a + d
    };
    a = a.MolGrabberDialog.prototype = new a.Dialog;
    a.title = "MolGrabber";
    a.setup = function() {
        let a = [];
        a.push('\x3cdiv style\x3d"font-size:12px;text-align:center;" id\x3d"');
        a.push(this.id);
        a.push('" title\x3d"');
        a.push(this.title);
        a.push('"\x3e');
        this.message && (a.push("\x3cp\x3e"), a.push(this.message), a.push("\x3c/p\x3e"));
        a.push('\x3ccanvas class\x3d"ChemDoodleWebComponent" id\x3d"');
        a.push(this.id);
        a.push('_mg"\x3e\x3c/canvas\x3e');
        this.afterMessage && (a.push("\x3cp\x3e"), a.push(this.afterMessage), a.push("\x3c/p\x3e"));
        a.push("\x3c/div\x3e");
        f.getElementById(this.sketcherid) ? p("#" + this.sketcherid).before(a.join("")) : f.writeln(a.join(""));
        this.canvas = new g.MolGrabberCanvas(this.id + "_mg", 200, 200);
        this.canvas.styles.backgroundColor = "#fff";
        this.canvas.repaint();
        this.getElement().dialog({
            autoOpen: !1,
            width: 250,
            buttons: this.buttons
        })
    }
})(ChemDoodle, ChemDoodle.uis.gui.desktop, ChemDoodle.lib.jQuery, document);
(function(g, a, p, f, m) {
    a.PeriodicTableDialog = function(a, d) {
        this.sketcher = a;
        this.id = a.id + d
    };
    g = a.PeriodicTableDialog.prototype = new a.Dialog;
    g.title = "Periodic Table";
    g.setup = function() {
        let a = [];
        a.push('\x3cdiv style\x3d"text-align:center;" id\x3d"');
        a.push(this.id);
        a.push('" title\x3d"');
        a.push(this.title);
        a.push('"\x3e');
        a.push('\x3ccanvas class\x3d"ChemDoodleWebComponents" id\x3d"');
        a.push(this.id);
        a.push('_pt"\x3e\x3c/canvas\x3e\x3c/div\x3e');
        f.getElementById(this.sketcher.id) ? p("#" + this.sketcher.id).before(a.join("")) :
            f.writeln(a.join(""));
        this.canvas = new ChemDoodle.PeriodicTableCanvas(this.id + "_pt", 20);
        this.canvas.selected = this.canvas.cells[7];
        this.canvas.repaint();
        let d = this;
        this.canvas.click = function(a) {
            this.hovered && (this.selected = this.hovered, a = this.getHoveredElement(), d.sketcher.stateManager.setState(d.sketcher.stateManager.STATE_LABEL), d.sketcher.stateManager.STATE_LABEL.label = a.symbol, d.sketcher.floatDrawTools ? d.sketcher.toolbarManager.labelTray.open(d.sketcher.toolbarManager.buttonLabelPT) : d.sketcher.toolbarManager.buttonLabel.absorb(d.sketcher.toolbarManager.buttonLabelPT),
                d.sketcher.toolbarManager.buttonLabel.select(), this.repaint())
        };
        this.getElement().dialog({
            autoOpen: !1,
            width: 400,
            buttons: d.buttons
        })
    }
})(ChemDoodle, ChemDoodle.uis.gui.desktop, ChemDoodle.lib.jQuery, document);
(function(g, a, p, f, m, h, d, l, t, q) {
    let r = new a.JSONInterpreter,
        n = /[^A-z0-9]|\[|\]/g;
    p.TemplateDialog = function(a, e) {
        this.sketcher = a;
        this.id = a.id + e
    };
    a = p.TemplateDialog.prototype = new p.Dialog;
    a.title = "Templates";
    a.setup = function() {
        let a = this,
            e = [];
        e.push('\x3cdiv style\x3d"font-size:12px;align-items:center;display:flex;flex-direction:column;" id\x3d"');
        e.push(this.id);
        e.push('" title\x3d"');
        e.push(this.title);
        e.push('"\x3e');
        e.push('\x3ccanvas class\x3d"ChemDoodleWebComponent" id\x3d"');
        e.push(this.id);
        e.push('_buffer" style\x3d"display:none;"\x3e\x3c/canvas\x3e');
        e.push('\x3ccanvas class\x3d"ChemDoodleWebComponent" id\x3d"');
        e.push(this.id);
        e.push('_attachment"\x3e\x3c/canvas\x3e');
        e.push('\x3cdiv\x3e\x3cselect id\x3d"');
        e.push(this.id);
        e.push('_select"\x3e');
        for (let a = 0, d = f.length; a < d; a++) {
            var p = f[a];
            e.push('\x3coption value\x3d"');
            e.push(p.name);
            e.push('"\x3e');
            e.push(p.name);
            e.push("\x3c/option\x3e")
        }
        e.push("\x3c/select\x3e");
        e.push('\x26nbsp;\x26nbsp;\x3cbutton type\x3d"button" id\x3d"');
        e.push(this.id);
        e.push('_button_add"\x3eAdd Template\x3c/button\x3e\x3c/div\x3e');
        e.push('\x3cdiv id\x3d"');
        e.push(this.id);
        e.push('_scroll" style\x3d"width:100%;height:150px;flex-grow:1;overflow-y:scroll;overflow-x:hidden;background:#eee;padding-right:5px;padding-bottom:5px;"\x3e');
        for (let a = 0, d = f.length; a < d; a++) p = f[a], p.condensedName = p.name.replace(n, ""), e.push('\x3cdiv style\x3d"display:flex;flex-wrap:wrap;justify-content:center;" id\x3d"'), e.push(this.id), e.push("_"), e.push(p.condensedName), e.push('_panel"\x3e'), e.push("\x3c/div\x3e");
        e.push("\x3c/div\x3e");
        e.push("\x3c/div\x3e");
        d.getElementById(this.sketcher.id) ? m("#" + this.sketcher.id).before(e.join("")) : d.writeln(e.join(""));
        this.buffer = new g.ViewerCanvas(this.id + "_buffer", 100, 100);
        this.bufferElement = d.getElementById(this.buffer.id);
        this.canvas = new g.ViewerCanvas(this.id + "_attachment", 200, 200);
        this.canvas.mouseout = function(a) {
            if (0 !== this.molecules.length) {
                for (let a = 0, b = this.molecules[0].atoms.length; a < b; a++) this.molecules[0].atoms[a].isHover = !1;
                this.repaint()
            }
        };
        this.canvas.touchend = this.canvas.mouseout;
        this.canvas.mousemove =
            function(a) {
                if (0 !== this.molecules.length) {
                    let e = q;
                    a.p.x = this.width / 2 + (a.p.x - this.width / 2) / this.styles.scale;
                    a.p.y = this.height / 2 + (a.p.y - this.height / 2) / this.styles.scale;
                    for (let b = 0, c = this.molecules[0].atoms.length; b < c; b++) {
                        let c = this.molecules[0].atoms[b];
                        c.isHover = !1;
                        if (e === q || a.p.distance(c) < a.p.distance(e)) e = c
                    }
                    10 > a.p.distance(e) && (e.isHover = !0);
                    this.repaint()
                }
            };
        this.canvas.mousedown = function(e) {
            if (0 !== this.molecules.length) {
                e = !1;
                for (let a = 0, b = this.molecules[0].atoms.length; a < b; a++)
                    if (this.molecules[0].atoms[a].isHover) {
                        e = !0;
                        break
                    } if (e)
                    for (let d = 0, b = this.molecules[0].atoms.length; d < b; d++) e = this.molecules[0].atoms[d], e.isSelected = !1, e.isHover && (e.isSelected = !0, e.isHover = !1, a.sketcher.stateManager.STATE_NEW_TEMPLATE.attachPos = d, a.sketcher.toolbarManager.buttonTemplate.select(), a.sketcher.toolbarManager.buttonTemplate.getElement().click());
                this.repaint()
            }
        };
        this.canvas.touchstart = function(e) {
            a.canvas.mousemove(e);
            a.canvas.mousedown(e)
        };
        this.canvas.drawChildExtras = function(e, d) {
            e.strokeStyle = a.sketcher.styles.colorSelect;
            e.fillStyle = a.sketcher.styles.colorSelect;
            e.beginPath();
            e.arc(8, 8, 7, 0, 2 * h.PI, !1);
            e.stroke();
            e.textAlign = "left";
            e.textBaseline = "middle";
            e.fillText("Substitution Point", 18, 8);
            e.save();
            e.translate(this.width / 2, this.height / 2);
            e.rotate(d.rotateAngle);
            e.scale(d.scale, d.scale);
            e.translate(-this.width / 2, -this.height / 2);
            if (0 !== this.molecules.length)
                for (let b = 0, c = this.molecules[0].atoms.length; b < c; b++) this.molecules[0].atoms[b].drawDecorations(e, a.sketcher.styles);
            e.restore()
        };
        this.getElement().dialog({
            autoOpen: !1,
            width: 260,
            height: 450,
            buttons: a.buttons,
            open: function() {
                a.populated || (a.populated = !0, a.populate())
            }
        });
        m("#" + this.id + "_select").change(function() {
            let e = this.selectedIndex;
            for (let e = 0, b = f.length; e < b; e++) m("#" + a.id + "_" + f[e].condensedName + "_panel").hide();
            m("#" + a.id + "_" + f[e].condensedName + "_panel").show();
            m("#" + a.id + "_scroll").scrollTop(0);
            a.loadTemplate(e, 0, !0)
        });
        m("#" + this.id + "_button_add").click(function() {
            if (0 === a.sketcher.lasso.atoms.length) alert("Please select a structure to define a template.");
            else {
                var e = !0;
                if (1 < a.sketcher.lasso.atoms.length) {
                    var d = a.sketcher.lasso.getFirstMolecule();
                    for (let b = 1, f = a.sketcher.lasso.atoms.length; b < f; b++)
                        if (d !== a.sketcher.getMoleculeByAtom(a.sketcher.lasso.atoms[b])) {
                            e = !1;
                            alert("Templates may only be defined of a single discrete structure.");
                            break
                        }
                }
                if (e) {
                    var b = prompt("Please enter the template name:", "My template");
                    if (null !== b) {
                        e = f[f.length - 1];
                        let c = r.molTo(a.sketcher.lasso.getFirstMolecule());
                        d = r.molFrom(c);
                        let h = m("#" + a.id + "_" + e.condensedName + "_panel");
                        0 === e.templates.length && h.empty();
                        b = {
                            name: b,
                            data: c
                        };
                        d.scaleToAverageBondLength(a.sketcher.styles.bondLength_2D);
                        a.buffer.loadMolecule(d);
                        b.img = a.bufferElement.toDataURL("image/png");
                        b.condensedName = b.name.replace(n, "");
                        h.append('\x3cdiv style\x3d"margin-left:5px;margin-top:5px;"\x3e\x3ccenter\x3e\x3cimg src\x3d"' + b.img + '" id\x3d"' + a.id + "_" + b.condensedName + '" g\x3d"' + (f.length - 1) + '" t\x3d"' + e.templates.length + '"style\x3d"width:100px;height:100px;" /\x3e\x3cbr\x3e' + b.name + "\x3c/center\x3e\x3c/div\x3e");
                        d = m("#" + a.id + "_" + b.condensedName);
                        d.click(function() {
                            a.loadTemplate(parseInt(this.getAttribute("g")), parseInt(this.getAttribute("t")), !0)
                        });
                        d.hover(function() {
                            m(this).css({
                                border: "1px solid " + a.sketcher.styles.colorHover,
                                margin: "-1px"
                            })
                        }, function() {
                            m(this).css({
                                border: "none",
                                margin: "0px"
                            })
                        });
                        e.templates.push(b);
                        t && t.setItem("chemdoodle_user_templates", l.stringify(f[f.length - 1].templates))
                    }
                }
            }
        })
    };
    a.loadTemplate = function(a, e, d) {
        if (a = f[a].templates[e]) {
            e = r.molFrom(a.data);
            e.scaleToAverageBondLength(this.sketcher.styles.bondLength_2D);
            let f = -1,
                h = Infinity;
            for (let b = 0, a = e.atoms.length; b < a; b++) {
                let a = e.atoms[b];
                "C" === a.label && a.x < h && (f = b, h = a.x)
            } - 1 === f && (f = 0);
            e.atoms[f].isSelected = !0;
            this.canvas.loadMolecule(e);
            this.sketcher.stateManager.STATE_NEW_TEMPLATE.template = a.data;
            this.sketcher.stateManager.STATE_NEW_TEMPLATE.attachPos = f;
            d && (this.sketcher.toolbarManager.buttonTemplate.select(), this.sketcher.toolbarManager.buttonTemplate.getElement().click())
        }
    };
    a.populate = function() {
        this.canvas.styles = m.extend({}, this.sketcher.styles);
        this.canvas.styles.atoms_implicitHydrogens_2D = !1;
        this.buffer.styles = m.extend({}, this.sketcher.styles);
        this.buffer.styles.atoms_implicitHydrogens_2D = !1;
        let a = this;
        for (let d = 0, h = f.length; d < h; d++) {
            let h = f[d],
                b = m("#" + this.id + "_" + h.condensedName + "_panel");
            if (0 === h.templates.length) b.append('\x3cdiv style\x3d"margin:5px;"\x3eThere are no templates in this group.\x3c/div\x3e');
            else
                for (let c = 0, f = h.templates.length; c < f; c++) {
                    var e = h.templates[c];
                    let f = r.molFrom(e.data);
                    f.scaleToAverageBondLength(this.sketcher.styles.bondLength_2D);
                    this.buffer.loadMolecule(f);
                    e.img = this.bufferElement.toDataURL("image/png");
                    e.condensedName = e.name.replace(n, "");
                    b.append('\x3cdiv style\x3d"margin-left:5px;margin-top:5px;"\x3e\x3ccenter\x3e\x3cimg src\x3d"' + e.img + '" id\x3d"' + this.id + "_" + e.condensedName + '" g\x3d"' + d + '" t\x3d"' + c + '" style\x3d"width:100px;height:100px;border-radius:10px;" /\x3e\x3cbr\x3e' + e.name + "\x3c/center\x3e\x3c/div\x3e");
                    e = m("#" + this.id + "_" + e.condensedName);
                    e.click(function() {
                        a.loadTemplate(parseInt(this.getAttribute("g")), parseInt(this.getAttribute("t")),
                            !0)
                    });
                    e.hover(function() {
                        m(this).css({
                            border: "1px solid " + a.sketcher.styles.colorHover,
                            margin: "-1px"
                        })
                    }, function() {
                        m(this).css({
                            border: "none",
                            margin: "0px"
                        })
                    })
                }
            0 !== d && b.hide()
        }
        0 !== f.length && (m("#" + this.id + "_" + f[0].condensedName + "_panel").show(), this.loadTemplate(0, 0, !1))
    }
})(ChemDoodle, ChemDoodle.io, ChemDoodle.uis.gui.desktop, ChemDoodle.uis.gui.templateDepot, ChemDoodle.lib.jQuery, Math, document, JSON, localStorage);
(function(g, a, p, f) {
    g.Popover = function(a, f, d, g) {
        this.sketcher = a;
        this.id = f;
        this.free = d;
        this.onclose = g
    };
    g = g.Popover.prototype;
    g.getHiddenSource = function() {
        let a = [];
        a.push('\x3cdiv style\x3d"display:none;position:absolute;z-index:10;border:1px #C1C1C1 solid;background:#F5F5F5;padding:5px;');
        this.free ? a.push("border-radius:5px;-moz-border-radius:5px;") : a.push("border-bottom-left-radius:5px;-moz-border-radius-bottomleft:5px;border-bottom-right-radius:5px;-moz-border-radius-bottomright:5px;border-top-color:black;");
        a.push('" id\x3d"');
        a.push(this.id);
        a.push('"\x3e');
        a.push(this.getContentSource());
        a.push("\x3c/div\x3e");
        return a.join("")
    };
    g.setup = function() {
        p.getElementById(this.sketcher.id) ? a("#" + this.sketcher.id).before(this.getHiddenSource()) : p.writeln(this.getHiddenSource());
        a("#" + this.id).hide();
        this.setupContent && this.setupContent()
    };
    g.show = function(f) {
        if (this.sketcher.modal) return !1;
        this.sketcher.modal = this;
        this.sketcher.doEventDefault = !0;
        let h = a("#" + this.id);
        this.free ? h.fadeIn(200).position({
            my: "center bottom",
            at: "center top",
            of: f,
            collision: "fit"
        }) : h.slideDown(400).position({
            my: "center top",
            at: "center top",
            of: a("#" + this.sketcher.id),
            collision: "fit"
        });
        return !1
    };
    g.close = function(g) {
        let h = a("#" + this.id);
        this.free ? h.hide(0) : h.slideUp(400);
        if (this.onclose) this.onclose(g);
        this.sketcher.modal = f;
        this.sketcher.doEventDefault = !1
    }
})(ChemDoodle.uis.gui.desktop, ChemDoodle.lib.jQuery, document);
(function(g, a, p, f, m, h) {
    p.IsotopePopover = function(a, f) {
        this.sketcher = a;
        this.id = a.id + f
    };
    g = p.IsotopePopover.prototype = new p.Popover;
    g.populate = function(a) {
        f("#" + this.id + "_input").val(-1 == a.mass ? "" : a.mass)
    };
    g.getContentSource = function() {
        let a = ['\x3cdiv style\x3d"width:320px;"\x3e'];
        a.push('\x3cdiv width\x3d"100%"\x3eEnter a positive integer for the isotope value:\x3c/div\x3e');
        a.push('\x3ccenter\x3e\x3ctable\x3e\x3ctr\x3e\x3ctd\x3e\x3cbutton type\x3d"button" id\x3d"' + this.id + '_remove" style\x3d"margin-right:100px;"\x3eRemove\x3c/button\x3e\x3c/td\x3e\x3ctd\x3e\x3cinput type\x3d"number" id\x3d"' +
            this.id + '_input" name\x3d"tentacles" min\x3d"1" max\x3d"999" style\x3d"margin:10px;"\x3e\x3c/input\x3e\x3c/td\x3e\x3ctd\x3e\x3cbutton type\x3d"button" id\x3d"' + this.id + '_set"\x3eSet\x3c/button\x3e\x3c/td\x3e\x3c/tr\x3e\x3c/table\x3e\x3c/center\x3e');
        a.push("\x3c/div\x3e");
        return a.join("")
    };
    g.setupContent = function() {
        let d = this;
        f("#" + this.id + "_set").click(function() {
            let h = parseInt(f("#" + d.id + "_input").val());
            1 > h ? alert("Please input a positive integer for the isotope value.") : 999 < h ? alert("The maximum allowed isotope value is 999.") :
                d.sketcher.hovering.mass !== h && (d.close(), d.sketcher.historyManager.pushUndo(new a.ChangeIsotopeAction(d.sketcher.hovering, h)))
        });
        f("#" + this.id + "_remove").click(function() {
            d.close(); - 1 !== d.sketcher.hovering.mass && d.sketcher.historyManager.pushUndo(new a.ChangeIsotopeAction(d.sketcher.hovering, -1))
        })
    }
})(ChemDoodle, ChemDoodle.uis.actions, ChemDoodle.uis.gui.desktop, ChemDoodle.lib.jQuery, document);
(function(g, a, p, f, m, h) {
    p.DialogManager = function(d) {
        let h = this;
        d.useServices ? this.saveDialog = new f.SaveFileDialog(d.id + "_save_dialog", d) : (this.saveDialog = new f.Dialog(d.id, "_save_dialog", "Save Molecule"), this.saveDialog.message = "Copy and paste the content of the textarea into a file and save it with the extension \x3cstrong\x3e.mol\x3c/strong\x3e.", this.saveDialog.includeTextArea = !0, this.saveDialog.afterMessage = '\x3ca href\x3d"http://www.chemdoodle.com" target\x3d"_blank"\x3eHow do I use MOLFiles?\x3c/a\x3e');
        this.saveDialog.setup();
        this.openPopup = new f.Popover(d, d.id + "_open_popover");
        this.openPopup.getContentSource = function() {
            let a = ['\x3cdiv style\x3d"width:320px;"\x3e'];
            a.push('\x3cdiv width\x3d"100%"\x3ePaste \x3cem\x3eMOLFile\x3c/em\x3e or \x3cem\x3eChemDoodle JSON\x3c/em\x3e text and press the \x3cstrong\x3eLoad\x3c/strong\x3e button.\x3cbr\x3e\x3cbr\x3e\x3ccenter\x3e\x3ca href\x3d"http://www.chemdoodle.com" target\x3d"_blank"\x3eWhere do I get MOLFiles or ChemDoodle JSON?\x3c/a\x3e\x3c/center\x3e\x3cbr\x3e\x3c/div\x3e');
            a.push('\x3ctextarea rows\x3d"12" id\x3d"' + d.id + '_open_text" style\x3d"width:100%;"\x3e\x3c/textarea\x3e');
            a.push('\x3cbr\x3e\x3cbutton type\x3d"button" style\x3d"margin-left:270px;" id\x3d"' + d.id + '_open_load"\x3eLoad\x3c/button\x3e\x3c/div\x3e');
            return a.join("")
        };
        this.openPopup.setupContent = function() {
            m("#" + d.id + "_open_load").click(function() {
                h.openPopup.close();
                let f = m("#" + d.id + "_open_text").val(),
                    l; - 1 !== f.indexOf("v2000") || -1 !== f.indexOf("V2000") ? l = {
                        molecules: [g.readMOL(f)],
                        shapes: []
                    } : "{" === f.charAt(0) &&
                    (l = g.readJSON(f));
                d.oneMolecule && l && 0 < l.molecules.length && 0 < l.molecules[0].atoms.length ? d.historyManager.pushUndo(new a.SwitchMoleculeAction(d, l.molecules[0])) : !d.oneMolecule && l && (0 < l.molecules.length || 0 < l.shapes.length) ? d.historyManager.pushUndo(new a.SwitchContentAction(d, l.molecules, l.shapes)) : alert("No chemical content was recognized.")
            })
        };
        this.openPopup.setup();
        this.isotopePopup = new f.IsotopePopover(d, "_isotope_popover");
        this.isotopePopup.setup();
        this.atomQueryDialog = new f.AtomQueryDialog(d,
            "_atom_query_dialog");
        this.atomQueryDialog.setup();
        this.bondQueryDialog = new f.BondQueryDialog(d, "_bond_query_dialog");
        this.bondQueryDialog.setup();
        this.templateDialog = new f.TemplateDialog(d, "_templates_dialog");
        this.templateDialog.setup();
        this.searchDialog = new f.MolGrabberDialog(d.id, "_search_dialog");
        this.searchDialog.buttons = {
            Load: function() {
                var f = h.searchDialog.canvas.molecules[0];
                if (f && 0 < f.atoms.length)
                    if (m(this).dialog("close"), d.oneMolecule) f !== d.molecule && d.historyManager.pushUndo(new a.SwitchMoleculeAction(d,
                        f));
                    else {
                        d.historyManager.pushUndo(new a.AddContentAction(d, h.searchDialog.canvas.molecules, h.searchDialog.canvas.shapes));
                        d.toolbarManager.buttonLasso.select();
                        d.toolbarManager.buttonLasso.getElement().click();
                        f = [];
                        for (let a = 0, d = h.searchDialog.canvas.molecules.length; a < d; a++) f = f.concat(h.searchDialog.canvas.molecules[a].atoms);
                        d.lasso.select(f, h.searchDialog.canvas.shapes)
                    }
                else alert('After entering a search term, press the "Show Molecule" button to show it before loading. To close this dialog, press the "X" button to the top-right.')
            }
        };
        this.searchDialog.setup();
        d.setupScene && (this.stylesDialog = new f.SpecsDialog(d, "_styles_dialog"), this.stylesDialog.buttons = {
            Done: function() {
                m(this).dialog("close")
            }
        }, this.stylesDialog.setup(this.stylesDialog, d));
        this.periodicTableDialog = new f.PeriodicTableDialog(d, "_periodicTable_dialog");
        this.periodicTableDialog.buttons = {
            Close: function() {
                m(this).dialog("close")
            }
        };
        this.periodicTableDialog.setup();
        this.calculateDialog = new f.Dialog(d.id, "_calculate_dialog", "Calculations");
        this.calculateDialog.includeTextArea = !0;
        this.calculateDialog.afterMessage = '\x3ca href\x3d"http://www.chemdoodle.com" target\x3d"_blank"\x3eWant more calculations?\x3c/a\x3e';
        this.calculateDialog.setup();
        this.inputDialog = new f.Dialog(d.id, "_input_dialog", "Input");
        this.inputDialog.message = 'Please input the rgroup number (must be a positive integer). Input "-1" to remove the rgroup.';
        this.inputDialog.includeTextField = !0;
        this.inputDialog.buttons = {
            Done: function() {
                m(this).dialog("close");
                h.inputDialog.doneFunction && h.inputDialog.doneFunction(h.inputDialog.getTextField().val())
            }
        };
        this.inputDialog.setup();
        this.makeOtherDialogs && this.makeOtherDialogs(d)
    }
})(ChemDoodle, ChemDoodle.uis.actions, ChemDoodle.uis.gui, ChemDoodle.uis.gui.desktop, ChemDoodle.lib.jQuery);
(function(g, a, p, f, m) {
    g.DropDown = function(a, f, h) {
        this.id = a;
        this.tooltip = f;
        this.dummy = h;
        this.buttonSet = new g.ButtonSet(a + "_set");
        this.buttonSet.buttonGroup = f;
        this.defaultButton = m
    };
    let h = g.DropDown.prototype;
    h.getButtonSource = function() {
        let d = [];
        d.push('\x3cbutton type\x3d"button" id\x3d"');
        d.push(this.id);
        d.push('" onclick\x3d"return false;" title\x3d"');
        d.push(this.tooltip);
        d.push('" style\x3d"box-sizing:border-box;margin-top:0px; margin-bottom:1px; padding:0px; height:28px; width:15px;"\x3e\x3cimg title\x3d"');
        d.push(this.tooltip);
        d.push('" width\x3d"9" height\x3d"20" src\x3d"');
        d.push(a.getURI(a.ARROW_DOWN));
        d.push('"\x3e\x3c/button\x3e');
        return d.join("")
    };
    h.getHiddenSource = function() {
        let a = [];
        a.push('\x3cdiv style\x3d"display:none;position:absolute;z-index:10;border:1px #C1C1C1 solid;background:#F5F5F5;padding:5px;border-bottom-left-radius:5px;-moz-border-radius-bottomleft:5px;border-bottom-right-radius:5px;-moz-border-radius-bottomright:5px;" id\x3d"');
        a.push(this.id);
        a.push('_hidden"\x3e');
        a.push(this.buttonSet.getSource(this.id +
            "_popup_set"));
        a.push("\x3c/div\x3e");
        return a.join("")
    };
    h.setup = function() {
        this.defaultButton || (this.defaultButton = this.buttonSet.buttons[0]);
        let a = "#" + this.id,
            h = p(a);
        h.button();
        h.click(function() {
            p(f).trigger("click");
            let d = p(a + "_hidden");
            d.show().position({
                my: "center top",
                at: "center bottom",
                of: this,
                collision: "fit"
            });
            p(f).one("click", function() {
                d.hide()
            });
            return !1
        });
        this.buttonSet.setup();
        let g = this;
        p.each(this.buttonSet.buttons, function(a, d) {
            g.buttonSet.buttons[a].getElement().click(function() {
                g.dummy.absorb(g.buttonSet.buttons[a]);
                g.dummy.select();
                g.dummy.getElement().click()
            })
        });
        g.dummy.absorb(this.defaultButton);
        this.defaultButton.select()
    }
})(ChemDoodle.uis.gui.desktop, ChemDoodle.uis.gui.imageDepot, ChemDoodle.lib.jQuery, document);
(function(g, a, p, f) {
    g.DummyButton = function(a, h) {
        this.id = a;
        this.toggle = !1;
        this.tooltip = h ? h : "";
        this.func = f
    };
    g = g.DummyButton.prototype = new g.Button;
    g.setup = function() {
        let a = this;
        this.getElement().click(function() {
            a.func()
        })
    };
    g.absorb = function(f) {
        p("#" + this.id + "_icon").attr("src", a.getURI(f.icon));
        this.func = f.func
    }
})(ChemDoodle.uis.gui.desktop, ChemDoodle.uis.gui.imageDepot, ChemDoodle.lib.jQuery);
(function(g, a, p) {
    g.TextButton = function(a, g, h) {
        this.id = a;
        this.toggle = !1;
        this.tooltip = g ? g : "";
        this.func = h ? h : p
    };
    g = g.TextButton.prototype = new g.Button;
    g.getSource = function(a) {
        let f = [];
        this.toggle ? (f.push('\x3cinput type\x3d"radio" name\x3d"'), f.push(a), f.push('" id\x3d"'), f.push(this.id), f.push('" title\x3d"'), f.push(this.tooltip), f.push('" /\x3e\x3clabel for\x3d"'), f.push(this.id), f.push('"\x3e'), f.push(this.tooltip), f.push("\x3c/label\x3e")) : (f.push('\x3cbutton type\x3d"button" id\x3d"'), f.push(this.id),
            f.push('" onclick\x3d"return false;" title\x3d"'), f.push(this.tooltip), f.push('"\x3e\x3clabel for\x3d"'), f.push(this.id), f.push('"\x3e'), f.push(this.tooltip), f.push("\x3c/label\x3e\x3c/button\x3e"));
        return f.join("")
    };
    g.check = function() {
        let a = this.getElement();
        a.prop("checked", !0);
        a.button("refresh")
    };
    g.uncheck = function() {
        let a = this.getElement();
        a.removeAttr("checked");
        a.button("refresh")
    }
})(ChemDoodle.uis.gui.desktop, ChemDoodle.lib.jQuery);
(function(g, a, p, f, m) {
    g.Tray = function(a, d, f, p) {
        this.sketcher = a;
        this.id = d;
        this.tooltip = f.tooltip;
        this.dummy = f;
        this.dummy.toggle = !0;
        this.buttonSet = new g.ButtonSet(d + "_set");
        this.buttonSet.columnCount = p;
        this.buttonSet.buttonGroup = this.tooltip;
        this.defaultButton = m
    };
    a = g.Tray.prototype;
    a.getSource = function(a) {
        let d = [];
        d.push(this.dummy.getSource(a));
        d.push('\x3cdiv style\x3d"display:none;position:absolute;z-index:11;border:none;background:#F5F5F5;box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19);" id\x3d"');
        d.push(this.id);
        d.push('_hidden"\x3e');
        d.push(this.buttonSet.getSource(this.id + "_popup_set"));
        d.push("\x3c/div\x3e");
        return d.join("")
    };
    a.setup = function() {
        this.dummy.setup(!0);
        let a = this.dummy.getElement();
        a.button();
        this.defaultButton || (this.defaultButton = this.buttonSet.buttons[0]);
        let d = this,
            g = "#" + this.id;
        a.click(function() {
            d.sketcher.openTray !== d && (d.sketcher.openTray && d.sketcher.openTray.close(), d.sketcher.openTray = d, p(f).trigger("click"), p(g + "_hidden").show());
            d.reposition()
        });
        this.buttonSet.setup();
        p.each(this.buttonSet.buttons, function(a, f) {
            d.buttonSet.buttons[a].getElement().click(function() {
                d.dummy.absorb(d.buttonSet.buttons[a])
            })
        });
        this.dummy.absorb(this.defaultButton);
        this.defaultButton.select()
    };
    a.open = function(a) {
        this.sketcher.openTray !== this && (this.sketcher.openTray && this.sketcher.openTray.close(), this.sketcher.openTray = this, p(f).trigger("click"), p("#" + this.id + "_hidden").show());
        a && (this.dummy.absorb(a), a.select());
        this.reposition()
    };
    a.reposition = function() {
        let a = p("#" + this.dummy.id +
            "_icon");
        p("#" + this.id + "_hidden").position({
            my: "right-8 center",
            at: "left center",
            of: a,
            collision: "flip none"
        })
    };
    a.close = function() {
        p("#" + this.id + "_hidden").hide();
        this.sketcher.openTray = m
    }
})(ChemDoodle.uis.gui.desktop, ChemDoodle.uis.gui.imageDepot, ChemDoodle.lib.jQuery, document);
(function(g, a, p, f, m, h, d, l, t, q, r, n, v) {
    h.ToolbarManager = function(e) {
        this.sketcher = e;
        this.sketcher.floatDrawTools && (this.drawTools = new l.FloatingToolbar(e));
        this.buttonOpen = new l.Button(e.id + "_button_open", d.OPEN, "Open", function() {
            e.dialogManager.openPopup.show()
        });
        /*
        this.buttonSave = new l.Button(e.id + "_button_save", d.SAVE, "Save", function() {
            e.useServices ? e.dialogManager.saveDialog.clear() : e.oneMolecule ? e.dialogManager.saveDialog.getTextArea().val(g.writeMOL(e.molecules[0])) : e.lasso.isActive() && e.dialogManager.saveDialog.getTextArea().val(g.writeMOL(e.lasso.getFirstMolecule()));
            e.dialogManager.saveDialog.open()
        });
        */
        this.buttonTemplate = new l.Button(e.id + "_button_template", d.TEMPLATES, "Templates", function() {
            e.stateManager.setState(e.stateManager.STATE_NEW_TEMPLATE);
            e.dialogManager.templateDialog.open()
        });
        this.buttonTemplate.toggle = !0;
        this.buttonSearch = new l.Button(e.id + "_button_search", d.SEARCH, "Search", function() {
            e.dialogManager.searchDialog.open()
        });
        this.buttonCalculate = new l.Button(e.id + "_button_calculate", d.CALCULATE, "Calculate", function() {
            let d = e.oneMolecule ? e.molecules[0] :
                e.lasso.getFirstMolecule();
            d && a.calculate(d, {
                descriptors: "mf ef mw miw deg_unsat hba hbd rot electron pol_miller cmr tpsa vabc xlogp2 bertz".split(" ")
            }, function(a) {
                function d(a, e, d) {
                    b.push(a);
                    b.push(": ");
                    for (a = a.length + 2; 30 > a; a++) b.push(" ");
                    b.push(e);
                    b.push(" ");
                    b.push(d);
                    b.push("\n")
                }
                let b = [];
                d("Molecular Formula", a.mf, "");
                d("Empirical Formula", a.ef, "");
                d("Molecular Mass", a.mw, "amu");
                d("Monoisotopic Mass", a.miw, "amu");
                d("Degree of Unsaturation", a.deg_unsat, "");
                d("Hydrogen Bond Acceptors", a.hba,
                    "");
                d("Hydrogen Bond Donors", a.hbd, "");
                d("Rotatable Bonds", a.rot, "");
                d("Total Electrons", a.rot, "");
                d("Molecular Polarizability", a.pol_miller, "A^3");
                d("Molar Refractivity", a.cmr, "cm^3/mol");
                d("Polar Surface Area", a.tpsa, "A^2");
                d("vdW Volume", a.vabc, "A^3");
                d("logP", a.xlogp2, "");
                d("Complexity", a.bertz, "");
                e.dialogManager.calculateDialog.getTextArea().val(b.join(""));
                e.dialogManager.calculateDialog.open()
            })
        });
        this.buttonMove = new l.Button(e.id + "_button_move", d.MOVE, "Move", function() {
            e.stateManager.setState(e.stateManager.STATE_MOVE)
        });
        this.buttonMove.toggle = !0;
        this.buttonErase = new l.Button(e.id + "_button_erase", d.ERASE, "Erase", function() {
            e.stateManager.setState(e.stateManager.STATE_ERASE)
        });
        this.buttonErase.toggle = !0;
        this.buttonCenter = new l.Button(e.id + "_button_center", d.CENTER, "Center", function() {
            let a = new f.Point(e.width / 2, e.height / 2),
                d = e.getContentBounds();
            a.x -= (d.maxX + d.minX) / 2;
            a.y -= (d.maxY + d.minY) / 2;
            e.historyManager.pushUndo(new m.MoveAction(e.getAllPoints(), a))
        });
        this.buttonClear = new l.Button(e.id + "_button_clear", d.CLEAR,
            "Clear",
            function() {
                let a = !0;
                if (e.oneMolecule) {
                    if (1 === e.molecules[0].atoms.length) {
                        let d = e.molecules[0].atoms[0];
                        "C" === d.label && 0 === d.charge && -1 === d.mass && (a = !1)
                    }
                } else 0 === e.molecules.length && 0 === e.shapes.length && (a = !1);
                a && (e.stateManager.getCurrentState().clearHover(), e.lasso && e.lasso.isActive() && e.lasso.empty(), e.historyManager.pushUndo(new m.ClearAction(e)))
            });
        this.buttonClean = new l.Button(e.id + "_button_clean", d.OPTIMIZE, "Clean", function() {
            let d = e.oneMolecule ? e.molecules[0] : e.lasso.getFirstMolecule();
            if (d) {
                let h = new p.JSONInterpreter;
                a._contactServer("optimize", {
                    mol: h.molTo(d)
                }, {
                    dimension: 2
                }, function(a) {
                    a = h.molFrom(a.mol);
                    let b = a.getCenter(),
                        c = e.oneMolecule ? new f.Point(e.width / 2, e.height / 2) : d.getCenter();
                    c.sub(b);
                    for (let b = 0, e = a.atoms.length; b < e; b++) a.atoms[b].add(c);
                    e.historyManager.pushUndo(new m.ChangeCoordinatesAction(d.atoms, a.atoms))
                })
            }
        });
        this.makeLassoSet(this);
        this.makeCopySet(this);
        this.makeScaleSet(this);
        this.makeFlipSet(this);
        this.makeHistorySet(this);
        this.makeLabelSet(this);
        this.buttonTextInput =
            new l.Button(e.id + "_button_text_input", d.TEXT, "Set Atom Label", function() {
                e.stateManager.setState(e.stateManager.STATE_TEXT_INPUT)
            });
        this.buttonTextInput.toggle = !0;
        this.buttonQuery = new l.Button(e.id + "_button_query", d.QUERY, "Set Query to Atom or Bond", function() {
            e.stateManager.setState(e.stateManager.STATE_QUERY)
        });
        this.buttonQuery.toggle = !0;
        this.makeBondSet(this);
        this.makeRingSet(this);
        this.buttonChain = new l.Button(e.id + "_button_chain", d.CHAIN_CARBON, "Add Carbon Chain", function() {
            e.stateManager.setState(e.stateManager.STATE_NEW_CHAIN)
        });
        this.buttonChain.toggle = !0;
        this.makeAttributeSet(this);
        this.makeShapeSet(this);
        this.makeOtherButtons && this.makeOtherButtons(this)
    };
    h = h.ToolbarManager.prototype;
    h.write = function() {
        let a = ['\x3cdiv style\x3d"font-size:10px;"\x3e'],
            d = this.sketcher.id + "_main_group";
        this.sketcher.oneMolecule ? a.push(this.buttonMove.getSource(d)) : a.push(this.lassoSet.getSource(d));
        a.push(this.buttonClear.getSource());
        a.push(this.buttonErase.getSource(d));
        a.push(this.buttonCenter.getSource());
        this.sketcher.useServices && a.push(this.buttonClean.getSource());
        a.push(this.flipSet.getSource());
        a.push(this.historySet.getSource());
        this.sketcher.oneMolecule || a.push(this.copySet.getSource());
        a.push(this.scaleSet.getSource());
        a.push(this.buttonOpen.getSource());
        /*
        a.push(this.buttonSave.getSource());
        */
        a.push(this.buttonTemplate.getSource(d));
        this.sketcher.useServices && (a.push(this.buttonSearch.getSource()), a.push(this.buttonCalculate.getSource()));
        this.sketcher.floatDrawTools || (a.push("\x3cbr\x3e"), l.TextInput && a.push(this.buttonTextInput.getSource(d)), a.push(this.labelSet.getSource(d)),
            this.sketcher.includeQuery && a.push(this.buttonQuery.getSource(d)), a.push(this.attributeSet.getSource(d)), a.push(this.bondSet.getSource(d)), a.push(this.ringSet.getSource(d)), a.push(this.buttonChain.getSource(d)), this.sketcher.oneMolecule || a.push(this.shapeSet.getSource(d)));
        a.push("\x3c/div\x3e");
        this.sketcher.floatDrawTools && (l.TextInput && this.drawTools.components.splice(0, 0, this.buttonTextInput), this.sketcher.includeQuery && this.drawTools.components.splice(l.TextInput ? 1 : 0, 0, this.buttonQuery), this.drawTools.components.splice(this.drawTools.components.length -
            (this.sketcher.oneMolecule ? 1 : 3), 0, this.buttonChain), this.sketcher.oneMolecule || this.drawTools.components.push(this.buttonVAP), a.push(this.drawTools.getSource(d)));
        n.getElementById(this.sketcher.id) ? r("#" + this.sketcher.id).before(a.join("")) : n.write(a.join(""))
    };
    h.setup = function() {
        this.sketcher.oneMolecule ? this.buttonMove.setup(!0) : this.lassoSet.setup();
        this.buttonClear.setup();
        this.buttonErase.setup(!0);
        this.buttonCenter.setup();
        this.sketcher.useServices && this.buttonClean.setup();
        this.flipSet.setup();
        this.historySet.setup();
        this.sketcher.oneMolecule || this.copySet.setup();
        this.scaleSet.setup();
        this.buttonOpen.setup();
        /*
        this.buttonSave.setup();
        */
        this.buttonTemplate.setup(!0);
        this.sketcher.useServices && (this.buttonSearch.setup(), this.buttonCalculate.setup());
        this.sketcher.floatDrawTools ? (this.drawTools.setup(), this.buttonBond.getElement().click()) : (l.TextInput && this.buttonTextInput.setup(!0), this.labelSet.setup(), this.sketcher.includeQuery && this.buttonQuery.setup(!0), this.attributeSet.setup(), this.bondSet.setup(),
            this.ringSet.setup(), this.buttonChain.setup(!0), this.sketcher.oneMolecule || this.shapeSet.setup(), this.buttonSingle.getElement().click());
        this.buttonUndo.disable();
        this.buttonRedo.disable();
        this.sketcher.oneMolecule || (this.buttonCut.disable(), this.buttonCopy.disable(), this.buttonPaste.disable(), this.buttonFlipVert.disable(), this.buttonFlipHor.disable(), this.sketcher.useServices && (this.buttonClean.disable(), this.buttonCalculate.disable())) /*, this.buttonSave.disable()))*/
    };
    h.makeCopySet = function(a) {
        this.buttonCut =
            new l.Button(a.sketcher.id + "_button_cut", d.CUT, "Cut", function() {
                a.sketcher.copyPasteManager.copy(!0)
            });
        this.buttonCopy = new l.Button(a.sketcher.id + "_button_copy", d.COPY, "Copy", function() {
            a.sketcher.copyPasteManager.copy(!1)
        });
        this.buttonPaste = new l.Button(a.sketcher.id + "_button_paste", d.PASTE, "Paste", function() {
            a.sketcher.copyPasteManager.paste()
        });
        this.copySet = new l.ButtonSet(a.sketcher.id + "_buttons_copy");
        this.copySet.toggle = !1;
        this.copySet.buttons.push(this.buttonCut);
        this.copySet.buttons.push(this.buttonCopy);
        this.copySet.buttons.push(this.buttonPaste)
    };
    h.makeScaleSet = function(a) {
        this.buttonScalePlus = new l.Button(a.sketcher.id + "_button_scale_plus", d.ZOOM_IN, "Increase Scale", function() {
            a.sketcher.styles.scale *= 1.5;
            a.sketcher.checkScale();
            a.sketcher.repaint()
        });
        this.buttonScaleMinus = new l.Button(a.sketcher.id + "_button_scale_minus", d.ZOOM_OUT, "Decrease Scale", function() {
            a.sketcher.styles.scale /= 1.5;
            a.sketcher.checkScale();
            a.sketcher.repaint()
        });
        this.scaleSet = new l.ButtonSet(a.sketcher.id + "_buttons_scale");
        this.scaleSet.toggle = !1;
        this.scaleSet.buttons.push(this.buttonScalePlus);
        this.scaleSet.buttons.push(this.buttonScaleMinus)
    };
    h.makeLassoSet = function(a) {
        this.buttonLassoAll = new l.Button(a.sketcher.id + "_button_lasso_lasso", d.LASSO, "Lasso Tool", function() {
            a.sketcher.stateManager.setState(a.sketcher.stateManager.STATE_LASSO);
            a.sketcher.lasso.mode = t.Lasso.MODE_LASSO;
            a.sketcher.lasso.isActive() || a.sketcher.lasso.selectNextMolecule()
        });
        this.buttonLassoShapes = new l.Button(a.sketcher.id + "_button_lasso_shapes",
            d.LASSO_SHAPES, "Lasso Tool (shapes only)",
            function() {
                a.sketcher.stateManager.setState(a.sketcher.stateManager.STATE_LASSO);
                a.sketcher.lasso.mode = t.Lasso.MODE_LASSO_SHAPES;
                a.sketcher.lasso.isActive() || a.sketcher.lasso.selectNextShape()
            });
        this.buttonRectMarq = new l.Button(a.sketcher.id + "_button_lasso_marquee", d.MARQUEE, "Marquee Tool", function() {
            a.sketcher.stateManager.setState(a.sketcher.stateManager.STATE_LASSO);
            a.sketcher.lasso.mode = t.Lasso.MODE_RECTANGLE_MARQUEE;
            a.sketcher.lasso.isActive() || a.sketcher.lasso.selectNextMolecule()
        });
        this.lassoSet = new l.ButtonSet(a.sketcher.id + "_buttons_lasso");
        this.buttonLasso = new l.DummyButton(a.sketcher.id + "_button_lasso", "Selection Tool");
        this.lassoSet.buttons.push(this.buttonLasso);
        this.lassoSet.addDropDown("More Selection Tools");
        this.lassoSet.dropDown.buttonSet.buttons.push(this.buttonLassoAll);
        this.lassoSet.dropDown.buttonSet.buttons.push(this.buttonLassoShapes);
        this.lassoSet.dropDown.buttonSet.buttons.push(this.buttonRectMarq)
    };
    h.makeFlipSet = function(a) {
        let e = function(e) {
            let d = a.sketcher.oneMolecule ?
                a.sketcher.getAllPoints() : a.sketcher.lasso.getAllPoints(),
                b = [],
                c = a.sketcher.oneMolecule ? a.sketcher.getAllBonds() : a.sketcher.lasso.getBonds();
            for (let a = 0, e = c.length; a < e; a++) {
                let e = c[a];
                1 !== e.bondOrder || e.stereo !== f.Bond.STEREO_PROTRUDING && e.stereo !== f.Bond.STEREO_RECESSED || b.push(e)
            }
            a.sketcher.historyManager.pushUndo(new m.FlipAction(d, b, e))
        };
        this.buttonFlipVert = new l.Button(a.sketcher.id + "_button_flip_hor", d.FLIP_HOR, "Flip Horizontally", function() {
            e(!0)
        });
        this.buttonFlipHor = new l.Button(a.sketcher.id +
            "_button_flip_ver", d.FLIP_VER, "Flip Vertically",
            function() {
                e(!1)
            });
        this.flipSet = new l.ButtonSet(a.sketcher.id + "_buttons_flip");
        this.flipSet.toggle = !1;
        this.flipSet.buttons.push(this.buttonFlipVert);
        this.flipSet.buttons.push(this.buttonFlipHor)
    };
    h.makeHistorySet = function(a) {
        this.buttonUndo = new l.Button(a.sketcher.id + "_button_undo", d.UNDO, "Undo", function() {
            a.sketcher.historyManager.undo()
        });
        this.buttonRedo = new l.Button(a.sketcher.id + "_button_redo", d.REDO, "Redo", function() {
            a.sketcher.historyManager.redo()
        });
        this.historySet = new l.ButtonSet(a.sketcher.id + "_buttons_history");
        this.historySet.toggle = !1;
        this.historySet.buttons.push(this.buttonUndo);
        this.historySet.buttons.push(this.buttonRedo)
    };
    h.makeLabelSet = function(a) {
        this.buttonLabelH = new l.Button(a.sketcher.id + "_button_label_h", d.HYDROGEN, "Hydrogen", function() {
            a.sketcher.stateManager.setState(a.sketcher.stateManager.STATE_LABEL);
            a.sketcher.stateManager.STATE_LABEL.label = "H"
        });
        this.buttonLabelC = new l.Button(a.sketcher.id + "_button_label_c", d.CARBON, "Carbon",
            function() {
                a.sketcher.stateManager.setState(a.sketcher.stateManager.STATE_LABEL);
                a.sketcher.stateManager.STATE_LABEL.label = "C"
            });
        this.buttonLabelN = new l.Button(a.sketcher.id + "_button_label_n", d.NITROGEN, "Nitrogen", function() {
            a.sketcher.stateManager.setState(a.sketcher.stateManager.STATE_LABEL);
            a.sketcher.stateManager.STATE_LABEL.label = "N"
        });
        this.buttonLabelO = new l.Button(a.sketcher.id + "_button_label_o", d.OXYGEN, "Oxygen", function() {
            a.sketcher.stateManager.setState(a.sketcher.stateManager.STATE_LABEL);
            a.sketcher.stateManager.STATE_LABEL.label = "O"
        });
        this.buttonLabelF = new l.Button(a.sketcher.id + "_button_label_f", d.FLUORINE, "Fluorine", function() {
            a.sketcher.stateManager.setState(a.sketcher.stateManager.STATE_LABEL);
            a.sketcher.stateManager.STATE_LABEL.label = "F"
        });
        this.buttonLabelCl = new l.Button(a.sketcher.id + "_button_label_cl", d.CHLORINE, "Chlorine", function() {
            a.sketcher.stateManager.setState(a.sketcher.stateManager.STATE_LABEL);
            a.sketcher.stateManager.STATE_LABEL.label = "Cl"
        });
        this.buttonLabelBr = new l.Button(a.sketcher.id +
            "_button_label_br", d.BROMINE, "Bromine",
            function() {
                a.sketcher.stateManager.setState(a.sketcher.stateManager.STATE_LABEL);
                a.sketcher.stateManager.STATE_LABEL.label = "Br"
            });
        this.buttonLabelI = new l.Button(a.sketcher.id + "_button_label_i", d.IODINE, "Iodine", function() {
            a.sketcher.stateManager.setState(a.sketcher.stateManager.STATE_LABEL);
            a.sketcher.stateManager.STATE_LABEL.label = "I"
        });
        this.buttonLabelP = new l.Button(a.sketcher.id + "_button_label_p", d.PHOSPHORUS, "Phosphorus", function() {
            a.sketcher.stateManager.setState(a.sketcher.stateManager.STATE_LABEL);
            a.sketcher.stateManager.STATE_LABEL.label = "P"
        });
        this.buttonLabelS = new l.Button(a.sketcher.id + "_button_label_s", d.SULFUR, "Sulfur", function() {
            a.sketcher.stateManager.setState(a.sketcher.stateManager.STATE_LABEL);
            a.sketcher.stateManager.STATE_LABEL.label = "S"
        });
        this.buttonLabelSi = new l.Button(a.sketcher.id + "_button_label_si", d.SILICON, "Silicon", function() {
            a.sketcher.stateManager.setState(a.sketcher.stateManager.STATE_LABEL);
            a.sketcher.stateManager.STATE_LABEL.label = "Si"
        });
        this.buttonLabelPT = new l.Button(a.sketcher.id +
            "_button_label_pt", d.PERIODIC_TABLE, "Choose Symbol",
            function() {
                a.sketcher.dialogManager.periodicTableDialog.canvas.selected && (a.sketcher.stateManager.setState(a.sketcher.stateManager.STATE_LABEL), a.sketcher.stateManager.STATE_LABEL.label = a.sketcher.dialogManager.periodicTableDialog.canvas.selected.element.symbol);
                a.sketcher.dialogManager.periodicTableDialog.open()
            });
        this.buttonLabel = new l.DummyButton(a.sketcher.id + "_button_label", "Set Label");
        a.sketcher.floatDrawTools ? (this.labelTray = new l.Tray(a.sketcher,
                a.sketcher.id + "_buttons_label", this.buttonLabel, 3), this.labelTray.defaultButton = this.buttonLabelO, this.labelTray.buttonSet.buttons.push(this.buttonLabelH), this.labelTray.buttonSet.buttons.push(this.buttonLabelC), this.labelTray.buttonSet.buttons.push(this.buttonLabelN), this.labelTray.buttonSet.buttons.push(this.buttonLabelO), this.labelTray.buttonSet.buttons.push(this.buttonLabelF), this.labelTray.buttonSet.buttons.push(this.buttonLabelCl), this.labelTray.buttonSet.buttons.push(this.buttonLabelBr), this.labelTray.buttonSet.buttons.push(this.buttonLabelI),
            this.labelTray.buttonSet.buttons.push(this.buttonLabelP), this.labelTray.buttonSet.buttons.push(this.buttonLabelS), this.labelTray.buttonSet.buttons.push(this.buttonLabelSi), this.labelTray.buttonSet.buttons.push(this.buttonLabelPT), this.drawTools.components.push(this.labelTray)) : (this.labelSet = new l.ButtonSet(a.sketcher.id + "_buttons_label"), this.labelSet.buttons.push(this.buttonLabel), this.labelSet.addDropDown("More Labels"), this.labelSet.dropDown.defaultButton = this.buttonLabelO, this.labelSet.dropDown.buttonSet.buttons.push(this.buttonLabelH),
            this.labelSet.dropDown.buttonSet.buttons.push(this.buttonLabelC), this.labelSet.dropDown.buttonSet.buttons.push(this.buttonLabelN), this.labelSet.dropDown.buttonSet.buttons.push(this.buttonLabelO), this.labelSet.dropDown.buttonSet.buttons.push(this.buttonLabelF), this.labelSet.dropDown.buttonSet.buttons.push(this.buttonLabelCl), this.labelSet.dropDown.buttonSet.buttons.push(this.buttonLabelBr), this.labelSet.dropDown.buttonSet.buttons.push(this.buttonLabelI), this.labelSet.dropDown.buttonSet.buttons.push(this.buttonLabelP),
            this.labelSet.dropDown.buttonSet.buttons.push(this.buttonLabelS), this.labelSet.dropDown.buttonSet.buttons.push(this.buttonLabelSi), this.labelSet.dropDown.buttonSet.buttons.push(this.buttonLabelPT))
    };
    h.makeBondSet = function(a) {
        this.buttonSingle = new l.Button(a.sketcher.id + "_button_bond_single", d.BOND_SINGLE, "Single Bond", function() {
            a.sketcher.stateManager.setState(a.sketcher.stateManager.STATE_NEW_BOND);
            a.sketcher.stateManager.STATE_NEW_BOND.bondOrder = 1;
            a.sketcher.stateManager.STATE_NEW_BOND.stereo =
                f.Bond.STEREO_NONE
        });
        this.buttonRecessed = new l.Button(a.sketcher.id + "_button_bond_recessed", d.BOND_RECESSED, "Recessed Bond", function() {
            a.sketcher.stateManager.setState(a.sketcher.stateManager.STATE_NEW_BOND);
            a.sketcher.stateManager.STATE_NEW_BOND.bondOrder = 1;
            a.sketcher.stateManager.STATE_NEW_BOND.stereo = f.Bond.STEREO_RECESSED
        });
        this.buttonProtruding = new l.Button(a.sketcher.id + "_button_bond_protruding", d.BOND_PROTRUDING, "Protruding Bond", function() {
            a.sketcher.stateManager.setState(a.sketcher.stateManager.STATE_NEW_BOND);
            a.sketcher.stateManager.STATE_NEW_BOND.bondOrder = 1;
            a.sketcher.stateManager.STATE_NEW_BOND.stereo = f.Bond.STEREO_PROTRUDING
        });
        this.buttonDouble = new l.Button(a.sketcher.id + "_button_bond_double", d.BOND_DOUBLE, "Double Bond", function() {
            a.sketcher.stateManager.setState(a.sketcher.stateManager.STATE_NEW_BOND);
            a.sketcher.stateManager.STATE_NEW_BOND.bondOrder = 2;
            a.sketcher.stateManager.STATE_NEW_BOND.stereo = f.Bond.STEREO_NONE
        });
        this.buttonZero = new l.Button(a.sketcher.id + "_button_bond_zero", d.BOND_ZERO, "Zero Bond (Ionic/Hydrogen)",
            function() {
                a.sketcher.stateManager.setState(a.sketcher.stateManager.STATE_NEW_BOND);
                a.sketcher.stateManager.STATE_NEW_BOND.bondOrder = 0;
                a.sketcher.stateManager.STATE_NEW_BOND.stereo = f.Bond.STEREO_NONE
            });
        this.buttonCovalent = new l.Button(a.sketcher.id + "_button_bond_covalent", d.BOND_COVALENT, "Covalent Bond", function() {
            a.sketcher.stateManager.setState(a.sketcher.stateManager.STATE_NEW_BOND);
            a.sketcher.stateManager.STATE_NEW_BOND.bondOrder = 0;
            a.sketcher.stateManager.STATE_NEW_BOND.stereo = f.Bond.STEREO_PROTRUDING
        });
        this.buttonHalf = new l.Button(a.sketcher.id + "_button_bond_half", d.BOND_HALF, "Half Bond", function() {
            a.sketcher.stateManager.setState(a.sketcher.stateManager.STATE_NEW_BOND);
            a.sketcher.stateManager.STATE_NEW_BOND.bondOrder = .5;
            a.sketcher.stateManager.STATE_NEW_BOND.stereo = f.Bond.STEREO_NONE
        });
        this.buttonWavy = new l.Button(a.sketcher.id + "_button_bond_wavy", d.BOND_WAVY, "Wavy Bond", function() {
            a.sketcher.stateManager.setState(a.sketcher.stateManager.STATE_NEW_BOND);
            a.sketcher.stateManager.STATE_NEW_BOND.bondOrder =
                1;
            a.sketcher.stateManager.STATE_NEW_BOND.stereo = f.Bond.STEREO_AMBIGUOUS
        });
        this.buttonResonance = new l.Button(a.sketcher.id + "_button_bond_resonance", d.BOND_RESONANCE, "Resonance Bond", function() {
            a.sketcher.stateManager.setState(a.sketcher.stateManager.STATE_NEW_BOND);
            a.sketcher.stateManager.STATE_NEW_BOND.bondOrder = 1.5;
            a.sketcher.stateManager.STATE_NEW_BOND.stereo = f.Bond.STEREO_NONE
        });
        this.buttonDoubleAmbiguous = new l.Button(a.sketcher.id + "_button_bond_ambiguous_double", d.BOND_DOUBLE_AMBIGUOUS, "Ambiguous Double Bond",
            function() {
                a.sketcher.stateManager.setState(a.sketcher.stateManager.STATE_NEW_BOND);
                a.sketcher.stateManager.STATE_NEW_BOND.bondOrder = 2;
                a.sketcher.stateManager.STATE_NEW_BOND.stereo = f.Bond.STEREO_AMBIGUOUS
            });
        this.buttonTriple = new l.Button(a.sketcher.id + "_button_bond_triple", d.BOND_TRIPLE, "Triple Bond", function() {
            a.sketcher.stateManager.setState(a.sketcher.stateManager.STATE_NEW_BOND);
            a.sketcher.stateManager.STATE_NEW_BOND.bondOrder = 3;
            a.sketcher.stateManager.STATE_NEW_BOND.stereo = f.Bond.STEREO_NONE
        });
        this.buttonBond = new l.DummyButton(a.sketcher.id + "_button_bond", a.sketcher.floatDrawTools ? "Draw Bond" : "Other Bond");
        a.sketcher.floatDrawTools ? (this.bondTray = new l.Tray(a.sketcher, a.sketcher.id + "_buttons_bond", this.buttonBond, 2), this.bondTray.defaultButton = this.buttonSingle, this.bondTray.buttonSet.buttons.push(this.buttonZero), this.bondTray.buttonSet.buttons.push(this.buttonCovalent), this.bondTray.buttonSet.buttons.push(this.buttonHalf), this.bondTray.buttonSet.buttons.push(this.buttonSingle), this.bondTray.buttonSet.buttons.push(this.buttonRecessed),
            this.bondTray.buttonSet.buttons.push(this.buttonProtruding), this.bondTray.buttonSet.buttons.push(this.buttonWavy), this.bondTray.buttonSet.buttons.push(this.buttonResonance), this.bondTray.buttonSet.buttons.push(this.buttonDoubleAmbiguous), this.bondTray.buttonSet.buttons.push(this.buttonDouble), this.bondTray.buttonSet.buttons.push(this.buttonTriple), this.drawTools.components.push(this.bondTray)) : (this.bondSet = new l.ButtonSet(a.sketcher.id + "_buttons_bond"), this.bondSet.buttons.push(this.buttonSingle),
            this.bondSet.buttons.push(this.buttonRecessed), this.bondSet.buttons.push(this.buttonProtruding), this.bondSet.buttons.push(this.buttonDouble), this.bondSet.buttons.push(this.buttonBond), this.bondSet.addDropDown("More Bonds"), this.bondSet.dropDown.buttonSet.buttons.push(this.buttonZero), this.bondSet.dropDown.buttonSet.buttons.push(this.buttonCovalent), this.bondSet.dropDown.buttonSet.buttons.push(this.buttonHalf), this.bondSet.dropDown.buttonSet.buttons.push(this.buttonWavy), this.bondSet.dropDown.buttonSet.buttons.push(this.buttonResonance),
            this.bondSet.dropDown.buttonSet.buttons.push(this.buttonDoubleAmbiguous), this.bondSet.dropDown.buttonSet.buttons.push(this.buttonTriple), this.bondSet.dropDown.defaultButton = this.buttonTriple)
    };
    h.makeRingSet = function(a) {
        this.buttonCyclohexane = new l.Button(a.sketcher.id + "_button_ring_cyclohexane", d.CYCLOHEXANE, "Cyclohexane Ring", function() {
            a.sketcher.stateManager.setState(a.sketcher.stateManager.STATE_NEW_RING);
            a.sketcher.stateManager.STATE_NEW_RING.numSides = 6;
            a.sketcher.stateManager.STATE_NEW_RING.unsaturated = !1
        });
        this.buttonBenzene = new l.Button(a.sketcher.id + "_button_ring_benzene", d.BENZENE, "Benzene Ring", function() {
            a.sketcher.stateManager.setState(a.sketcher.stateManager.STATE_NEW_RING);
            a.sketcher.stateManager.STATE_NEW_RING.numSides = 6;
            a.sketcher.stateManager.STATE_NEW_RING.unsaturated = !0
        });
        this.buttonCyclopropane = new l.Button(a.sketcher.id + "_button_ring_cyclopropane", d.CYCLOPROPANE, "Cyclopropane Ring", function() {
            a.sketcher.stateManager.setState(a.sketcher.stateManager.STATE_NEW_RING);
            a.sketcher.stateManager.STATE_NEW_RING.numSides =
                3;
            a.sketcher.stateManager.STATE_NEW_RING.unsaturated = !1
        });
        this.buttonCyclobutane = new l.Button(a.sketcher.id + "_button_ring_cyclobutane", d.CYCLOBUTANE, "Cyclobutane Ring", function() {
            a.sketcher.stateManager.setState(a.sketcher.stateManager.STATE_NEW_RING);
            a.sketcher.stateManager.STATE_NEW_RING.numSides = 4;
            a.sketcher.stateManager.STATE_NEW_RING.unsaturated = !1
        });
        this.buttonCyclopentane = new l.Button(a.sketcher.id + "_button_ring_cyclopentane", d.CYCLOPENTANE, "Cyclopentane Ring", function() {
            a.sketcher.stateManager.setState(a.sketcher.stateManager.STATE_NEW_RING);
            a.sketcher.stateManager.STATE_NEW_RING.numSides = 5;
            a.sketcher.stateManager.STATE_NEW_RING.unsaturated = !1
        });
        this.buttonCycloheptane = new l.Button(a.sketcher.id + "_button_ring_cycloheptane", d.CYCLOHEPTANE, "Cycloheptane Ring", function() {
            a.sketcher.stateManager.setState(a.sketcher.stateManager.STATE_NEW_RING);
            a.sketcher.stateManager.STATE_NEW_RING.numSides = 7;
            a.sketcher.stateManager.STATE_NEW_RING.unsaturated = !1
        });
        this.buttonCyclooctane = new l.Button(a.sketcher.id + "_button_ring_cyclooctane", d.CYCLOOCTANE,
            "Cyclooctane Ring",
            function() {
                a.sketcher.stateManager.setState(a.sketcher.stateManager.STATE_NEW_RING);
                a.sketcher.stateManager.STATE_NEW_RING.numSides = 8;
                a.sketcher.stateManager.STATE_NEW_RING.unsaturated = !1
            });
        this.buttonRingArbitrary = new l.Button(a.sketcher.id + "_button_ring_arbitrary", d.RING_ARBITRARY, "Arbitrary Ring Size Tool", function() {
            a.sketcher.stateManager.setState(a.sketcher.stateManager.STATE_NEW_RING);
            a.sketcher.stateManager.STATE_NEW_RING.numSides = -1;
            a.sketcher.stateManager.STATE_NEW_RING.unsaturated = !1
        });
        this.buttonRing = new l.DummyButton(a.sketcher.id + "_button_ring", a.sketcher.floatDrawTools ? "Draw Ring" : "Other Ring");
        a.sketcher.floatDrawTools ? (this.ringTray = new l.Tray(a.sketcher, a.sketcher.id + "_buttons_ring", this.buttonRing, 2), this.ringTray.defaultButton = this.buttonCyclohexane, this.ringTray.buttonSet.buttons.push(this.buttonCyclopropane), this.ringTray.buttonSet.buttons.push(this.buttonCyclobutane), this.ringTray.buttonSet.buttons.push(this.buttonCyclopentane), this.ringTray.buttonSet.buttons.push(this.buttonCyclohexane),
            this.ringTray.buttonSet.buttons.push(this.buttonCycloheptane), this.ringTray.buttonSet.buttons.push(this.buttonCyclooctane), this.ringTray.buttonSet.buttons.push(this.buttonBenzene), this.ringTray.buttonSet.buttons.push(this.buttonRingArbitrary), this.drawTools.components.push(this.ringTray)) : (this.ringSet = new l.ButtonSet(a.sketcher.id + "_buttons_ring"), this.ringSet.buttons.push(this.buttonCyclohexane), this.ringSet.buttons.push(this.buttonBenzene), this.ringSet.buttons.push(this.buttonRing), this.ringSet.addDropDown("More Rings"),
            this.ringSet.dropDown.buttonSet.buttons.push(this.buttonCyclopropane), this.ringSet.dropDown.buttonSet.buttons.push(this.buttonCyclobutane), this.ringSet.dropDown.buttonSet.buttons.push(this.buttonCyclopentane), this.ringSet.dropDown.defaultButton = this.buttonCyclopentane, this.ringSet.dropDown.buttonSet.buttons.push(this.buttonCycloheptane), this.ringSet.dropDown.buttonSet.buttons.push(this.buttonCyclooctane), this.ringSet.dropDown.buttonSet.buttons.push(this.buttonRingArbitrary))
    };
    h.makeAttributeSet = function(a) {
        this.buttonChargePlus =
            new l.Button(a.sketcher.id + "_button_attribute_charge_increment", d.INCREASE_CHARGE, "Increase Charge", function() {
                a.sketcher.stateManager.setState(a.sketcher.stateManager.STATE_CHARGE);
                a.sketcher.stateManager.STATE_CHARGE.delta = 1
            });
        this.buttonChargeMinus = new l.Button(a.sketcher.id + "_button_attribute_charge_decrement", d.DECREASE_CHARGE, "Decrease Charge", function() {
            a.sketcher.stateManager.setState(a.sketcher.stateManager.STATE_CHARGE);
            a.sketcher.stateManager.STATE_CHARGE.delta = -1
        });
        this.buttonPairPlus =
            new l.Button(a.sketcher.id + "_button_attribute_lonePair_increment", d.ADD_LONE_PAIR, "Add Lone Pair", function() {
                a.sketcher.stateManager.setState(a.sketcher.stateManager.STATE_LONE_PAIR);
                a.sketcher.stateManager.STATE_LONE_PAIR.delta = 1
            });
        this.buttonPairMinus = new l.Button(a.sketcher.id + "_button_attribute_lonePair_decrement", d.REMOVE_LONE_PAIR, "Remove Lone Pair", function() {
            a.sketcher.stateManager.setState(a.sketcher.stateManager.STATE_LONE_PAIR);
            a.sketcher.stateManager.STATE_LONE_PAIR.delta = -1
        });
        this.buttonRadicalPlus =
            new l.Button(a.sketcher.id + "_button_attribute_radical_increment", d.ADD_RADICAL, "Add Radical", function() {
                a.sketcher.stateManager.setState(a.sketcher.stateManager.STATE_RADICAL);
                a.sketcher.stateManager.STATE_RADICAL.delta = 1
            });
        this.buttonRadicalMinus = new l.Button(a.sketcher.id + "_button_attribute_radical_decrement", d.REMOVE_RADICAL, "Remove Radical", function() {
            a.sketcher.stateManager.setState(a.sketcher.stateManager.STATE_RADICAL);
            a.sketcher.stateManager.STATE_RADICAL.delta = -1
        });
        this.buttonIsotope = new l.Button(a.sketcher.id +
            "_button_attribute_isotope", d.ISOTOPE, "Set Isotope Value",
            function() {
                a.sketcher.stateManager.setState(a.sketcher.stateManager.STATE_ISOTOPE)
            });
        this.buttonAttribute = new l.DummyButton(a.sketcher.id + "_button_attribute", "Attributes");
        a.sketcher.floatDrawTools ? (this.attributeTray = new l.Tray(a.sketcher, a.sketcher.id + "_buttons_attribute", this.buttonAttribute, 2), this.attributeTray.defaultButton = this.buttonChargePlus, this.attributeTray.buttonSet.buttons.push(this.buttonChargeMinus), this.attributeTray.buttonSet.buttons.push(this.buttonChargePlus),
            this.attributeTray.buttonSet.buttons.push(this.buttonPairMinus), this.attributeTray.buttonSet.buttons.push(this.buttonPairPlus), this.attributeTray.buttonSet.buttons.push(this.buttonRadicalMinus), this.attributeTray.buttonSet.buttons.push(this.buttonRadicalPlus), this.attributeTray.buttonSet.buttons.push(this.buttonIsotope), this.drawTools.components.push(this.attributeTray)) : (this.attributeSet = new l.ButtonSet(a.sketcher.id + "_buttons_attribute"), this.attributeSet.buttons.push(this.buttonAttribute), this.attributeSet.addDropDown("More Attributes"),
            this.attributeSet.dropDown.buttonSet.buttons.push(this.buttonChargePlus), this.attributeSet.dropDown.buttonSet.buttons.push(this.buttonChargeMinus), this.attributeSet.dropDown.buttonSet.buttons.push(this.buttonPairPlus), this.attributeSet.dropDown.buttonSet.buttons.push(this.buttonPairMinus), this.attributeSet.dropDown.buttonSet.buttons.push(this.buttonRadicalPlus), this.attributeSet.dropDown.buttonSet.buttons.push(this.buttonRadicalMinus), this.attributeSet.dropDown.buttonSet.buttons.push(this.buttonIsotope))
    };
    h.makeShapeSet = function(a) {
        this.buttonArrowSynthetic = new l.Button(a.sketcher.id + "_button_shape_arrow_synthetic", d.ARROW_SYNTHETIC, "Synthetic Arrow", function() {
            a.sketcher.stateManager.setState(a.sketcher.stateManager.STATE_SHAPE);
            a.sketcher.stateManager.STATE_SHAPE.shapeType = q.ShapeState.ARROW_SYNTHETIC
        });
        this.buttonArrowRetrosynthetic = new l.Button(a.sketcher.id + "_button_shape_arrow_retrosynthetic", d.ARROW_RETROSYNTHETIC, "Retrosynthetic Arrow", function() {
            a.sketcher.stateManager.setState(a.sketcher.stateManager.STATE_SHAPE);
            a.sketcher.stateManager.STATE_SHAPE.shapeType = q.ShapeState.ARROW_RETROSYNTHETIC
        });
        this.buttonArrowResonance = new l.Button(a.sketcher.id + "_button_shape_arrow_resonance", d.ARROW_RESONANCE, "Resonance Arrow", function() {
            a.sketcher.stateManager.setState(a.sketcher.stateManager.STATE_SHAPE);
            a.sketcher.stateManager.STATE_SHAPE.shapeType = q.ShapeState.ARROW_RESONANCE
        });
        this.buttonArrowEquilibrum = new l.Button(a.sketcher.id + "_button_shape_arrow_equilibrium", d.ARROW_EQUILIBRIUM, "Equilibrium Arrow", function() {
            a.sketcher.stateManager.setState(a.sketcher.stateManager.STATE_SHAPE);
            a.sketcher.stateManager.STATE_SHAPE.shapeType = q.ShapeState.ARROW_EQUILIBRIUM
        });
        this.buttonReactionMapping = new l.Button(a.sketcher.id + "_button_reaction_mapping", d.ATOM_REACTION_MAP, "Reaction Mapping", function() {
            a.sketcher.stateManager.setState(a.sketcher.stateManager.STATE_PUSHER);
            a.sketcher.stateManager.STATE_PUSHER.numElectron = -10
        });
        this.buttonPusher1 = new l.Button(a.sketcher.id + "_button_shape_pusher_1", d.PUSHER_SINGLE, "Single Electron Pusher", function() {
            a.sketcher.stateManager.setState(a.sketcher.stateManager.STATE_PUSHER);
            a.sketcher.stateManager.STATE_PUSHER.numElectron = 1
        });
        this.buttonPusher2 = new l.Button(a.sketcher.id + "_button_shape_pusher_2", d.PUSHER_DOUBLE, "Electron Pair Pusher", function() {
            a.sketcher.stateManager.setState(a.sketcher.stateManager.STATE_PUSHER);
            a.sketcher.stateManager.STATE_PUSHER.numElectron = 2
        });
        this.buttonPusherBond = new l.Button(a.sketcher.id + "_button_shape_pusher_bond_forming", d.PUSHER_BOND_FORMING, "Bond Forming Pusher", function() {
            a.sketcher.stateManager.setState(a.sketcher.stateManager.STATE_PUSHER);
            a.sketcher.stateManager.STATE_PUSHER.numElectron = -1
        });
        this.buttonReactionMapping = new l.Button(a.sketcher.id + "_button_reaction_mapping", d.ATOM_REACTION_MAP, "Reaction Mapping", function() {
            a.sketcher.stateManager.setState(a.sketcher.stateManager.STATE_PUSHER);
            a.sketcher.stateManager.STATE_PUSHER.numElectron = -10
        });
        this.buttonBracket = new l.Button(a.sketcher.id + "_button_shape_charge_bracket", d.BRACKET_CHARGE, "Bracket", function() {
            a.sketcher.stateManager.setState(a.sketcher.stateManager.STATE_SHAPE);
            a.sketcher.stateManager.STATE_SHAPE.shapeType =
                q.ShapeState.BRACKET;
            a.sketcher.repaint()
        });
        this.buttonRepeatUnit = new l.Button(a.sketcher.id + "_button_repeat_unit", d.BRACKET_REPEAT_UNIT, "Repeat Unit", function() {
            a.sketcher.stateManager.setState(a.sketcher.stateManager.STATE_REPEAT_UNIT)
        });
        this.buttonVAP = new l.Button(a.sketcher.id + "_button_vap", d.VARIABLE_ATTACHMENT_POINTS, "Variable Attachment Points", function() {
            a.sketcher.stateManager.setState(a.sketcher.stateManager.STATE_VAP)
        });
        this.sketcher.oneMolecule || (this.buttonShape = new l.DummyButton(a.sketcher.id +
            "_button_shape", a.sketcher.floatDrawTools ? "Reactions" : "Shapes"), a.sketcher.floatDrawTools ? (this.buttonVAP.toggle = !0, this.shapeTray = new l.Tray(a.sketcher, a.sketcher.id + "_buttons_shape", this.buttonShape, 4), this.shapeTray.defaultButton = this.buttonArrowSynthetic, this.shapeTray.buttonSet.buttons.push(this.buttonArrowSynthetic), this.shapeTray.buttonSet.buttons.push(this.buttonArrowRetrosynthetic), this.shapeTray.buttonSet.buttons.push(this.buttonArrowResonance), this.shapeTray.buttonSet.buttons.push(this.buttonArrowEquilibrum),
            this.shapeTray.buttonSet.buttons.push(this.buttonPusher1), this.shapeTray.buttonSet.buttons.push(this.buttonPusher2), this.shapeTray.buttonSet.buttons.push(this.buttonPusherBond), this.shapeTray.buttonSet.buttons.push(this.buttonReactionMapping), this.drawTools.components.push(this.shapeTray), this.buttonBrackets = new l.DummyButton(a.sketcher.id + "_button_bracket", "Brackets"), this.bracketTray = new l.Tray(a.sketcher, a.sketcher.id + "_buttons_bracket", this.buttonBrackets, 2), this.bracketTray.buttonSet.buttons.push(this.buttonBracket),
            this.bracketTray.buttonSet.buttons.push(this.buttonRepeatUnit), this.drawTools.components.push(this.bracketTray)) : (this.shapeSet = new l.ButtonSet(a.sketcher.id + "_buttons_shape"), this.shapeSet.buttons.push(this.buttonShape), this.shapeSet.addDropDown("More Shapes"), this.shapeSet.dropDown.buttonSet.buttons.push(this.buttonArrowSynthetic), this.shapeSet.dropDown.buttonSet.buttons.push(this.buttonArrowRetrosynthetic), this.shapeSet.dropDown.buttonSet.buttons.push(this.buttonArrowResonance), this.shapeSet.dropDown.buttonSet.buttons.push(this.buttonArrowEquilibrum),
            this.shapeSet.dropDown.buttonSet.buttons.push(this.buttonPusher1), this.shapeSet.dropDown.buttonSet.buttons.push(this.buttonPusher2), this.shapeSet.dropDown.buttonSet.buttons.push(this.buttonPusherBond), this.shapeSet.dropDown.buttonSet.buttons.push(this.buttonReactionMapping), this.shapeSet.dropDown.buttonSet.buttons.push(this.buttonBracket), this.shapeSet.dropDown.buttonSet.buttons.push(this.buttonRepeatUnit), this.shapeSet.dropDown.buttonSet.buttons.push(this.buttonVAP)))
    }
})(ChemDoodle, ChemDoodle.iChemLabs,
    ChemDoodle.io, ChemDoodle.structures, ChemDoodle.uis.actions, ChemDoodle.uis.gui, ChemDoodle.uis.gui.imageDepot, ChemDoodle.uis.gui.desktop, ChemDoodle.uis.tools, ChemDoodle.uis.states, ChemDoodle.lib.jQuery, document);
(function(g, a, p, f) {
    g.CursorManager = function(a) {
        this.sketcher = a;
        this.currentCursor = this.lastCursor = f
    };
    g.CursorManager.POINTER = "default";
    g.CursorManager.CROSSHAIR = "crosshair";
    g.CursorManager.TEXT = "text";
    p = -1 !== p.navigator.userAgent.indexOf("Trident/");
    g.CursorManager.HAND_OPEN = p ? "move" : "grab";
    g.CursorManager.HAND_CLOSE = p ? "move" : "grabbing";
    g.CursorManager.HAND_POINT = "pointer";
    g.CursorManager.LASSO = "default";
    g.CursorManager.ROTATE = "alias";
    g.CursorManager.RESIZE = "move";
    g.CursorManager.ERASER = "cell";
    g =
        g.CursorManager.prototype;
    g.setCursor = function(f) {
        this.sketcher.isMobile || this.currentCursor === f || (this.lastCursor = this.currentCursor, this.currentCursor = f, a("#" + this.sketcher.id).css("cursor", f))
    };
    g.setPreviousCursor = function() {
        this.sketcher.isMobile || this.lastCursor === f || this.lastCursor === this.currentCursor || (this.currentCursor = this.lastCursor, a("#" + this.sketcher.id).css("cursor", this.lastCursor))
    };
    g.getCurrentCursor = function() {
        return this.currentCursor
    }
})(ChemDoodle.uis.gui.desktop, ChemDoodle.lib.jQuery,
    window);
(function(g, a, p, f, m) {
    f.Lasso = function(a) {
        this.sketcher = a;
        this.atoms = [];
        this.shapes = [];
        this.bounds = m;
        this.mode = f.Lasso.MODE_LASSO;
        this.points = []
    };
    f.Lasso.MODE_LASSO = "lasso";
    f.Lasso.MODE_LASSO_SHAPES = "shapes";
    f.Lasso.MODE_RECTANGLE_MARQUEE = "rectangle";
    let h = f.Lasso.prototype;
    h.select = function(d, h) {
        if (!this.block) {
            a.SHIFT || this.empty();
            if (d) this.atoms = d.slice(0), this.shapes = h.slice(0);
            else {
                if (this.mode !== f.Lasso.MODE_LASSO_SHAPES) {
                    d = [];
                    for (let a = 0, m = this.sketcher.molecules.length; a < m; a++) {
                        h = this.sketcher.molecules[a];
                        for (let a = 0, m = h.atoms.length; a < m; a++) {
                            var l = h.atoms[a];
                            this.mode === f.Lasso.MODE_RECTANGLE_MARQUEE ? 2 === this.points.length && g.isBetween(l.x, this.points[0].x, this.points[1].x) && g.isBetween(l.y, this.points[0].y, this.points[1].y) && d.push(l) : 1 < this.points.length && g.isPointInPoly(this.points, l) && d.push(l)
                        }
                    }
                    if (0 === this.atoms.length) this.atoms = d;
                    else {
                        h = [];
                        for (let a = 0, f = this.atoms.length; a < f; a++) l = this.atoms[a], -1 === d.indexOf(l) ? h.push(l) : l.isLassoed = !1;
                        for (let a = 0, f = d.length; a < f; a++) - 1 === this.atoms.indexOf(d[a]) &&
                            h.push(d[a]);
                        this.atoms = h
                    }
                }
                d = [];
                for (let a = 0, m = this.sketcher.shapes.length; a < m; a++) {
                    h = this.sketcher.shapes[a];
                    l = h.getPoints();
                    let n = 0 < l.length;
                    for (let a = 0, e = l.length; a < e; a++) {
                        let e = l[a];
                        if (this.mode === f.Lasso.MODE_RECTANGLE_MARQUEE)
                            if (2 === this.points.length) {
                                if (!g.isBetween(e.x, this.points[0].x, this.points[1].x) || !g.isBetween(e.y, this.points[0].y, this.points[1].y)) {
                                    n = !1;
                                    break
                                }
                            } else {
                                n = !1;
                                break
                            }
                        else if (1 < this.points.length) {
                            if (!g.isPointInPoly(this.points, e)) {
                                n = !1;
                                break
                            }
                        } else {
                            n = !1;
                            break
                        }
                    }
                    n && d.push(h)
                }
                if (0 ===
                    this.shapes.length) this.shapes = d;
                else {
                    h = [];
                    for (let a = 0, f = this.shapes.length; a < f; a++) l = this.shapes[a], -1 === d.indexOf(l) ? asFinal.push(l) : l.isLassoed = !1;
                    for (let a = 0, f = d.length; a < f; a++) - 1 === this.shapes.indexOf(d[a]) && h.push(d[a]);
                    this.shapes = h
                }
            }
            for (let a = 0, d = this.atoms.length; a < d; a++) this.atoms[a].isLassoed = !0;
            for (let a = 0, d = this.shapes.length; a < d; a++) this.shapes[a].isLassoed = !0;
            this.setBounds();
            this.bounds && Infinity === this.bounds.minX && this.empty();
            this.points = [];
            this.sketcher.stateManager.getCurrentState().clearHover();
            this.enableButtons();
            this.sketcher.repaint()
        }
    };
    h.enableButtons = function() {
        this.sketcher.useServices && (0 < this.atoms.length ? (this.sketcher.toolbarManager.buttonClean.enable(), this.sketcher.toolbarManager.buttonCalculate.enable()) : (this.sketcher.toolbarManager.buttonClean.disable(), this.sketcher.toolbarManager.buttonCalculate.disable()));
        0 < this.atoms.length || 0 < this.shapes.length ? (this.sketcher.toolbarManager.buttonCut.enable(), this.sketcher.toolbarManager.buttonCopy.enable(),
            this.sketcher.toolbarManager.buttonFlipVert.enable(), this.sketcher.toolbarManager.buttonFlipHor.enable()) : (this.sketcher.toolbarManager.buttonCut.disable(), this.sketcher.toolbarManager.buttonCopy.disable(), this.sketcher.toolbarManager.buttonFlipVert.disable(), this.sketcher.toolbarManager.buttonFlipHor.disable())
    };
    h.setBounds = function() {
        if (this.isActive()) {
            this.sketcher.repaint();
            this.bounds = new g.Bounds;
            for (let a = 0, f = this.atoms.length; a < f; a++) this.bounds.expand(this.atoms[a].getBounds());
            for (let a = 0, f = this.shapes.length; a < f; a++) this.bounds.expand(this.shapes[a].getBounds());
            this.bounds.minX -= 5;
            this.bounds.minY -= 5;
            this.bounds.maxX += 5;
            this.bounds.maxY += 5
        } else this.bounds = m
    };
    h.empty = function() {
        for (let a = 0, f = this.atoms.length; a < f; a++) this.atoms[a].isLassoed = !1;
        for (let a = 0, f = this.shapes.length; a < f; a++) this.shapes[a].isLassoed = !1;
        this.atoms = [];
        this.shapes = [];
        this.bounds = m;
        this.enableButtons();
        this.sketcher.repaint()
    };
    h.draw = function(a, h) {
        a.strokeStyle = h.colorSelect;
        a.lineWidth = .5 / h.scale;
        a.setLineDash([5]);
        if (0 < this.points.length)
            if (this.mode === f.Lasso.MODE_RECTANGLE_MARQUEE) {
                if (2 === this.points.length) {
                    h = this.points[0];
                    let d = this.points[1];
                    a.beginPath();
                    a.rect(h.x, h.y, d.x - h.x, d.y - h.y);
                    a.stroke()
                }
            } else if (1 < this.points.length) {
            a.beginPath();
            a.moveTo(this.points[0].x, this.points[0].y);
            for (let d = 1, f = this.points.length; d < f; d++) a.lineTo(this.points[d].x, this.points[d].y);
            a.closePath();
            a.stroke()
        }
        this.bounds && (a.beginPath(), a.rect(this.bounds.minX, this.bounds.minY, this.bounds.maxX - this.bounds.minX,
            this.bounds.maxY - this.bounds.minY), a.stroke());
        a.setLineDash([])
    };
    h.isActive = function() {
        return 0 < this.atoms.length || 0 < this.shapes.length
    };
    h.getFirstMolecule = function() {
        return 0 < this.atoms.length ? this.sketcher.getMoleculeByAtom(this.atoms[0]) : m
    };
    h.getBonds = function() {
        let a = [];
        if (0 < this.atoms.length)
            for (let d = 0, f = this.sketcher.molecules.length; d < f; d++) {
                let f = this.sketcher.molecules[d];
                for (let d = 0, h = f.bonds.length; d < h; d++) {
                    let h = f.bonds[d];
                    h.a1.isLassoed && h.a2.isLassoed && a.push(h)
                }
            }
        return a
    };
    h.getAllPoints =
        function() {
            let a = this.atoms;
            for (let d = 0, f = this.shapes.length; d < f; d++) a = a.concat(this.shapes[d].getPoints());
            return a
        };
    h.addPoint = function(a) {
        if (this.mode === f.Lasso.MODE_RECTANGLE_MARQUEE)
            if (2 > this.points.length) this.points.push(a);
            else {
                let d = this.points[1];
                d.x = a.x;
                d.y = a.y
            }
        else this.points.push(a)
    };
    h.selectNextMolecule = function() {
        if (0 < this.sketcher.molecules.length) {
            var a = this.sketcher.molecules.length - 1;
            0 < this.atoms.length && (a = this.sketcher.getMoleculeByAtom(this.atoms[0]), a = this.sketcher.molecules.indexOf(a) +
                1);
            a === this.sketcher.molecules.length && (a = 0);
            a = this.sketcher.molecules[a];
            let d = [];
            for (let f = 0, h = this.sketcher.shapes.length; f < h; f++) {
                let h = this.sketcher.shapes[f];
                h instanceof p.d2.RepeatUnit && 0 !== h.contents.length && -1 !== a.atoms.indexOf(h.contents[0]) && d.push(h)
            }
            this.select(a.atoms, d)
        }
    };
    h.selectNextShape = function() {
        if (0 < this.sketcher.shapes.length) {
            let a = this.sketcher.shapes.length - 1;
            0 < this.shapes.length && (a = this.sketcher.shapes.indexOf(this.shapes[0]) + 1);
            a === this.sketcher.shapes.length && (a = 0);
            this.empty();
            this.select([], [this.sketcher.shapes[a]])
        }
    }
})(ChemDoodle.math, ChemDoodle.monitor, ChemDoodle.structures, ChemDoodle.uis.tools);
(function(g, a, p, f, m, h) {
    let d = new g.Splitter;
    f.CopyPasteManager = function(a) {
        this.sketcher = a;
        this.data = h
    };
    g = f.CopyPasteManager.prototype;
    g.interpreter = new a.JSONInterpreter;
    g.copy = function(a) {
        if (this.sketcher.lasso.isActive()) {
            let f = d.split({
                atoms: this.sketcher.lasso.atoms,
                bonds: this.sketcher.lasso.getBonds()
            });
            this.data = this.interpreter.contentTo(f, this.sketcher.lasso.shapes);
            a && this.sketcher.stateManager.STATE_ERASE.handleDelete();
            this.sketcher.toolbarManager.buttonPaste.enable()
        }
    };
    g.paste = function() {
        if (this.data) {
            var a =
                this.interpreter.contentFrom(this.data);
            if (0 !== a.molecules.length || 0 !== a.shapes.length) {
                let f = [];
                for (let d = 0, h = a.molecules.length; d < h; d++) f = f.concat(a.molecules[d].atoms);
                if (this.sketcher.lastMousePos) var d = new p.Point(this.sketcher.lastMousePos.x, this.sketcher.lastMousePos.y);
                else this.sketcher.lasso.isActive() ? (this.sketcher.lasso.setBounds(), d = this.sketcher.lasso.bounds, d = new p.Point((d.minX + d.maxX) / 2 + 50, (d.minY + d.maxY) / 2 + 50)) : d = new p.Point(this.sketcher.width / 2, this.sketcher.height / 2);
                this.sketcher.historyManager.pushUndo(new m.AddContentAction(this.sketcher,
                    a.molecules, a.shapes));
                this.sketcher.lasso.empty();
                this.sketcher.lasso.select(f, a.shapes);
                this.sketcher.lasso.setBounds();
                a = this.sketcher.lasso.bounds;
                d.sub(new p.Point((a.minX + a.maxX) / 2 + 10, (a.minY + a.maxY) / 2 + 10));
                (new m.MoveAction(this.sketcher.lasso.getAllPoints(), d)).forward(this.sketcher);
                this.sketcher.repaint()
            }
        }
    }
})(ChemDoodle.informatics, ChemDoodle.io, ChemDoodle.structures, ChemDoodle.uis, ChemDoodle.uis.actions);
(function(g, a, p, f, m, h, d, l, t, q, r) {
    g.SketcherCanvas = function(a, h, e, g) {
        this.isMobile = g.isMobile === r ? p.supports_touch() : g.isMobile;
        this.useServices = g.useServices === r ? !1 : g.useServices;
        this.oneMolecule = g.oneMolecule === r ? !1 : g.oneMolecule;
        this.requireStartingAtom = g.requireStartingAtom === r ? !0 : g.requireStartingAtom;
        this.includeToolbar = g.includeToolbar === r ? !0 : g.includeToolbar;
        this.floatDrawTools = g.floatDrawTools === r ? !1 : g.floatDrawTools;
        this.resizable = g.resizable === r ? !1 : g.resizable;
        this.includeQuery = g.includeQuery ===
            r ? !1 : g.includeQuery;
        this.originalOptions = g;
        this.id = a;
        this.toolbarManager = new f.gui.ToolbarManager(this);
        if (this.includeToolbar) {
            this.toolbarManager.write();
            let e = this;
            document.getElementById(this.id) ? l("#" + a + "_button_chain_icon").load(function() {
                e.toolbarManager.setup()
            }) : l(q).load(function() {
                e.toolbarManager.setup()
            });
            this.dialogManager = new f.gui.DialogManager(this)
        }
        f.gui.desktop.TextInput && (this.textInput = new f.gui.desktop.TextInput(this, this.id + "_textInput"));
        a && this.create(a, h, e);
        this.cursorManager =
            new f.gui.desktop.CursorManager(this);
        this.stateManager = new f.states.StateManager(this);
        this.historyManager = new f.actions.HistoryManager(this);
        this.copyPasteManager = new f.CopyPasteManager(this);
        this.styles.atoms_circleDiameter_2D = 7;
        this.styles.atoms_circleBorderWidth_2D = 0;
        this.isHelp = !1;
        this.lastPinchScale = 1;
        this.lastGestureRotate = 0;
        this.inGesture = !1;
        this.oneMolecule ? (a = new m.Molecule, a.atoms.push(new m.Atom), this.loadMolecule(a)) : (this.startAtom = new m.Atom("C", -10, -10), this.startAtom.isLone = !0, this.lasso =
            new d.Lasso(this));
        if (this.resizable) {
            let a = l("#" + this.id),
                e = this;
            a.resizable({
                resize: function(b, c) {
                    e.resize(a.innerWidth(), a.innerHeight())
                }
            })
        }
    };
    g = g.SketcherCanvas.prototype = new g._Canvas;
    g.drawSketcherDecorations = function(d, f) {
        d.save();
        d.translate(this.width / 2, this.height / 2);
        d.rotate(f.rotateAngle);
        d.scale(f.scale, f.scale);
        d.translate(-this.width / 2, -this.height / 2);
        this.hovering && this.hovering.drawDecorations(d, f);
        this.startAtom && -10 != this.startAtom.x && !this.isMobile && this.startAtom.draw(d, f);
        this.tempAtom &&
            (d.strokeStyle = f.colorPreview, d.fillStyle = f.colorPreview, d.lineWidth = 1, d.beginPath(), d.moveTo(this.hovering.x, this.hovering.y), d.lineTo(this.tempAtom.x, this.tempAtom.y), d.setLineDash([2]), d.stroke(), d.setLineDash([]), "C" === this.tempAtom.label ? (d.beginPath(), d.arc(this.tempAtom.x, this.tempAtom.y, 3, 0, 2 * t.PI, !1), d.fill()) : (d.textAlign = "center", d.textBaseline = "middle", d.font = a.getFontString(f.atoms_font_size_2D, f.atoms_font_families_2D, f.atoms_font_bold_2D, f.atoms_font_italic_2D), d.fillText(this.tempAtom.label,
                this.tempAtom.x, this.tempAtom.y)), this.tempAtom.isOverlap && (d.strokeStyle = f.colorError, d.lineWidth = 1.2, d.beginPath(), d.arc(this.tempAtom.x, this.tempAtom.y, 7, 0, 2 * t.PI, !1), d.stroke()));
        if (this.tempRing) {
            d.strokeStyle = f.colorPreview;
            d.fillStyle = f.colorPreview;
            d.lineWidth = 1;
            d.beginPath();
            if (this.hovering instanceof m.Atom) {
                d.moveTo(this.hovering.x, this.hovering.y);
                d.lineTo(this.tempRing[0].x, this.tempRing[0].y);
                for (let a = 1, c = this.tempRing.length; a < c; a++) d.lineTo(this.tempRing[a].x, this.tempRing[a].y);
                d.lineTo(this.hovering.x, this.hovering.y)
            } else if (this.hovering instanceof m.Bond) {
                var e = this.hovering.a2,
                    h = this.hovering.a1;
                this.tempRing[0] === this.hovering.a1 && (e = this.hovering.a1, h = this.hovering.a2);
                d.moveTo(e.x, e.y);
                d.lineTo(this.tempRing[1].x, this.tempRing[1].y);
                for (let a = 2, c = this.tempRing.length; a < c; a++) d.lineTo(this.tempRing[a].x, this.tempRing[a].y);
                d.lineTo(h.x, h.y)
            }
            d.setLineDash([2]);
            d.stroke();
            d.setLineDash([]);
            d.strokeStyle = f.colorError;
            d.lineWidth = 1.2;
            for (let a = 0, c = this.tempRing.length; a <
                c; a++) this.tempRing[a].isOverlap && (d.beginPath(), d.arc(this.tempRing[a].x, this.tempRing[a].y, 7, 0, 2 * t.PI, !1), d.stroke());
            if (-1 === this.stateManager.STATE_NEW_RING.numSides) {
                h = e = 0;
                if (this.hovering instanceof m.Atom) e += this.hovering.x, h += this.hovering.y;
                else if (this.hovering instanceof m.Bond) {
                    var g = this.hovering.a1;
                    this.tempRing[0] === this.hovering.a1 && (g = this.hovering.a2);
                    e += g.x;
                    h += g.y
                }
                g = this.tempRing.length;
                for (var n = 0; n < g; n++) e += this.tempRing[n].x, h += this.tempRing[n].y;
                g++;
                e /= g;
                h /= g;
                d.font = a.getFontString(f.text_font_size,
                    f.text_font_families, f.text_font_bold, f.text_font_italic);
                d.textAlign = "center";
                d.textBaseline = "middle";
                d.fillStyle = "black";
                d.fillText(g, e, h)
            }
        }
        if (this.tempChain && 0 < this.tempChain.length) {
            d.strokeStyle = f.colorPreview;
            d.fillStyle = f.colorPreview;
            d.lineWidth = 1;
            d.beginPath();
            d.moveTo(this.hovering.x, this.hovering.y);
            d.lineTo(this.tempChain[0].x, this.tempChain[0].y);
            for (let a = 1, c = this.tempChain.length; a < c; a++) d.lineTo(this.tempChain[a].x, this.tempChain[a].y);
            d.setLineDash([2]);
            d.stroke();
            d.setLineDash([]);
            d.strokeStyle = f.colorError;
            d.lineWidth = 1.2;
            for (let a = 0, c = this.tempChain.length; a < c; a++) this.tempChain[a].isOverlap && (d.beginPath(), d.arc(this.tempChain[a].x, this.tempChain[a].y, 7, 0, 2 * t.PI, !1), d.stroke());
            d.font = a.getFontString(f.text_font_size, f.text_font_families, f.text_font_bold, f.text_font_italic);
            d.textAlign = "left";
            d.textBaseline = "bottom";
            e = this.tempChain.length;
            d.fillStyle = "black";
            d.fillText(e, this.tempChain[e - 1].x + 10, this.tempChain[e - 1].y - 10)
        }
        if (this.tempTemplate) {
            if (0 < this.tempTemplate.atoms.length) {
                e =
                    f.atoms_color;
                h = f.atoms_useJMOLColors;
                g = f.atoms_usePYMOLColors;
                n = f.bonds_color;
                let a = f.atoms_HBlack_2D;
                f.atoms_color = f.colorPreview;
                f.atoms_useJMOLColors = !1;
                f.atoms_usePYMOLColors = !1;
                f.bonds_color = f.colorPreview;
                f.atoms_HBlack_2D = !1;
                this.tempTemplate.draw(d, f);
                f.atoms_color = e;
                f.atoms_useJMOLColors = h;
                f.atoms_usePYMOLColors = g;
                f.bonds_color = n;
                f.atoms_HBlack_2D = a
            }
            d.strokeStyle = f.colorError;
            d.lineWidth = 1.2;
            for (let a = 0, c = this.molecules.length; a < c; a++) {
                e = this.molecules[a];
                for (let a = 0, b = e.atoms.length; a <
                    b; a++) h = e.atoms[a], h.isOverlap && (d.beginPath(), d.arc(h.x, h.y, 7, 0, 2 * t.PI, !1), d.stroke())
            }
        }
        this.lasso && this.lasso.draw(d, f);
        this.stateManager.getCurrentState().draw && this.stateManager.getCurrentState().draw(d, f);
        d.restore()
    };
    g.checksOnAction = function(a) {
        if (a && this.doChecks) {
            var d = [],
                e = [];
            let a = [];
            for (let b = 0, c = this.shapes.length; b < c; b++) {
                var f = this.shapes[b];
                if (f instanceof h.AtomMapping) f.error = !1, d.push(f);
                else if (f instanceof h.Line && !g) var g = f;
                else f instanceof h.RepeatUnit ? (f.error = !1, e.push(f)) :
                    f instanceof h.VAP && (f.error = !1, a.push(f))
            }
            for (let a = 0, c = d.length; a < c; a++) {
                g = d[a];
                g.label = (a + 1).toString();
                for (let b = a + 1, c = d.length; b < c; b++)
                    if (f = d[b], g.o1 === f.o1 || g.o2 === f.o1 || g.o1 === f.o2 || g.o2 === f.o2) g.error = !0, f.error = !0;
                g.error || g.o1.label === g.o2.label || (g.error = !0);
                g.error || this.getMoleculeByAtom(g.o1) !== this.getMoleculeByAtom(g.o2) || (g.error = !0)
            }
            if (0 !== e.length) {
                d = this.getAllAtoms();
                for (let a = 0, c = d.length; a < c; a++) d[a].inBracket = !1;
                for (let a = 0, c = e.length; a < c; a++) {
                    d = e[a];
                    d.setContents(this);
                    if (0 ===
                        d.contents.length) d.error = !0;
                    else
                        for (let a = 0, b = d.contents.length; a < b; a++)
                            if (d.contents[a].inBracket) {
                                d.error = !0;
                                break
                            } for (let a = 0, b = d.contents.length; a < b; a++) d.contents[a].inBracket = !0
                }
            }
            for (let b = 0, c = a.length; b < c; b++)
                if (e = a[b], e.substituent ? 0 === e.attachments.length && (e.error = !0) : e.error = !0, !e.error) {
                    d = this.getMoleculeByAtom(e.attachments[0]);
                    e.substituent.present = r;
                    for (let a = 0, b = d.atoms.length; a < b; a++) d.atoms[a].present = !0;
                    e.substituent.present && (e.error = !0);
                    if (!e.error)
                        for (let a = 0, b = e.attachments.length; a <
                            b; a++)
                            if (!e.attachments[a].present) {
                                e.error = !0;
                                break
                            } for (let a = 0, b = d.atoms.length; a < b; a++) d.atoms[a].present = r
                }
        }
        this.doChecks = !a
    };
    g.drawChildExtras = function(a, d) {
        this.drawSketcherDecorations(a, d);
        if (!this.hideHelp) {
            let e = new m.Point(this.width - 20, 20),
                f = a.createRadialGradient(e.x, e.y, 10, e.x, e.y, 2);
            f.addColorStop(0, "#00680F");
            f.addColorStop(1, "#01DF01");
            a.fillStyle = f;
            a.beginPath();
            a.arc(e.x, e.y, 10, 0, 2 * t.PI, !1);
            a.fill();
            a.lineWidth = 2;
            this.isHelp && (a.strokeStyle = d.colorHover, a.stroke());
            a.strokeStyle =
                "black";
            a.fillStyle = "white";
            a.textAlign = "center";
            a.textBaseline = "middle";
            a.font = "14px sans-serif";
            a.strokeText("?", e.x, e.y);
            a.fillText("?", e.x, e.y)
        }
        this.paidToHideTrademark || (a.font = "14px sans-serif", d = a.measureText("ChemDoodle").width, a.textAlign = "left", a.textBaseline = "bottom", a.fillStyle = "rgba(60, 60, 60, 0.5)", a.fillText("ChemDoodle", this.width - d - 13, this.height - 4), a.font = "10px sans-serif", a.fillText("\u00ae", this.width - 13, this.height - 12))
    };
    g.scaleEvent = function(a) {
        a.op = new m.Point(a.p.x, a.p.y);
        1 !== this.styles.scale && (a.p.x = this.width / 2 + (a.p.x - this.width / 2) / this.styles.scale, a.p.y = this.height / 2 + (a.p.y - this.height / 2) / this.styles.scale)
    };
    g.checkScale = function() {
        .5 > this.styles.scale ? this.styles.scale = .5 : 10 < this.styles.scale && (this.styles.scale = 10)
    };
    g.click = function(a) {
        this.scaleEvent(a);
        if (this.modal) return this.modal.close(a), !1;
        this.stateManager.getCurrentState().click(a)
    };
    g.rightclick = function(a) {
        if (this.modal) return !1;
        this.scaleEvent(a);
        this.stateManager.getCurrentState().rightclick(a)
    };
    g.dblclick = function(a) {
        if (this.modal) return !1;
        this.scaleEvent(a);
        this.stateManager.getCurrentState().dblclick(a)
    };
    g.mousedown = function(a) {
        if (this.modal) return !1;
        this.scaleEvent(a);
        this.stateManager.getCurrentState().mousedown(a)
    };
    g.rightmousedown = function(a) {
        if (this.modal) return !1;
        this.scaleEvent(a);
        this.stateManager.getCurrentState().rightmousedown(a)
    };
    g.mousemove = function(a) {
        if (this.modal) return !1;
        this.isHelp = !1;
        10 > a.p.distance(new m.Point(this.width - 20, 20)) && (this.isHelp = !0);
        this.scaleEvent(a);
        this.stateManager.getCurrentState().mousemove(a)
    };
    g.mouseout = function(a) {
        if (this.modal) return !1;
        this.scaleEvent(a);
        this.stateManager.getCurrentState().mouseout(a)
    };
    g.mouseover = function(a) {
        if (this.modal) return !1;
        this.scaleEvent(a);
        this.stateManager.getCurrentState().mouseover(a)
    };
    g.mouseup = function(a) {
        if (this.modal) return !1;
        this.scaleEvent(a);
        this.stateManager.getCurrentState().mouseup(a)
    };
    g.rightmouseup = function(a) {
        if (this.modal) return !1;
        this.scaleEvent(a);
        this.stateManager.getCurrentState().rightmouseup(a)
    };
    g.mousewheel = function(a, d) {
        if (this.modal) return !1;
        this.scaleEvent(a);
        this.stateManager.getCurrentState().mousewheel(a, d)
    };
    g.drag = function(a) {
        if (this.modal) return !1;
        this.scaleEvent(a);
        this.stateManager.getCurrentState().drag(a)
    };
    g.keydown = function(a) {
        if (this.modal) return !1;
        this.scaleEvent(a);
        this.stateManager.getCurrentState().keydown(a)
    };
    g.keypress = function(a) {
        if (this.modal) return !1;
        this.scaleEvent(a);
        this.stateManager.getCurrentState().keypress(a)
    };
    g.keyup = function(a) {
        if (this.modal) return !1;
        this.scaleEvent(a);
        this.stateManager.getCurrentState().keyup(a)
    };
    g.touchstart = function(a) {
        if (this.modal) return !1;
        if (a.originalEvent.touches && 1 < a.originalEvent.touches.length) {
            if (this.tempAtom || this.tempRing) this.hovering = this.tempRing = this.tempAtom = r, this.repaint();
            this.lastPoint = r
        } else this.scaleEvent(a), this.stateManager.getCurrentState().mousemove(a), this.stateManager.getCurrentState().mousedown(a)
    };
    g.touchmove = function(a) {
        if (this.modal) return !1;
        this.scaleEvent(a);
        !this.inGesture && 5 < this.lastPoint.distance(a.p) &&
            this.stateManager.getCurrentState().drag(a)
    };
    g.touchend = function(a) {
        if (this.modal) return !1;
        this.scaleEvent(a);
        this.stateManager.getCurrentState().mouseup(a);
        this.hovering && (this.stateManager.getCurrentState().clearHover(), this.repaint())
    };
    g.gesturechange = function(a) {
        if (this.modal) return !1;
        this.inGesture = !0;
        this.stateManager.getCurrentState().newMolAllowed = !1;
        1 !== a.originalEvent.scale - this.lastPinchScale && (this.lasso && this.lasso.isActive() || (this.styles.scale *= a.originalEvent.scale / this.lastPinchScale,
            this.checkScale()), this.lastPinchScale = a.originalEvent.scale);
        if (0 !== this.lastGestureRotate - a.originalEvent.rotation) {
            let h = (this.lastGestureRotate - a.originalEvent.rotation) / 180 * t.PI;
            if (this.parentAction) {
                this.parentAction.dif += h;
                for (let a = 0, f = this.parentAction.ps.length; a < f; a++) {
                    var d = this.parentAction.ps[a],
                        e = this.parentAction.center.distance(d);
                    let b = this.parentAction.center.angle(d) + h;
                    d.x = this.parentAction.center.x + e * t.cos(b);
                    d.y = this.parentAction.center.y - e * t.sin(b)
                }
                for (let a = 0, e = this.molecules.length; a <
                    e; a++) this.molecules[a].check();
                this.lasso && this.lasso.isActive() && this.lasso.setBounds()
            } else d = this.lasso && this.lasso.isActive() ? this.lasso.getAllPoints() : this.getAllPoints(), e = this.lasso && this.lasso.isActive() ? new m.Point((this.lasso.bounds.minX + this.lasso.bounds.maxX) / 2, (this.lasso.bounds.minY + this.lasso.bounds.maxY) / 2) : new m.Point(this.width / 2, this.height / 2), this.parentAction = new f.actions.RotateAction(d, h, e), this.historyManager.pushUndo(this.parentAction);
            this.lastGestureRotate = a.originalEvent.rotation
        }
        this.repaint()
    };
    g.gestureend = function(a) {
        if (this.modal) return !1;
        this.inGesture = !1;
        this.lastPinchScale = 1;
        this.lastGestureRotate = 0;
        this.parentAction = r
    }
})(ChemDoodle, ChemDoodle.extensions, ChemDoodle.featureDetection, ChemDoodle.uis, ChemDoodle.structures, ChemDoodle.structures.d2, ChemDoodle.uis.tools, ChemDoodle.lib.jQuery, Math, window);
(function(g, a, p, f, m, h, d, l, t, q) {
    m._State3D = function() {};
    g = m._State3D.prototype;
    g.setup = function(a) {
        this.editor = a
    };
    g.enter = function() {
        this.innerenter && this.innerenter()
    };
    g.exit = function() {
        this.innerexit && this.innerexit()
    };
    g.click = function(a) {
        this.innerclick && this.innerclick(a)
    };
    g.rightclick = function(a) {
        this.innerrightclick && this.innerrightclick(a)
    };
    g.dblclick = function(a) {
        this.innerdblclick && this.innerdblclick(a)
    };
    g.mousedown = function(a) {
        this.editor.defaultmousedown(a);
        this.editor.isHelp || this.editor.isMobile &&
            10 > a.p.distance(new h.Point(this.editor.width - 20, 20)) ? (this.editor.isHelp = !1, this.editor.lastPoint = q, this.editor.repaint(), location.href = "https://web.chemdoodle.com/demos/3d-editor") : this.innermousedown && this.innermousedown(a)
    };
    g.rightmousedown = function(a) {
        this.innerrightmousedown && this.innerrightmousedown(a);
        this.editor.defaultrightmousedown(a)
    };
    g.mousemove = function(a) {
        this.innermousemove && this.innermousemove(a);
        this.editor.repaint()
    };
    g.mouseout = function(a) {
        this.innermouseout && this.innermouseout(a)
    };
    g.mouseover = function(a) {
        this.innermouseover && this.innermouseover(a)
    };
    g.mouseup = function(a) {
        this.innermouseup && this.innermouseup(a);
        this.editor.defaultmouseup(a)
    };
    g.rightmouseup = function(a) {
        this.innerrightmouseup && this.innerrightmouseup(a)
    };
    g.mousewheel = function(a, d) {
        this.innermousewheel ? this.innermousewheel(a) : this.editor.defaultmousewheel(a, d)
    };
    g.drag = function(a) {
        this.innerdrag ? this.innerdrag(a) : this.editor.defaultdrag(a)
    };
    g.keydown = function(a) {
        p.META && (90 === a.which ? this.editor.historyManager.undo() :
            89 === a.which ? this.editor.historyManager.redo() : 83 === a.which ? this.editor.toolbarManager.buttonOpen.func() : 78 === a.which ? this.editor.toolbarManager.buttonClear.func() : 187 === a.which || 61 === a.which ? this.editor.toolbarManager.buttonScalePlus.func() : (189 === a.which || 109 === a.which) && this.editor.toolbarManager.buttonScaleMinus.func());
        this.innerkeydown && this.innerkeydown(a)
    };
    g.keypress = function(a) {
        this.innerkeypress && this.innerkeypress(a)
    };
    g.keyup = function(a) {
        this.innerkeyup &&
            this.innerkeyup(a)
    }
})(ChemDoodle, ChemDoodle.math, ChemDoodle.monitor, ChemDoodle.uis.actions, ChemDoodle.uis.states, ChemDoodle.structures, ChemDoodle.SYMBOLS, Math, ChemDoodle.lib.mat4);
(function(g, a, p, f, m, h) {
    a.MeasureState3D = function(a) {
        this.setup(a);
        this.selectedAtoms = []
    };
    a = a.MeasureState3D.prototype = new a._State3D;
    a.numToSelect = 2;
    a.reset = function() {
        for (let a = 0, f = this.selectedAtoms.length; a < f; a++) this.selectedAtoms[a].isSelected = !1;
        this.selectedAtoms = [];
        this.editor.repaint()
    };
    a.innerenter = function(a) {
        this.reset()
    };
    a.innerexit = function(a) {
        this.reset()
    };
    a.innermousemove = function(a) {
        this.hoveredAtom && (this.hoveredAtom.isHover = !1, this.hoveredAtom = h);
        (a = this.editor.pick(a.p.x, a.p.y,
            !0, !1)) && a instanceof p.Atom && (this.hoveredAtom = a, a.isHover = !0);
        this.editor.repaint()
    };
    a.innermousedown = function(a) {
        this.editor.isMobile && this.innermousemove(a);
        if (this.hoveredAtom) {
            this.hoveredAtom.isHover = !1;
            if (this.hoveredAtom.isSelected) {
                let a = this.hoveredAtom;
                this.selectedAtoms = m.grep(this.selectedAtoms, function(d) {
                    return d !== a
                })
            } else this.selectedAtoms.push(this.hoveredAtom);
            this.hoveredAtom.isSelected = !this.hoveredAtom.isSelected;
            this.hoveredAtom = h;
            this.editor.repaint()
        }
        if (this.selectedAtoms.length ===
            this.numToSelect) {
            let a;
            switch (this.numToSelect) {
                case 2:
                    a = new f.Distance(this.selectedAtoms[0], this.selectedAtoms[1]);
                    break;
                case 3:
                    a = new f.Angle(this.selectedAtoms[0], this.selectedAtoms[1], this.selectedAtoms[2]);
                    break;
                case 4:
                    a = new f.Torsion(this.selectedAtoms[0], this.selectedAtoms[1], this.selectedAtoms[2], this.selectedAtoms[3])
            }
            this.reset();
            a && this.editor.historyManager.pushUndo(new g.AddShapeAction(this.editor, a))
        }
    }
})(ChemDoodle.uis.actions, ChemDoodle.uis.states, ChemDoodle.structures, ChemDoodle.structures.d3,
    ChemDoodle.lib.jQuery);
(function(g, a) {
    g.ViewState3D = function(a) {
        this.setup(a)
    };
    g.ViewState3D.prototype = new g._State3D
})(ChemDoodle.uis.states);
(function(g, a) {
    g.StateManager3D = function(a) {
        this.STATE_VIEW = new g.ViewState3D(a);
        this.STATE_MEASURE = new g.MeasureState3D(a);
        let f = this.STATE_VIEW;
        f.enter();
        this.setState = function(a) {
            a !== f && (f.exit(), f = a, f.enter())
        };
        this.getCurrentState = function() {
            return f
        }
    }
})(ChemDoodle.uis.states);
(function(g, a, p, f, m, h, d, l, t, q, r, n, v) {
    h.ToolbarManager3D = function(e) {
        this.editor = e;
        this.buttonOpen = new l.Button(e.id + "_button_open", d.OPEN, "Open", function() {
            e.dialogManager.openPopup.show()
        });
        /*
        this.buttonSave = new l.Button(e.id + "_button_save", d.SAVE, "Save", function() {
            e.useServices ? e.dialogManager.saveDialog.clear() : e.dialogManager.saveDialog.getTextArea().val(g.writeMOL(e.molecules[0]));
            e.dialogManager.saveDialog.open()
        });
        */
        this.buttonSearch = new l.Button(e.id + "_button_search", d.SEARCH, "Search", function() {
            e.dialogManager.searchDialog.open()
        });
        this.buttonCalculate = new l.Button(e.id + "_button_calculate", d.CALCULATE, "Calculate", function() {
            let d = e.molecules[0];
            d && a.calculate(d, {
                descriptors: "mf ef mw miw deg_unsat hba hbd rot electron pol_miller cmr tpsa vabc xlogp2 bertz".split(" ")
            }, function(a) {
                function d(a, e, d) {
                    b.push(a);
                    b.push(": ");
                    for (a = a.length + 2; 30 > a; a++) b.push(" ");
                    b.push(e);
                    b.push(" ");
                    b.push(d);
                    b.push("\n")
                }
                let b = [];
                d("Molecular Formula", a.mf, "");
                d("Empirical Formula", a.ef, "");
                d("Molecular Mass", a.mw, "amu");
                d("Monoisotopic Mass",
                    a.miw, "amu");
                d("Degree of Unsaturation", a.deg_unsat, "");
                d("Hydrogen Bond Acceptors", a.hba, "");
                d("Hydrogen Bond Donors", a.hbd, "");
                d("Rotatable Bonds", a.rot, "");
                d("Total Electrons", a.rot, "");
                d("Molecular Polarizability", a.pol_miller, "A^3");
                d("Molar Refractivity", a.cmr, "cm^3/mol");
                d("Polar Surface Area", a.tpsa, "A^2");
                d("vdW Volume", a.vabc, "A^3");
                d("logP", a.xlogp2, "");
                d("Complexity", a.bertz, "");
                e.dialogManager.calculateDialog.getTextArea().val(b.join(""));
                e.dialogManager.calculateDialog.open()
            })
        });
        this.buttonTransform =
            new l.Button(e.id + "_button_transform", d.PERSPECTIVE, "Transform", function() {
                e.stateManager.setState(e.stateManager.STATE_VIEW)
            });
        this.buttonTransform.toggle = !0;
        this.buttonSettings = new l.Button(e.id + "_button_specifications", d.SETTINGS, "Visual Specifications", function() {
            e.dialogManager.stylesDialog.update(e.styles);
            e.dialogManager.stylesDialog.open()
        });
        this.buttonAnimation = new l.Button(e.id + "_button_animation", d.ANIMATION, "Animations", function() {
            e.stateManager.setState(e.stateManager.STATE_MOVE)
        });
        this.buttonClear =
            new l.Button(e.id + "_button_clear", d.CLEAR, "Clear", function() {
                e.historyManager.pushUndo(new m.ClearAction(e))
            });
        this.buttonClean = new l.Button(e.id + "_button_clean", d.OPTIMIZE, "Clean", function() {
            let d = e.molecules[0];
            d && a.optimize(d, {
                dimension: 3
            }, function(a) {
                e.historyManager.pushUndo(new m.SwitchMoleculeAction(e, a))
            })
        });
        this.makeScaleSet(this);
        this.makeHistorySet(this);
        this.makeMeasurementsSet(this)
    };
    p = h.ToolbarManager3D.prototype;
    p.write = function() {
        let a = ['\x3cdiv style\x3d"font-size:10px;"\x3e'],
            d =
            this.editor.id + "_main_group";
        a.push(this.historySet.getSource());
        a.push(this.scaleSet.getSource());
        a.push(this.buttonOpen.getSource());
        /*
        a.push(this.buttonSave.getSource());
        */
        this.editor.useServices && (a.push(this.buttonSearch.getSource()), a.push(this.buttonCalculate.getSource()));
        a.push("\x3cbr\x3e");
        a.push(this.buttonTransform.getSource(d));
        a.push(this.buttonSettings.getSource());
        a.push(this.measurementsSet.getSource(d));
        a.push(this.buttonClear.getSource());
        this.editor.useServices && a.push(this.buttonClean.getSource());
        a.push("\x3c/div\x3e");
        n.getElementById(this.editor.id) ? r("#" + this.editor.id).before(a.join("")) : n.write(a.join(""))
    };
    p.setup = function() {
        this.buttonTransform.setup(!0);
        this.buttonSettings.setup();
        this.measurementsSet.setup();
        this.buttonClear.setup();
        this.editor.useServices && this.buttonClean.setup();
        this.historySet.setup();
        this.scaleSet.setup();
        this.buttonOpen.setup();
        /*
        this.buttonSave.setup();
        */
        this.editor.useServices && (this.buttonSearch.setup(), this.buttonCalculate.setup());
        this.buttonTransform.getElement().click();
        this.buttonUndo.disable();
        this.buttonRedo.disable()
    };
    p.makeScaleSet = function(a) {
        this.scaleSet = new l.ButtonSet(a.editor.id + "_buttons_scale");
        this.scaleSet.toggle = !1;
        this.buttonScalePlus = new l.Button(a.editor.id + "_button_scale_plus", d.ZOOM_IN, "Increase Scale", function() {
            a.editor.mousewheel(null, -10)
        });
        this.scaleSet.buttons.push(this.buttonScalePlus);
        this.buttonScaleMinus = new l.Button(a.editor.id + "_button_scale_minus", d.ZOOM_OUT, "Decrease Scale", function() {
            a.editor.mousewheel(null, 10)
        });
        this.scaleSet.buttons.push(this.buttonScaleMinus)
    };
    p.makeHistorySet = function(a) {
        this.historySet = new l.ButtonSet(a.editor.id + "_buttons_history");
        this.historySet.toggle = !1;
        this.buttonUndo = new l.Button(a.editor.id + "_button_undo", d.UNDO, "Undo", function() {
            a.editor.historyManager.undo()
        });
        this.historySet.buttons.push(this.buttonUndo);
        this.buttonRedo = new l.Button(a.editor.id + "_button_redo", d.REDO, "Redo", function() {
            a.editor.historyManager.redo()
        });
        this.historySet.buttons.push(this.buttonRedo)
    };
    p.makeMeasurementsSet = function(a) {
        this.measurementsSet = new l.ButtonSet(a.editor.id +
            "_buttons_measurements");
        this.buttonDistance = new l.Button(a.editor.id + "_button_distance", d.DISTANCE, "Distance", function() {
            a.editor.stateManager.STATE_MEASURE.numToSelect = 2;
            a.editor.stateManager.STATE_MEASURE.reset();
            a.editor.stateManager.setState(a.editor.stateManager.STATE_MEASURE)
        });
        this.measurementsSet.buttons.push(this.buttonDistance);
        this.buttonAngle = new l.Button(a.editor.id + "_button_angle", d.ANGLE, "Angle", function() {
            a.editor.stateManager.STATE_MEASURE.numToSelect = 3;
            a.editor.stateManager.STATE_MEASURE.reset();
            a.editor.stateManager.setState(a.editor.stateManager.STATE_MEASURE)
        });
        this.measurementsSet.buttons.push(this.buttonAngle);
        this.buttonTorsion = new l.Button(a.editor.id + "_button_torsion", d.TORSION, "Torsion", function() {
            a.editor.stateManager.STATE_MEASURE.numToSelect = 4;
            a.editor.stateManager.STATE_MEASURE.reset();
            a.editor.stateManager.setState(a.editor.stateManager.STATE_MEASURE)
        });
        this.measurementsSet.buttons.push(this.buttonTorsion)
    }
})(ChemDoodle, ChemDoodle.iChemLabs, ChemDoodle.io, ChemDoodle.structures,
    ChemDoodle.uis.actions, ChemDoodle.uis.gui, ChemDoodle.uis.gui.imageDepot, ChemDoodle.uis.gui.desktop, ChemDoodle.uis.tools, ChemDoodle.uis.states, ChemDoodle.lib.jQuery, document);
(function(g, a, p, f, m) {
    a.SpecsDialog = function(a, d) {
        this.editor = a;
        this.id = this.editor.id + d
    };
    g = a.SpecsDialog.prototype = new a.Dialog;
    g.title = "Visual Specifications";
    g.makeProjectionSet = function(f) {
        this.projectionSet = new a.ButtonSet(f.id + "_projection_group");
        this.buttonPerspective = new a.TextButton(f.id + "_button_Perspective", "Perspective", function() {
            f.editor.styles.projectionPerspective_3D = !0;
            f.editor.updateScene();
            f.update(editor.styles)
        });
        this.projectionSet.buttons.push(this.buttonPerspective);
        this.buttonOrthographic =
            new a.TextButton(f.id + "_button_Orthographic", "Orthographic", function() {
                f.editor.styles.projectionPerspective_3D = !1;
                f.editor.updateScene(f);
                f.update(editor.styles)
            });
        this.projectionSet.buttons.push(this.buttonOrthographic)
    };
    g.makeAtomColorSet = function(f) {
        this.atomColorSet = new a.ButtonSet(f.id + "_atom_color_group");
        this.atomColorSet.toggle = !0;
        this.buttonJmolColors = new a.TextButton(f.id + "_button_Jmol_Colors", "Jmol", function() {
            f.editor.styles.atoms_useJMOLColors = !0;
            f.editor.styles.atoms_usePYMOLColors = !1;
            f.editor.updateScene();
            f.update(editor.styles)
        });
        this.atomColorSet.buttons.push(this.buttonJmolColors);
        this.buttonPymolColors = new a.TextButton(f.id + "_button_PyMOL_Colors", "PyMOL", function() {
            f.editor.styles.atoms_usePYMOLColors = !0;
            f.editor.styles.atoms_useJMOLColors = !1;
            f.editor.updateScene();
            f.update(editor.styles)
        });
        this.atomColorSet.buttons.push(this.buttonPymolColors)
    };
    g.makeBondColorSet = function(f) {
        this.bondColorSet = new a.ButtonSet(f.id + "_bond_color_group");
        this.bondColorSet.toggle = !0;
        this.buttonJmolBondColors =
            new a.TextButton(f.id + "_button_Jmol_Bond_Colors", "Jmol", function() {
                f.editor.styles.bonds_useJMOLColors = !0;
                f.editor.styles.bonds_usePYMOLColors = !1;
                f.editor.updateScene();
                f.update(editor.styles)
            });
        this.bondColorSet.buttons.push(this.buttonJmolBondColors);
        this.buttonPymolBondColors = new a.TextButton(f.id + "_button_PyMOL_Bond_Colors", "PyMOL", function() {
            f.editor.styles.bonds_usePYMOLColors = !0;
            f.editor.styles.bonds_useJMOLColors = !1;
            f.editor.updateScene();
            f.update(editor.styles)
        });
        this.bondColorSet.buttons.push(this.buttonPymolBondColors)
    };
    g.makeCompassPositionSet = function(f) {
        this.compassPositionSet = new a.ButtonSet(f.id + "_compass_position_group");
        this.buttonCompassCorner = new a.TextButton(f.id + "_button_compass_corner", "Corner", function() {
            f.editor.styles.compass_type_3D = 0;
            f.editor.styles.compass_size_3D = 50;
            f.editor.setupScene();
            f.editor.updateScene();
            f.update(editor.styles)
        });
        this.compassPositionSet.buttons.push(this.buttonCompassCorner);
        this.buttonCompassOrigin = new a.TextButton(f.id + "_button_compass_origin", "Origin", function() {
            f.editor.styles.compass_type_3D =
                1;
            f.editor.styles.compass_size_3D = 150;
            f.editor.setupScene();
            f.editor.updateScene();
            f.update(editor.styles)
        });
        this.compassPositionSet.buttons.push(this.buttonCompassOrigin)
    };
    g.makeFogModeSet = function(f) {
        this.fogModeSet = new a.ButtonSet(f.id + "_fog_mode_group");
        this.buttonFogMode0 = new a.TextButton(f.id + "_button_fog_mode_0", "No Fogging", function() {
            f.editor.styles.fog_mode_3D = 0;
            f.editor.updateScene();
            f.update(editor.styles)
        });
        this.fogModeSet.buttons.push(this.buttonFogMode0);
        this.buttonFogMode1 = new a.TextButton(f.id +
            "_button_fog_mode_1", "Linear",
            function() {
                f.editor.styles.fog_mode_3D = 1;
                f.editor.updateScene();
                f.update(editor.styles)
            });
        this.fogModeSet.buttons.push(this.buttonFogMode1);
        this.buttonFogMode2 = new a.TextButton(f.id + "_button_fog_mode_2", "Exponential", function() {
            f.editor.styles.fog_mode_3D = 2;
            f.editor.updateScene();
            f.update(editor.styles)
        });
        this.fogModeSet.buttons.push(this.buttonFogMode2);
        this.buttonFogMode3 = new a.TextButton(f.id + "_button_fog_mode_3", "Exponential\x26sup2;", function() {
            f.editor.styles.fog_mode_3D =
                3;
            f.editor.updateScene();
            f.update(editor.styles)
        });
        this.fogModeSet.buttons.push(this.buttonFogMode3)
    };
    g.setup = function(h, d) {
        this.makeProjectionSet(this);
        this.bgcolor = new a.ColorPicker(this.id + "_bgcolor", "Background Color: ", function(a) {
            d.styles.backgroundColor = a;
            d.setupScene();
            d.repaint();
            h.update(d.styles)
        });
        this.makeFogModeSet(this);
        this.fogcolor = new a.ColorPicker(this.id + "_fogcolor", "Fog Color: ", function(a) {
            d.styles.fog_color_3D = a;
            d.setupScene();
            d.repaint();
            h.update(d.styles)
        });
        this.atomsDisplayToggle =
            new a.CheckBox(this.id + "_atoms_display_toggle", "Display atoms", function() {
                d.styles.atoms_display = !d.styles.atoms_display;
                d.updateScene();
                h.update(d.styles)
            }, !0);
        this.atomcolor = new a.ColorPicker(this.id + "_atomcolor", "Atom Color: ", function(a) {
            d.styles.atoms_color = a;
            d.setupScene();
            d.repaint();
            h.update(d.styles)
        });
        this.makeAtomColorSet(this);
        this.atomColorSetToggle = new a.CheckBox(this.id + "_atom_color_group_toggle", "Color Schemes", function() {
            h.buttonJmolColors.getElement().prop("disabled") ? (h.atomColorSet.enable(),
                d.styles.atoms_useJMOLColors = !0) : (h.atomColorSet.disable(), d.styles.atoms_useJMOLColors = !1, d.styles.atoms_usePYMOLColors = !1, h.buttonJmolColors.uncheck(), h.buttonPymolColors.uncheck());
            d.updateScene();
            h.update(d.styles)
        }, !1);
        this.vdwToggle = new a.CheckBox(this.id + "_vdw_toggle", "Use VDW Diameters", function() {
            d.styles.atoms_useVDWDiameters_3D = !d.styles.atoms_useVDWDiameters_3D;
            d.updateScene();
            h.update(d.styles)
        }, !1);
        this.atomsNonBondedAsStarsToggle = new a.CheckBox(this.id + "_non_bonded_as_stars_toggle",
            "Non-bonded as stars",
            function() {
                d.styles.atoms_nonBondedAsStars_3D = !d.styles.atoms_nonBondedAsStars_3D;
                d.updateScene();
                h.update(d.styles)
            }, !1);
        this.displayLabelsToggle = new a.CheckBox(this.id + "_display_labels_toggle", "Atom labels", function() {
            d.styles.atoms_displayLabels_3D = !d.styles.atoms_displayLabels_3D;
            d.updateScene();
            h.update(d.styles)
        }, !1);
        this.bondsDisplayToggle = new a.CheckBox(this.id + "_bonds_display_toggle", "Display bonds", function() {
            d.styles.bonds_display = !d.styles.bonds_display;
            d.updateScene();
            h.update(d.styles)
        }, !0);
        this.bondcolor = new a.ColorPicker(this.id + "_bondcolor", "Bond Color: ", function(a) {
            d.styles.bonds_color = a;
            d.setupScene();
            d.repaint();
            h.update(d.styles)
        });
        this.makeBondColorSet(this);
        this.bondColorSetToggle = new a.CheckBox(this.id + "_bond_color_group_toggle", "Color Schemes", function() {
            h.buttonJmolBondColors.getElement().prop("disabled") ? (h.bondColorSet.enable(), d.styles.bonds_useJMOLColors = !0) : (h.bondColorSet.disable(), d.styles.bonds_useJMOLColors = !1, d.styles.bonds_usePYMOLColors = !1, h.buttonJmolBondColors.uncheck(), h.buttonPymolBondColors.uncheck());
            d.updateScene();
            h.update(d.styles)
        }, !1);
        this.bondOrderToggle = new a.CheckBox(this.id + "_bond_order_toggle", "Show order", function() {
            d.styles.bonds_showBondOrders_3D = !d.styles.bonds_showBondOrders_3D;
            d.updateScene();
            h.update(d.styles)
        }, !1);
        this.bondsRenderAsLinesToggle = new a.CheckBox(this.id + "_bonds_render_as_lines_toggle", "Render as lines", function() {
            d.styles.bonds_renderAsLines_3D = !d.styles.bonds_renderAsLines_3D;
            d.updateScene();
            h.update(d.styles)
        }, !1);
        this.ribbonsToggle = new a.CheckBox(this.id + "_ribbons_toggle", "Ribbons", function() {
            d.styles.proteins_displayRibbon = !d.styles.proteins_displayRibbon;
            d.updateScene();
            h.update(d.styles)
        }, !1);
        this.backboneToggle = new a.CheckBox(this.id + "_backbone_toggle", "Backbone", function() {
            d.styles.proteins_displayBackbone = !d.styles.proteins_displayBackbone;
            d.updateScene();
            h.update(d.styles)
        }, !1);
        this.pipeplankToggle = new a.CheckBox(this.id + "_pipeplank_toggle", "Pipe and Plank", function() {
            d.styles.proteins_displayPipePlank = !d.styles.proteins_displayPipePlank;
            d.updateScene();
            h.update(d.styles)
        }, !1);
        this.cartoonizeToggle = new a.CheckBox(this.id + "_cartoonize_toggle", "Cartoonize", function() {
            d.styles.proteins_ribbonCartoonize = !d.styles.proteins_ribbonCartoonize;
            d.updateScene();
            h.update(d.styles)
        }, !1);
        this.colorByChainToggle = new a.CheckBox(this.id + "_color_by_chain_toggle", "Color by Chain", function() {
            d.styles.macro_colorByChain = !d.styles.macro_colorByChain;
            d.updateScene();
            h.update(d.styles)
        }, !1);
        this.proteinColorToggle = new a.CheckBox(this.id +
            "_protein_color_toggle", "Color by Segment",
            function() {
                h.proteinColorToggle.checked ? (d.styles.proteins_residueColor = "none", h.proteinColorToggle.uncheck(), p("#proteinColors").prop("disabled", !0)) : (h.proteinColorToggle.check(), p("#proteinColors").removeAttr("disabled"), d.styles.proteins_residueColor = p("#proteinColors").val());
                d.updateScene();
                h.update(d.styles)
            }, !1);
        this.nucleicAcidColorToggle = new a.CheckBox(this.id + "_nucleic_acid_color_toggle", "Color by Segment", function() {
            h.nucleicAcidColorToggle.checked ?
                (d.styles.nucleics_residueColor = "none", h.nucleicAcidColorToggle.uncheck(), p("#nucleicColors").prop("disabled", !0)) : (h.nucleicAcidColorToggle.check(), p("#nucleicColors").removeAttr("disabled"), d.styles.nucleics_residueColor = p("#nucleicColors").val());
            d.updateScene();
            h.update(d.styles)
        }, !1);
        this.shapecolor = new a.ColorPicker(this.id + "_shapecolor", "Shape Color: ", function(a) {
            d.styles.shapes_color = a;
            d.setupScene();
            d.repaint();
            h.update(d.styles)
        });
        this.displayCompassToggle = new a.CheckBox(this.id + "_display_compass_toggle",
            "Display Compass",
            function() {
                h.displayCompassToggle.checked ? (d.styles.compass_display = !1, d.setupScene(), d.updateScene(), h.compassPositionSet.disable(), h.buttonCompassCorner.uncheck(), h.displayCompassToggle.uncheck()) : (d.styles.compass_display = !0, d.styles.compass_type_3D = 0, d.styles.compass_size_3D = 50, h.compassPositionSet.enable(), h.displayCompassToggle.check(), h.buttonCompassCorner.check(), d.setupScene(), d.updateScene());
                h.update(d.styles)
            }, !1);
        this.makeCompassPositionSet(this);
        let g = [];
        g.push('\x3cdiv style\x3d"font-size:12px;text-align:left;overflow-y:scroll;height:300px;" id\x3d"');
        g.push(this.id);
        g.push('" title\x3d"');
        g.push(this.title);
        g.push('"\x3e');
        this.message && (g.push("\x3cp\x3e"), g.push(this.message), g.push("\x3c/p\x3e"));
        g.push("\x3cp\x3e\x3cstrong\x3eRepresentation\x3c/strong\x3e");
        g.push('\x3cp\x3e\x3cselect id\x3d"reps"\x3e\x3coption value\x3d"Ball and Stick"\x3eBall and Stick\x3c/option\x3e\x3coption value\x3d"van der Waals Spheres"\x3evdW Spheres\x3c/option\x3e\x3coption value\x3d"Stick"\x3eStick\x3c/option\x3e\x3coption value\x3d"Wireframe"\x3eWireframe\x3c/option\x3e\x3coption value\x3d"Line"\x3eLine\x3c/option\x3e\x3c/select\x3e\x3c/p\x3e');
        g.push("\x3chr\x3e\x3cstrong\x3eCanvas\x3c/strong\x3e");
        g.push(this.bgcolor.getSource());
        g.push("\x3cp\x3eProjection: ");
        g.push(this.projectionSet.getSource(this.id + "_projection_group"));
        g.push("\x3c/p\x3e\x3cp\x3eFog Mode: ");
        g.push(this.fogModeSet.getSource(this.id + "_fog_mode_group"));
        g.push(this.fogcolor.getSource());
        g.push('\x3c/p\x3e\x3cp\x3eFog start: \x3cinput type\x3d"number" id\x3d"fogstart" min\x3d"0" max\x3d"100" value\x3d"0"\x3e %\x3c/p\x3e');
        g.push('\x3c/p\x3e\x3cp\x3eFog end: \x3cinput type\x3d"number" id\x3d"fogend" min\x3d"0" max\x3d"100" value\x3d"100"\x3e %\x3c/p\x3e');
        g.push('\x3c/p\x3e\x3cp\x3eFog density: \x3cinput type\x3d"number" id\x3d"fogdensity" min\x3d"0" max\x3d"100" value\x3d"100"\x3e %\x3c/p\x3e');
        g.push("\x3chr\x3e\x3cstrong\x3eAtoms\x3c/strong\x3e\x3cp\x3e");
        g.push(this.atomsDisplayToggle.getSource());
        g.push("\x3c/p\x3e\x3cp\x3e");
        g.push(this.atomcolor.getSource());
        g.push('\x3c/p\x3e\x3cp\x3eSphere diameter: \x3cinput type\x3d"number" id\x3d"spherediameter" min\x3d"0" max\x3d"40" value\x3d"0.8" step\x3d"0.01"\x3e Angstroms\x3c/p\x3e');
        g.push(this.vdwToggle.getSource());
        g.push('\x3c/p\x3e\x3cp\x3eVDW Multiplier: \x3cinput type\x3d"number" id\x3d"vdwMultiplier" min\x3d"0" max\x3d"100" value\x3d"100"\x3e %\x3c/p\x3e');
        g.push(this.atomsNonBondedAsStarsToggle.getSource());
        g.push("\x3c/p\x3e\x3cp\x3e");
        g.push(this.displayLabelsToggle.getSource());
        g.push("\x3c/p\x3e\x3cp\x3e");
        g.push(this.atomColorSetToggle.getSource());
        g.push(": ");
        g.push(this.atomColorSet.getSource(this.id + "_atom_color_group"));
        g.push("\x3c/p\x3e\x3chr\x3e\x3cstrong\x3eBonds\x3c/strong\x3e\x3cp\x3e");
        g.push(this.bondsDisplayToggle.getSource());
        g.push("\x3c/p\x3e\x3cp\x3e");
        g.push(this.bondcolor.getSource());
        g.push(this.bondColorSetToggle.getSource());
        g.push(": ");
        g.push(this.bondColorSet.getSource(this.id + "_bond_color_group"));
        g.push("\x3c/p\x3e\x3cp\x3e");
        g.push(this.bondOrderToggle.getSource());
        g.push('\x3c/p\x3e\x3cp\x3eCylinder diameter: \x3cinput type\x3d"number" id\x3d"cylinderdiameter" min\x3d"0" max\x3d"40" value\x3d"0.3" step\x3d"0.01"\x3e Angstroms\x3c/p\x3e');
        g.push("\x3c/p\x3e\x3chr\x3e\x3cstrong\x3eProteins\x3c/strong\x3e");
        g.push("\x3cp\x3e");
        g.push(this.ribbonsToggle.getSource());
        g.push("\x3c/p\x3e\x3cp\x3e");
        g.push(this.backboneToggle.getSource());
        g.push("\x3c/p\x3e\x3cp\x3e");
        g.push(this.pipeplankToggle.getSource());
        g.push("\x3c/p\x3e\x3cp\x3e");
        g.push(this.cartoonizeToggle.getSource());
        g.push("\x3c/p\x3e\x3cp\x3e");
        g.push(this.colorByChainToggle.getSource());
        g.push("\x3c/p\x3e\x3cp\x3e");
        g.push(this.proteinColorToggle.getSource());
        g.push('\x3cselect id\x3d"proteinColors" disabled\x3e\x3coption value\x3d"amino"\x3eAmino\x3c/option\x3e\x3coption value\x3d"shapely"\x3eShapely\x3c/option\x3e\x3coption value\x3d"polarity"\x3ePolarity\x3c/option\x3e\x3coption value\x3d"rainbow"\x3eRainbow\x3c/option\x3e\x3coption value\x3d"acidity"\x3eAcidity\x3c/option\x3e\x3c/select\x3e\x3c/p\x3e');
        g.push("\x3chr\x3e\x3cstrong\x3eNucleic Acids\x3c/strong\x3e\x3cp\x3e");
        g.push(this.nucleicAcidColorToggle.getSource());
        g.push(": ");
        g.push('\x3cselect id\x3d"nucleicColors" disabled\x3e\x3coption value\x3d"shapely"\x3eShapely\x3c/option\x3e\x3coption value\x3d"rainbow"\x3eRainbow\x3c/option\x3e\x3c/select\x3e\x3c/p\x3e');
        g.push("\x3chr\x3e\x3cstrong\x3eShapes\x3c/strong\x3e\x3cp\x3e");
        g.push(this.shapecolor.getSource());
        g.push("\x3c/p\x3e\x3chr\x3e\x3cstrong\x3eCompass\x3c/strong\x3e");
        g.push("\x3cp\x3e");
        g.push(this.displayCompassToggle.getSource());
        g.push(": ");
        g.push(this.compassPositionSet.getSource(this.id + "_compass_position_group"));
        g.push("\x3c/p\x3e");
        g.push("\x3c/div\x3e");
        this.afterMessage && (g.push("\x3cp\x3e"), g.push(this.afterMessage), g.push("\x3c/p\x3e"));
        f.writeln(g.join(""));
        this.getElement().dialog({
            autoOpen: !1,
            position: {
                my: "center",
                at: "center",
                of: f
            },
            buttons: h.buttons,
            width: 500,
            height: 300,
            open: function(a, d) {
                p(this).height(300);
                p(this).width(478);
                p(this).dialog("option", "position", "center")
            }
        });
        this.bgcolor.setup();
        this.fogcolor.setup();
        this.atomcolor.setup();
        this.bondcolor.setup();
        this.shapecolor.setup();
        p("#reps").change(function() {
            d.styles.set3DRepresentation(this.options[this.selectedIndex].value);
            d.updateScene();
            h.update(d.styles)
        });
        p("#proteinColors").change(function() {
            switch (this.selectedIndex) {
                case 0:
                    d.styles.proteins_residueColor = "amino";
                    break;
                case 1:
                    d.styles.proteins_residueColor = "shapely";
                    break;
                case 2:
                    d.styles.proteins_residueColor = "polarity";
                    break;
                case 3:
                    d.styles.proteins_residueColor =
                        "rainbow";
                    break;
                case 4:
                    d.styles.proteins_residueColor = "acidity"
            }
            d.updateScene();
            h.update(d.styles)
        });
        p("#nucleicColors").change(function() {
            switch (this.selectedIndex) {
                case 0:
                    d.styles.nucleics_residueColor = "shapely";
                    break;
                case 1:
                    d.styles.nucleics_residueColor = "rainbow"
            }
            d.updateScene();
            h.update(d.styles)
        });
        p("#fogstart").change(function() {
            d.styles.fog_start_3D = parseInt(this.value) / 100;
            d.updateScene()
        });
        p("#fogend").change(function() {
            d.styles.fog_end_3D = parseInt(this.value) / 100;
            d.updateScene()
        });
        p("#fogdensity").change(function() {
            d.styles.fog_density_3D =
                parseInt(this.value) / 100;
            d.updateScene()
        });
        p("#vdwMultiplier").change(function() {
            d.styles.atoms_vdwMultiplier_3D = parseInt(this.value) / 100;
            d.updateScene()
        });
        p("#spherediameter").change(function() {
            d.styles.atoms_sphereDiameter_3D = parseFloat(this.value);
            d.updateScene()
        });
        p("#cylinderdiameter").change(function() {
            d.styles.bonds_cylinderDiameter_3D = parseFloat(this.value);
            d.updateScene()
        });
        this.projectionSet.setup();
        this.fogModeSet.setup();
        this.atomsDisplayToggle.setup();
        this.vdwToggle.setup();
        this.atomsNonBondedAsStarsToggle.setup();
        this.displayLabelsToggle.setup();
        this.atomColorSet.setup();
        this.atomColorSet.disable();
        this.atomColorSetToggle.setup();
        this.bondsDisplayToggle.setup();
        this.bondColorSet.setup();
        this.bondColorSet.disable();
        this.bondColorSetToggle.setup();
        this.bondOrderToggle.setup();
        this.ribbonsToggle.setup();
        this.backboneToggle.setup();
        this.pipeplankToggle.setup();
        this.cartoonizeToggle.setup();
        this.colorByChainToggle.setup();
        this.proteinColorToggle.setup();
        this.nucleicAcidColorToggle.setup();
        this.displayCompassToggle.setup();
        this.compassPositionSet.setup();
        this.compassPositionSet.disable()
    };
    g.update = function(a) {
        this.bgcolor.setColor(a.backgroundColor);
        this.fogcolor.setColor(a.fog_color_3D);
        this.atomcolor.setColor(a.atoms_color);
        this.bondcolor.setColor(a.bonds_color);
        this.shapecolor.setColor(a.shapes_color);
        a.projectionPerspective_3D ? this.buttonPerspective.select() : this.buttonOrthographic.select();
        switch (a.fog_mode_3D) {
            case 1:
                this.buttonFogMode0.uncheck();
                this.buttonFogMode1.check();
                this.buttonFogMode2.uncheck();
                this.buttonFogMode3.uncheck();
                break;
            case 2:
                this.buttonFogMode0.uncheck();
                this.buttonFogMode1.uncheck();
                this.buttonFogMode2.check();
                this.buttonFogMode3.uncheck();
                break;
            case 3:
                this.buttonFogMode0.uncheck();
                this.buttonFogMode1.uncheck();
                this.buttonFogMode2.uncheck();
                this.buttonFogMode3.check();
                break;
            default:
                this.buttonFogMode0.check(), this.buttonFogMode1.uncheck(), this.buttonFogMode2.uncheck(), this.buttonFogMode3.uncheck()
        }
        p("#fogstart").val(100 * a.fog_start_3D);
        p("#fogend").val(100 * a.fog_end_3D);
        p("#fogdensity").val(100 * a.fog_density_3D);
        a.atoms_display ? this.atomsDisplayToggle.check() : this.atomsDisplayToggle.uncheck();
        a.atoms_useVDWDiameters_3D ? (this.vdwToggle.check(), p("#spherediameter").prop("disabled", !0), p("#vdwMultiplier").prop("disabled", !1), p("#vdwMultiplier").val(100 * a.atoms_vdwMultiplier_3D)) : (this.vdwToggle.uncheck(), p("#spherediameter").prop("disabled", !1), p("#spherediameter").val(a.atoms_sphereDiameter_3D), p("#vdwMultiplier").prop("disabled", !0));
        a.atoms_useJMOLColors || a.atoms_usePYMOLColors ? (this.atomColorSetToggle.check(),
            this.atomColorSet.enable(), a.atoms_useJMOLColors ? (this.buttonJmolColors.check(), this.buttonPymolColors.uncheck()) : a.atoms_usePYMOLColors && (this.buttonJmolColors.uncheck(), this.buttonPymolColors.check())) : (this.atomColorSetToggle.uncheck(), this.buttonPymolColors.uncheck(), this.buttonJmolColors.uncheck(), this.atomColorSet.disable());
        a.atoms_nonBondedAsStars_3D ? this.atomsNonBondedAsStarsToggle.check() : this.atomsNonBondedAsStarsToggle.uncheck();
        a.atoms_displayLabels_3D ? this.displayLabelsToggle.check() :
            this.displayLabelsToggle.uncheck();
        a.bonds_display ? this.bondsDisplayToggle.check() : this.bondsDisplayToggle.uncheck();
        a.bonds_useJMOLColors || a.bonds_usePYMOLColors ? (this.bondColorSetToggle.check(), this.bondColorSet.enable(), a.bonds_useJMOLColors ? (this.buttonJmolBondColors.check(), this.buttonPymolBondColors.uncheck()) : a.atoms_usePYMOLColors && (this.buttonJmolBondColors.uncheck(), this.buttonPymolBondColors.check())) : (this.bondColorSetToggle.uncheck(), this.buttonPymolBondColors.uncheck(), this.buttonJmolBondColors.uncheck(),
            this.bondColorSet.disable());
        a.bonds_showBondOrders_3D ? this.bondOrderToggle.check() : this.bondOrderToggle.uncheck();
        p("#cylinderdiameter").val(a.bonds_cylinderDiameter_3D);
        a.proteins_displayRibbon ? this.ribbonsToggle.check() : this.ribbonsToggle.uncheck();
        a.proteins_displayBackbone ? this.backboneToggle.check() : this.backboneToggle.uncheck();
        a.proteins_displayPipePlank ? this.pipeplankToggle.check() : this.pipeplankToggle.uncheck();
        a.proteins_ribbonCartoonize ? this.cartoonizeToggle.check() : this.cartoonizeToggle.uncheck();
        a.macro_colorByChain ? this.colorByChainToggle.check() : this.colorByChainToggle.uncheck();
        switch (a.proteins_residueColor) {
            case "amino":
                this.proteinColorToggle.check();
                p("#proteinColors").val("amino");
                break;
            case "shapely":
                this.proteinColorToggle.check();
                p("#proteinColors").val("shapely");
                break;
            case "polarity":
                this.proteinColorToggle.check();
                p("#proteinColors").val("polarity");
                break;
            case "rainbow":
                this.proteinColorToggle.check();
                p("#proteinColors").val("rainbow");
                break;
            case "acidity":
                this.proteinColorToggle.check();
                p("#proteinColors").val("acidity");
                break;
            default:
                this.proteinColorToggle.uncheck(), p("#proteinColors").prop("disabled", !0)
        }
        switch (a.nucleics_residueColor) {
            case "shapely":
                this.nucleicAcidColorToggle.check();
                p("#nucleicColors").val("shapely");
                break;
            case "rainbow":
                this.nucleicAcidColorToggle.check();
                p("#nucleicColors").val("rainbow");
                break;
            default:
                this.nucleicAcidColorToggle.uncheck(), p("#nucleicColors").prop("disabled", !0)
        }
        1 == a.compass_display ? (this.compassPositionSet.enable(), 0 == a.compass_type_3D ?
            (this.buttonCompassCorner.check(), this.buttonCompassOrigin.uncheck()) : (this.buttonCompassOrigin.check(), this.buttonCompassCorner.uncheck())) : (this.compassPositionSet.disable(), this.buttonCompassCorner.uncheck(), this.buttonCompassOrigin.uncheck())
    }
})(ChemDoodle, ChemDoodle.uis.gui.desktop, ChemDoodle.lib.jQuery, document);
(function(g, a, p, f, m, h, d, l, t, q, r) {
    g.EditorCanvas3D = function(g, h, e, l) {
        this.isMobile = l.isMobile === r ? a.supports_touch() : l.isMobile;
        this.useServices = l.useServices === r ? !1 : l.useServices;
        this.includeToolbar = l.includeToolbar === r ? !0 : l.includeToolbar;
        this.id = g;
        this.toolbarManager = new f.gui.ToolbarManager3D(this);
        if (this.includeToolbar) {
            this.toolbarManager.write();
            let a = this;
            document.getElementById(this.id) ? d("#" + g + "_button_calculate").load(function() {
                a.toolbarManager.setup()
            }) : d(q).load(function() {
                a.toolbarManager.setup()
            });
            this.dialogManager = new f.gui.DialogManager(this)
        }
        this.stateManager = new f.states.StateManager3D(this);
        this.historyManager = new f.actions.HistoryManager(this);
        g && this.create(g, h, e);
        g = new m.Styles;
        g.atoms_useVDWDiameters_3D = !1;
        g.atoms_sphereDiameter_3D = 2;
        this.helpButton = new m.Atom("C", 0, 0, 0);
        this.helpButton.isHover = !0;
        this.helpButton.styles = g;
        this.styles.backgroundColor = "#000";
        this.styles.shapes_color = "#fff";
        this.isHelp = !1;
        this.setupScene();
        this.repaint()
    };
    g = g.EditorCanvas3D.prototype = new g._Canvas3D;
    g.defaultmousedown = g.mousedown;
    g.defaultmouseup = g.mouseup;
    g.defaultrightmousedown = g.rightmousedown;
    g.defaultdrag = g.drag;
    g.defaultmousewheel = g.mousewheel;
    g.drawChildExtras = function(a) {
        a.disable(a.DEPTH_TEST);
        let d = t.create();
        var e = this.height / 20,
            f = l.tan(this.styles.projectionPerspectiveVerticalFieldOfView_3D / 360 * l.PI);
        let g = e / f;
        var h = l.max(g - e, .1),
            b = this.width / this.height;
        let c = g / this.height * f;
        f *= g;
        let k = -f;
        e = t.ortho(b * k, b * f, k, f, h, g + e, []);
        this.phongShader.useShaderProgram(a);
        this.phongShader.setProjectionMatrix(a,
            e);
        this.phongShader.setFogMode(a, 0);
        this.hideHelp || (h = (this.width - 40) * c, b = (this.height - 40) * c, t.translate(t.identity([]), [h, b, -g], d), a.material.setTempColors(a, this.styles.bonds_materialAmbientColor_3D, r, this.styles.bonds_materialSpecularColor_3D, this.styles.bonds_materialShininess_3D), a.material.setDiffuseColor(a, "#00ff00"), a.modelViewMatrix = t.multiply(d, a.rotationMatrix, []), this.phongShader.enableAttribsArray(a), a.sphereBuffer.bindBuffers(this.gl), this.helpButton.render(a, r, !0), this.isHelp && (a.sphereBuffer.bindBuffers(a),
            a.blendFunc(a.SRC_ALPHA, a.ONE), a.material.setTempColors(a, "#000000", r, "#000000", 0), a.enable(a.BLEND), a.depthMask(!1), a.material.setAlpha(a, .4), this.helpButton.renderHighlight(a, r), a.depthMask(!0), a.disable(a.BLEND), a.blendFuncSeparate(a.SRC_ALPHA, a.ONE_MINUS_SRC_ALPHA, a.ONE, a.ONE_MINUS_SRC_ALPHA)), this.phongShader.disableAttribsArray(a), a.flush(), a.enable(a.BLEND), a.depthMask(!1), this.labelShader.useShaderProgram(a), this.labelShader.setProjectionMatrix(a, e), this.textTextImage.updateFont(this.gl, 14.1,
            ["sans-serif"], !1, !1, !0), h = t.multiply(d, t.identity([]), []), this.labelShader.setModelViewMatrix(a, h), this.labelShader.enableAttribsArray(a), this.renderText("?", [0, 0, 0]), this.labelShader.disableAttribsArray(a), a.disable(a.BLEND), a.depthMask(!0));
        this.paidToHideTrademark || (a.enable(this.gl.BLEND), this.labelShader.useShaderProgram(a), this.labelShader.setProjectionMatrix(a, e), this.labelShader.enableAttribsArray(a), this.textTextImage.updateFont(a, 14.1, ["sans-serif"], !1, !1, !0), e = this.textTextImage.textWidth("ChemDoodle") /
            this.pixelRatio, e = (this.width - e - 30) * c, h = (-this.height + 24) * c, t.translate(t.identity([]), [e, h, -g], d), e = t.multiply(d, a.rotationMatrix, []), this.labelShader.setModelViewMatrix(a, e), this.renderText("ChemDoodle", [0, 0, 0]), e = (this.width - 18) * c, h = (-this.height + 30) * c, t.translate(t.identity([]), [e, h, -g], d), e = t.multiply(d, a.rotationMatrix, []), this.labelShader.setModelViewMatrix(a, e), this.textTextImage.updateFont(a, 10, ["sans-serif"], !1, !1, !0), this.renderText("\u00ae", [0, 0, 0]), this.labelShader.disableAttribsArray(a),
            a.disable(a.BLEND), a.flush());
        a.enable(a.DEPTH_TEST)
    };
    g.checksOnAction = function(a) {
        this.doChecks = !a
    };
    g.click = function(a) {
        this.stateManager.getCurrentState().click(a)
    };
    g.rightclick = function(a) {
        this.stateManager.getCurrentState().rightclick(a)
    };
    g.dblclick = function(a) {
        this.stateManager.getCurrentState().dblclick(a)
    };
    g.mousedown = function(a) {
        this.stateManager.getCurrentState().mousedown(a)
    };
    g.rightmousedown = function(a) {
        this.stateManager.getCurrentState().rightmousedown(a)
    };
    g.mousemove = function(a) {
        this.isHelp = !1;
        10 > a.p.distance(new m.Point(this.width - 20, 20)) && (this.isHelp = !0);
        this.stateManager.getCurrentState().mousemove(a)
    };
    g.mouseout = function(a) {
        this.stateManager.getCurrentState().mouseout(a)
    };
    g.mouseover = function(a) {
        this.stateManager.getCurrentState().mouseover(a)
    };
    g.mouseup = function(a) {
        this.stateManager.getCurrentState().mouseup(a)
    };
    g.rightmouseup = function(a) {
        this.stateManager.getCurrentState().rightmouseup(a)
    };
    g.mousewheel = function(a, d) {
        this.stateManager.getCurrentState().mousewheel(a, d)
    };
    g.drag =
        function(a) {
            this.stateManager.getCurrentState().drag(a)
        };
    g.keydown = function(a) {
        this.stateManager.getCurrentState().keydown(a)
    };
    g.keypress = function(a) {
        this.stateManager.getCurrentState().keypress(a)
    };
    g.keyup = function(a) {
        this.stateManager.getCurrentState().keyup(a)
    }
})(ChemDoodle, ChemDoodle.featureDetection, ChemDoodle.structures.d3, ChemDoodle.uis, ChemDoodle.structures, ChemDoodle.uis.tools, ChemDoodle.lib.jQuery, Math, ChemDoodle.lib.mat4, window);