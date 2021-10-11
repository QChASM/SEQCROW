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

// some web fetching stuff is commented out because I thought
// there was some bad interaction between the ChimeraX browser
// and this
// It might have just been my bad HTML/javascript...
// I also made the code more readable using https://beautifier.io/
//  - Tony Schaefer, August 2021

'use strict';
let ChemDoodle = function() {
    let f = {
        iChemLabs: {},
        informatics: {},
        io: {},
        lib: {},
        notations: {},
        structures: {}
    };
    f.structures.d2 = {};
    f.structures.d3 = {};
    f.getVersion = function() {
        return "9.2.0"
    };
    return f
}();
(function(f, q, l) {
    (function(f, e) {
        "object" === typeof module && "object" === typeof module.exports ? module.exports = f.document ? e(f, !0) : function(k) {
            if (!k.document) throw Error("jQuery requires a window with a document");
            return e(k)
        } : e(f)
    })("undefined" !== typeof f ? f : this, function(f, e) {
        function k(c) {
            var a = !!c && "length" in c && c.length,
                b = r.type(c);
            return "function" === b || r.isWindow(c) ? !1 : "array" === b || 0 === a || "number" === typeof a && 0 < a && a - 1 in c
        }

        function b(c, a, b) {
            if (r.isFunction(a)) return r.grep(c, function(c, d) {
                return !!a.call(c,
                    d, c) !== b
            });
            if (a.nodeType) return r.grep(c, function(c) {
                return c === a !== b
            });
            if ("string" === typeof a) {
                if (ob.test(a)) return r.filter(a, c, b);
                a = r.filter(a, c)
            }
            return r.grep(c, function(c) {
                return -1 < Ca.call(a, c) !== b
            })
        }

        function d(c, a) {
            for (;
                (c = c[a]) && 1 !== c.nodeType;);
            return c
        }

        function h(c) {
            var a = {};
            r.each(c.match(ka) || [], function(c, b) {
                a[b] = !0
            });
            return a
        }

        function a() {
            I.removeEventListener("DOMContentLoaded", a);
            f.removeEventListener("load", a);
            r.ready()
        }

        function g() {
            this.expando = r.expando + g.uid++
        }

        function n(c, a, b) {
            if (b ===
                l && 1 === c.nodeType)
                if (b = "data-" + a.replace(Ta, "-$\x26").toLowerCase(), b = c.getAttribute(b), "string" === typeof b) {
                    try {
                        b = "true" === b ? !0 : "false" === b ? !1 : "null" === b ? null : +b + "" === b ? +b : pb.test(b) ? r.parseJSON(b) : b
                    } catch (ec) {}
                    Y.set(c, a, b)
                } else b = l;
            return b
        }

        function v(c, a, b, d) {
            var g = 1,
                p = 20,
                h = d ? function() {
                    return d.cur()
                } : function() {
                    return r.css(c, a, "")
                },
                G = h(),
                e = b && b[3] || (r.cssNumber[a] ? "" : "px"),
                m = (r.cssNumber[a] || "px" !== e && +G) && pa.exec(r.css(c, a));
            if (m && m[3] !== e) {
                e = e || m[3];
                b = b || [];
                m = +G || 1;
                do g = g || ".5", m /= g, r.style(c,
                    a, m + e); while (g !== (g = h() / G) && 1 !== g && --p)
            }
            if (b) {
                m = +m || +G || 0;
                var n = b[1] ? m + (b[1] + 1) * b[2] : +b[2];
                d && (d.unit = e, d.start = m, d.end = n)
            }
            return n
        }

        function m(c, a) {
            var b = "undefined" !== typeof c.getElementsByTagName ? c.getElementsByTagName(a || "*") : "undefined" !== typeof c.querySelectorAll ? c.querySelectorAll(a || "*") : [];
            return a === l || a && r.nodeName(c, a) ? r.merge([c], b) : b
        }

        function x(c, a) {
            for (var b = 0, d = c.length; b < d; b++) M.set(c[b], "globalEval", !a || M.get(a[b], "globalEval"))
        }

        function u(c, a, b, d, g) {
            for (var p, h, G, e = a.createDocumentFragment(),
                    n = [], v = 0, f = c.length; v < f; v++)
                if ((p = c[v]) || 0 === p)
                    if ("object" === r.type(p)) r.merge(n, p.nodeType ? [p] : p);
                    else if (rb.test(p)) {
                h = h || e.appendChild(a.createElement("div"));
                G = (Ua.exec(p) || ["", ""])[1].toLowerCase();
                G = ba[G] || ba._default;
                h.innerHTML = G[1] + r.htmlPrefilter(p) + G[2];
                for (G = G[0]; G--;) h = h.lastChild;
                r.merge(n, h.childNodes);
                h = e.firstChild;
                h.textContent = ""
            } else n.push(a.createTextNode(p));
            e.textContent = "";
            for (v = 0; p = n[v++];)
                if (d && -1 < r.inArray(p, d)) g && g.push(p);
                else if (c = r.contains(p.ownerDocument, p), h = m(e.appendChild(p),
                    "script"), c && x(h), b)
                for (G = 0; p = h[G++];) Va.test(p.type || "") && b.push(p);
            return e
        }

        function w() {
            return !0
        }

        function t() {
            return !1
        }

        function y() {
            try {
                return I.activeElement
            } catch (G) {}
        }

        function c(a, b, d, g, p, h) {
            var G;
            if ("object" === typeof b) {
                "string" !== typeof d && (g = g || d, d = l);
                for (G in b) c(a, G, d, g, b[G], h);
                return a
            }
            null == g && null == p ? (p = d, g = d = l) : null == p && ("string" === typeof d ? (p = g, g = l) : (p = g, g = d, d = l));
            if (!1 === p) p = t;
            else if (!p) return a;
            if (1 === h) {
                var e = p;
                p = function(c) {
                    r().off(c);
                    return e.apply(this, arguments)
                };
                p.guid = e.guid ||
                    (e.guid = r.guid++)
            }
            return a.each(function() {
                r.event.add(this, b, p, g, d)
            })
        }

        function p(c, a) {
            return r.nodeName(c, "table") && r.nodeName(11 !== a.nodeType ? a : a.firstChild, "tr") ? c.getElementsByTagName("tbody")[0] || c.appendChild(c.ownerDocument.createElement("tbody")) : c
        }

        function A(c) {
            c.type = (null !== c.getAttribute("type")) + "/" + c.type;
            return c
        }

        function B(c) {
            var a = sb.exec(c.type);
            a ? c.type = a[1] : c.removeAttribute("type");
            return c
        }

        function C(c, a) {
            var b, d;
            if (1 === a.nodeType) {
                if (M.hasData(c)) {
                    var g = M.access(c);
                    var p = M.set(a,
                        g);
                    if (g = g.events)
                        for (d in delete p.handle, p.events = {}, g)
                            for (p = 0, b = g[d].length; p < b; p++) r.event.add(a, d, g[d][p])
                }
                Y.hasData(c) && (c = Y.access(c), c = r.extend({}, c), Y.set(a, c))
            }
        }

        function q(c, a, b, d) {
            a = Wa.apply([], a);
            var g, p = 0,
                h = c.length,
                e = h - 1,
                G = a[0],
                n = r.isFunction(G);
            if (n || 1 < h && "string" === typeof G && !T.checkClone && tb.test(G)) return c.each(function(g) {
                var p = c.eq(g);
                n && (a[0] = G.call(this, g, p.html()));
                q(p, a, b, d)
            });
            if (h) {
                var v = u(a, c[0].ownerDocument, !1, c, d);
                var f = v.firstChild;
                1 === v.childNodes.length && (v = f);
                if (f ||
                    d) {
                    f = r.map(m(v, "script"), A);
                    for (g = f.length; p < h; p++) {
                        var k = v;
                        p !== e && (k = r.clone(k, !0, !0), g && r.merge(f, m(k, "script")));
                        b.call(c[p], k, p)
                    }
                    if (g)
                        for (v = f[f.length - 1].ownerDocument, r.map(f, B), p = 0; p < g; p++) k = f[p], Va.test(k.type || "") && !M.access(k, "globalEval") && r.contains(v, k) && (k.src ? r._evalUrl && r._evalUrl(k.src) : r.globalEval(k.textContent.replace(vb, "")))
                }
            }
            return c
        }

        function F(c, a, b) {
            for (var d = a ? r.filter(a, c) : c, g = 0; null != (a = d[g]); g++) b || 1 !== a.nodeType || r.cleanData(m(a)), a.parentNode && (b && r.contains(a.ownerDocument,
                a) && x(m(a, "script")), a.parentNode.removeChild(a));
            return c
        }

        function L(c, a) {
            c = r(a.createElement(c)).appendTo(a.body);
            a = r.css(c[0], "display");
            c.detach();
            return a
        }

        function H(c) {
            var a = I,
                b = Xa[c];
            b || (b = L(c, a), "none" !== b && b || (Da = (Da || r("\x3ciframe frameborder\x3d'0' width\x3d'0' height\x3d'0'/\x3e")).appendTo(a.documentElement), a = Da[0].contentDocument, a.write(), a.close(), b = L(c, a), Da.detach()), Xa[c] = b);
            return b
        }

        function K(c, a, b) {
            var d = c.style;
            var g = (b = b || Ea(c)) ? b.getPropertyValue(a) || b[a] : l;
            "" !== g && g !== l ||
                r.contains(c.ownerDocument, c) || (g = r.style(c, a));
            if (b && !T.pixelMarginRight() && Ja.test(g) && Ya.test(a)) {
                c = d.width;
                a = d.minWidth;
                var p = d.maxWidth;
                d.minWidth = d.maxWidth = d.width = g;
                g = b.width;
                d.width = c;
                d.minWidth = a;
                d.maxWidth = p
            }
            return g !== l ? g + "" : g
        }

        function N(c, a) {
            return {
                get: function() {
                    if (c()) delete this.get;
                    else return (this.get = a).apply(this, arguments)
                }
            }
        }

        function P(c) {
            if (c in Za) return c;
            for (var a = c[0].toUpperCase() + c.slice(1), b = $a.length; b--;)
                if (c = $a[b] + a, c in Za) return c
        }

        function Z(c, a, b) {
            return (c = pa.exec(a)) ?
                Math.max(0, c[2] - (b || 0)) + (c[3] || "px") : a
        }

        function E(c, a, b, d, g) {
            a = b === (d ? "border" : "content") ? 4 : "width" === a ? 1 : 0;
            for (var p = 0; 4 > a; a += 2) "margin" === b && (p += r.css(c, b + la[a], !0, g)), d ? ("content" === b && (p -= r.css(c, "padding" + la[a], !0, g)), "margin" !== b && (p -= r.css(c, "border" + la[a] + "Width", !0, g))) : (p += r.css(c, "padding" + la[a], !0, g), "padding" !== b && (p += r.css(c, "border" + la[a] + "Width", !0, g)));
            return p
        }

        function fa(c, a, b) {
            var d = !0,
                g = "width" === a ? c.offsetWidth : c.offsetHeight,
                p = Ea(c),
                h = "border-box" === r.css(c, "boxSizing", !1, p);
            if (0 >= g || null == g) {
                g = K(c, a, p);
                if (0 > g || null == g) g = c.style[a];
                if (Ja.test(g)) return g;
                d = h && (T.boxSizingReliable() || g === c.style[a]);
                g = parseFloat(g) || 0
            }
            return g + E(c, a, b || (h ? "border" : "content"), d, p) + "px"
        }

        function J(c, a) {
            for (var b, d, g, p = [], h = 0, e = c.length; h < e; h++) d = c[h], d.style && (p[h] = M.get(d, "olddisplay"), b = d.style.display, a ? (p[h] || "none" !== b || (d.style.display = ""), "" === d.style.display && ma(d) && (p[h] = M.access(d, "olddisplay", H(d.nodeName)))) : (g = ma(d), "none" === b && g || M.set(d, "olddisplay", g ? b : r.css(d, "display"))));
            for (h = 0; h < e; h++) d = c[h], !d.style || a && "none" !== d.style.display && "" !== d.style.display || (d.style.display = a ? p[h] || "" : "none");
            return c
        }

        function O(c, a, b, d, g) {
            return new O.prototype.init(c, a, b, d, g)
        }

        function Q() {
            f.setTimeout(function() {
                ta = l
            });
            return ta = r.now()
        }

        function V(c, a) {
            var b = 0,
                d = {
                    height: c
                };
            for (a = a ? 1 : 0; 4 > b; b += 2 - a) {
                var g = la[b];
                d["margin" + g] = d["padding" + g] = c
            }
            a && (d.opacity = d.width = c);
            return d
        }

        function X(c, a, b) {
            for (var d, g = (R.tweeners[a] || []).concat(R.tweeners["*"]), p = 0, h = g.length; p < h; p++)
                if (d = g[p].call(b,
                        a, c)) return d
        }

        function ha(c, a) {
            var b, d;
            for (b in c) {
                var g = r.camelCase(b);
                var p = a[g];
                var h = c[b];
                r.isArray(h) && (p = h[1], h = c[b] = h[0]);
                b !== g && (c[g] = h, delete c[b]);
                if ((d = r.cssHooks[g]) && "expand" in d)
                    for (b in h = d.expand(h), delete c[g], h) b in c || (c[b] = h[b], a[b] = p);
                else a[g] = p
            }
        }

        function R(c, a, b) {
            var d, g = 0,
                p = R.prefilters.length,
                h = r.Deferred().always(function() {
                    delete e.elem
                }),
                e = function() {
                    if (d) return !1;
                    var a = ta || Q();
                    a = Math.max(0, m.startTime + m.duration - a);
                    for (var b = 1 - (a / m.duration || 0), g = 0, p = m.tweens.length; g <
                        p; g++) m.tweens[g].run(b);
                    h.notifyWith(c, [m, b, a]);
                    if (1 > b && p) return a;
                    h.resolveWith(c, [m]);
                    return !1
                },
                m = h.promise({
                    elem: c,
                    props: r.extend({}, a),
                    opts: r.extend(!0, {
                        specialEasing: {},
                        easing: r.easing._default
                    }, b),
                    originalProperties: a,
                    originalOptions: b,
                    startTime: ta || Q(),
                    duration: b.duration,
                    tweens: [],
                    createTween: function(a, b) {
                        a = r.Tween(c, m.opts, a, b, m.opts.specialEasing[a] || m.opts.easing);
                        m.tweens.push(a);
                        return a
                    },
                    stop: function(a) {
                        var b = 0,
                            g = a ? m.tweens.length : 0;
                        if (d) return this;
                        for (d = !0; b < g; b++) m.tweens[b].run(1);
                        a ? (h.notifyWith(c, [m, 1, 0]), h.resolveWith(c, [m, a])) : h.rejectWith(c, [m, a]);
                        return this
                    }
                });
            b = m.props;
            for (ha(b, m.opts.specialEasing); g < p; g++)
                if (a = R.prefilters[g].call(m, c, b, m.opts)) return r.isFunction(a.stop) && (r._queueHooks(m.elem, m.opts.queue).stop = r.proxy(a.stop, a)), a;
            r.map(b, X, m);
            r.isFunction(m.opts.start) && m.opts.start.call(c, m);
            r.fx.timer(r.extend(e, {
                elem: c,
                anim: m,
                queue: m.opts.queue
            }));
            return m.progress(m.opts.progress).done(m.opts.done, m.opts.complete).fail(m.opts.fail).always(m.opts.always)
        }

        function U(c) {
            return c.getAttribute &&
                c.getAttribute("class") || ""
        }

        function ca(c) {
            return function(a, b) {
                "string" !== typeof a && (b = a, a = "*");
                var d = 0,
                    g = a.toLowerCase().match(ka) || [];
                if (r.isFunction(b))
                    for (; a = g[d++];) "+" === a[0] ? (a = a.slice(1) || "*", (c[a] = c[a] || []).unshift(b)) : (c[a] = c[a] || []).push(b)
            }
        }

        function ia(c, a, b, d) {
            function g(e) {
                var m;
                p[e] = !0;
                r.each(c[e] || [], function(c, e) {
                    c = e(a, b, d);
                    if ("string" === typeof c && !h && !p[c]) return a.dataTypes.unshift(c), g(c), !1;
                    if (h) return !(m = c)
                });
                return m
            }
            var p = {},
                h = c === Ka;
            return g(a.dataTypes[0]) || !p["*"] && g("*")
        }

        function aa(c, a) {
            var b, d, g = r.ajaxSettings.flatOptions || {};
            for (b in a) a[b] !== l && ((g[b] ? c : d || (d = {}))[b] = a[b]);
            d && r.extend(!0, c, d);
            return c
        }

        function da(c, a, b, d) {
            var g;
            if (r.isArray(a)) r.each(a, function(a, g) {
                b || wb.test(c) ? d(c, g) : da(c + "[" + ("object" === typeof g && null != g ? a : "") + "]", g, b, d)
            });
            else if (b || "object" !== r.type(a)) d(c, a);
            else
                for (g in a) da(c + "[" + g + "]", a[g], b, d)
        }

        function na(c) {
            return r.isWindow(c) ? c : 9 === c.nodeType && c.defaultView
        }
        var ea = [],
            I = f.document,
            oa = ea.slice,
            Wa = ea.concat,
            La = ea.push,
            Ca = ea.indexOf,
            Fa = {},
            xb = Fa.toString,
            ua = Fa.hasOwnProperty,
            T = {},
            r = function(c, a) {
                return new r.fn.init(c, a)
            },
            yb = /^[\s\uFEFF\xA0]+|[\s\uFEFF\xA0]+$/g,
            zb = /^-ms-/,
            Ab = /-([\da-z])/gi,
            Bb = function(c, a) {
                return a.toUpperCase()
            };
        r.fn = r.prototype = {
            jquery: "2.2.4",
            constructor: r,
            selector: "",
            length: 0,
            toArray: function() {
                return oa.call(this)
            },
            get: function(c) {
                return null != c ? 0 > c ? this[c + this.length] : this[c] : oa.call(this)
            },
            pushStack: function(c) {
                c = r.merge(this.constructor(), c);
                c.prevObject = this;
                c.context = this.context;
                return c
            },
            each: function(c) {
                return r.each(this,
                    c)
            },
            map: function(c) {
                return this.pushStack(r.map(this, function(a, b) {
                    return c.call(a, b, a)
                }))
            },
            slice: function() {
                return this.pushStack(oa.apply(this, arguments))
            },
            first: function() {
                return this.eq(0)
            },
            last: function() {
                return this.eq(-1)
            },
            eq: function(c) {
                var a = this.length;
                c = +c + (0 > c ? a : 0);
                return this.pushStack(0 <= c && c < a ? [this[c]] : [])
            },
            end: function() {
                return this.prevObject || this.constructor()
            },
            push: La,
            sort: ea.sort,
            splice: ea.splice
        };
        r.extend = r.fn.extend = function() {
            var c, a, b, d = arguments[0] || {},
                g = 1,
                p = arguments.length,
                h = !1;
            "boolean" === typeof d && (h = d, d = arguments[g] || {}, g++);
            "object" === typeof d || r.isFunction(d) || (d = {});
            g === p && (d = this, g--);
            for (; g < p; g++)
                if (null != (c = arguments[g]))
                    for (a in c) {
                        var e = d[a];
                        var m = c[a];
                        d !== m && (h && m && (r.isPlainObject(m) || (b = r.isArray(m))) ? (b ? (b = !1, e = e && r.isArray(e) ? e : []) : e = e && r.isPlainObject(e) ? e : {}, d[a] = r.extend(h, e, m)) : m !== l && (d[a] = m))
                    }
            return d
        };
        r.extend({
            expando: "jQuery" + ("2.2.4" + Math.random()).replace(/\D/g, ""),
            isReady: !0,
            error: function(c) {
                throw Error(c);
            },
            noop: function() {},
            isFunction: function(c) {
                return "function" ===
                    r.type(c)
            },
            isArray: Array.isArray,
            isWindow: function(c) {
                return null != c && c === c.window
            },
            isNumeric: function(c) {
                var a = c && c.toString();
                return !r.isArray(c) && 0 <= a - parseFloat(a) + 1
            },
            isPlainObject: function(c) {
                var a;
                if ("object" !== r.type(c) || c.nodeType || r.isWindow(c) || c.constructor && !ua.call(c, "constructor") && !ua.call(c.constructor.prototype || {}, "isPrototypeOf")) return !1;
                for (a in c);
                return a === l || ua.call(c, a)
            },
            isEmptyObject: function(c) {
                for (var a in c) return !1;
                return !0
            },
            type: function(c) {
                return null == c ? c + "" : "object" ===
                    typeof c || "function" === typeof c ? Fa[xb.call(c)] || "object" : typeof c
            },
            globalEval: function(c) {
                var a = eval;
                if (c = r.trim(c)) 1 === c.indexOf("use strict") ? (a = I.createElement("script"), a.text = c, I.head.appendChild(a).parentNode.removeChild(a)) : a(c)
            },
            camelCase: function(c) {
                return c.replace(zb, "ms-").replace(Ab, Bb)
            },
            nodeName: function(c, a) {
                return c.nodeName && c.nodeName.toLowerCase() === a.toLowerCase()
            },
            each: function(c, a) {
                var b, d = 0;
                if (k(c))
                    for (b = c.length; d < b && !1 !== a.call(c[d], d, c[d]); d++);
                else
                    for (d in c)
                        if (!1 === a.call(c[d],
                                d, c[d])) break;
                return c
            },
            trim: function(c) {
                return null == c ? "" : (c + "").replace(yb, "")
            },
            makeArray: function(c, a) {
                a = a || [];
                null != c && (k(Object(c)) ? r.merge(a, "string" === typeof c ? [c] : c) : La.call(a, c));
                return a
            },
            inArray: function(c, a, b) {
                return null == a ? -1 : Ca.call(a, c, b)
            },
            merge: function(c, a) {
                for (var b = +a.length, d = 0, g = c.length; d < b; d++) c[g++] = a[d];
                c.length = g;
                return c
            },
            grep: function(c, a, b) {
                for (var d = [], g = 0, p = c.length, h = !b; g < p; g++) b = !a(c[g], g), b !== h && d.push(c[g]);
                return d
            },
            map: function(c, a, b) {
                var d, g = 0,
                    p = [];
                if (k(c))
                    for (d =
                        c.length; g < d; g++) {
                        var h = a(c[g], g, b);
                        null != h && p.push(h)
                    } else
                        for (g in c) h = a(c[g], g, b), null != h && p.push(h);
                return Wa.apply([], p)
            },
            guid: 1,
            proxy: function(c, a) {
                if ("string" === typeof a) {
                    var b = c[a];
                    a = c;
                    c = b
                }
                if (!r.isFunction(c)) return l;
                var d = oa.call(arguments, 2);
                b = function() {
                    return c.apply(a || this, d.concat(oa.call(arguments)))
                };
                b.guid = c.guid = c.guid || r.guid++;
                return b
            },
            now: Date.now,
            support: T
        });
        "function" === typeof Symbol && (r.fn[Symbol.iterator] = ea[Symbol.iterator]);
        r.each("Boolean Number String Function Array Date RegExp Object Error Symbol".split(" "),
            function(c, a) {
                Fa["[object " + a + "]"] = a.toLowerCase()
            });
        var sa = function(c) {
            function a(c, a, b, d) {
                var g, p, h, e, m = a && a.ownerDocument,
                    n = a ? a.nodeType : 9;
                b = b || [];
                if ("string" !== typeof c || !c || 1 !== n && 9 !== n && 11 !== n) return b;
                if (!d && ((a ? a.ownerDocument || a : N) !== C && wa(a), a = a || C, D)) {
                    if (11 !== n && (e = oa.exec(c)))
                        if (g = e[1])
                            if (9 === n)
                                if (p = a.getElementById(g)) {
                                    if (p.id === g) return b.push(p), b
                                } else return b;
                    else {
                        if (m && (p = m.getElementById(g)) && K(a, p) && p.id === g) return b.push(p), b
                    } else {
                        if (e[2]) return R.apply(b, a.getElementsByTagName(c)),
                            b;
                        if ((g = e[3]) && W.getElementsByClassName && a.getElementsByClassName) return R.apply(b, a.getElementsByClassName(g)), b
                    }
                    if (!(!W.qsa || fa[c + " "] || F && F.test(c))) {
                        if (1 !== n) {
                            m = a;
                            var f = c
                        } else if ("object" !== a.nodeName.toLowerCase()) {
                            (h = a.getAttribute("id")) ? h = h.replace(ta, "\\$\x26"): a.setAttribute("id", h = E);
                            e = ma(c);
                            g = e.length;
                            for (p = ea.test(h) ? "#" + h : "[id\x3d'" + h + "']"; g--;) e[g] = p + " " + k(e[g]);
                            f = e.join(",");
                            m = la.test(c) && v(a.parentNode) || a
                        }
                        if (f) try {
                            return R.apply(b, m.querySelectorAll(f)), b
                        } catch (jc) {} finally {
                            h ===
                                E && a.removeAttribute("id")
                        }
                    }
                }
                return xa(c.replace(aa, "$1"), a, b, d)
            }

            function b() {
                function c(b, d) {
                    a.push(b + " ") > S.cacheLength && delete c[a.shift()];
                    return c[b + " "] = d
                }
                var a = [];
                return c
            }

            function d(c) {
                c[E] = !0;
                return c
            }

            function g(c) {
                var a = C.createElement("div");
                try {
                    return !!c(a)
                } catch (hc) {
                    return !1
                } finally {
                    a.parentNode && a.parentNode.removeChild(a)
                }
            }

            function p(c, a) {
                c = c.split("|");
                for (var b = c.length; b--;) S.attrHandle[c[b]] = a
            }

            function h(c, a) {
                var b = a && c,
                    d = b && 1 === c.nodeType && 1 === a.nodeType && (~a.sourceIndex || -2147483648) -
                    (~c.sourceIndex || -2147483648);
                if (d) return d;
                if (b)
                    for (; b = b.nextSibling;)
                        if (b === a) return -1;
                return c ? 1 : -1
            }

            function e(c) {
                return function(a) {
                    return "input" === a.nodeName.toLowerCase() && a.type === c
                }
            }

            function m(c) {
                return function(a) {
                    var b = a.nodeName.toLowerCase();
                    return ("input" === b || "button" === b) && a.type === c
                }
            }

            function n(c) {
                return d(function(a) {
                    a = +a;
                    return d(function(b, d) {
                        for (var g, p = c([], b.length, a), h = p.length; h--;) b[g = p[h]] && (b[g] = !(d[g] = b[g]))
                    })
                })
            }

            function v(c) {
                return c && "undefined" !== typeof c.getElementsByTagName &&
                    c
            }

            function f() {}

            function k(c) {
                for (var a = 0, b = c.length, d = ""; a < b; a++) d += c[a].value;
                return d
            }

            function G(c, a, b) {
                var d = a.dir,
                    g = b && "parentNode" === d,
                    p = J++;
                return a.first ? function(a, b, p) {
                    for (; a = a[d];)
                        if (1 === a.nodeType || g) return c(a, b, p)
                } : function(a, b, h) {
                    var e, m = [P, p];
                    if (h)
                        for (; a = a[d];) {
                            if ((1 === a.nodeType || g) && c(a, b, h)) return !0
                        } else
                            for (; a = a[d];)
                                if (1 === a.nodeType || g) {
                                    var n = a[E] || (a[E] = {});
                                    n = n[a.uniqueID] || (n[a.uniqueID] = {});
                                    if ((e = n[d]) && e[0] === P && e[1] === p) return m[2] = e[2];
                                    n[d] = m;
                                    if (m[2] = c(a, b, h)) return !0
                                }
                }
            }

            function A(c) {
                return 1 < c.length ? function(a, b, d) {
                    for (var g = c.length; g--;)
                        if (!c[g](a, b, d)) return !1;
                    return !0
                } : c[0]
            }

            function u(c, a, b, d, g) {
                for (var p, h = [], e = 0, m = c.length, n = null != a; e < m; e++)
                    if (p = c[e])
                        if (!b || b(p, d, g)) h.push(p), n && a.push(e);
                return h
            }

            function x(c, b, g, p, h, e) {
                p && !p[E] && (p = x(p));
                h && !h[E] && (h = x(h, e));
                return d(function(d, e, m, n) {
                    var v, f = [],
                        k = [],
                        G = e.length,
                        A;
                    if (!(A = d)) {
                        A = b || "*";
                        for (var x = m.nodeType ? [m] : m, w = [], l = 0, t = x.length; l < t; l++) a(A, x[l], w);
                        A = w
                    }
                    A = !c || !d && b ? A : u(A, f, c, m, n);
                    x = g ? h || (d ? c : G || p) ? [] : e :
                        A;
                    g && g(A, x, m, n);
                    if (p) {
                        var z = u(x, k);
                        p(z, [], m, n);
                        for (m = z.length; m--;)
                            if (v = z[m]) x[k[m]] = !(A[k[m]] = v)
                    }
                    if (d) {
                        if (h || c) {
                            if (h) {
                                z = [];
                                for (m = x.length; m--;)(v = x[m]) && z.push(A[m] = v);
                                h(null, x = [], z, n)
                            }
                            for (m = x.length; m--;)(v = x[m]) && -1 < (z = h ? ha(d, v) : f[m]) && (d[z] = !(e[z] = v))
                        }
                    } else x = u(x === e ? x.splice(G, x.length) : x), h ? h(null, e, x, n) : R.apply(e, x)
                })
            }

            function w(c) {
                var a, b, d = c.length,
                    g = S.relative[c[0].type];
                var p = g || S.relative[" "];
                for (var h = g ? 1 : 0, e = G(function(c) {
                            return c === a
                        }, p, !0), m = G(function(c) {
                            return -1 < ha(a, c)
                        }, p, !0),
                        n = [function(c, b, d) {
                            c = !g && (d || b !== r) || ((a = b).nodeType ? e(c, b, d) : m(c, b, d));
                            a = null;
                            return c
                        }]; h < d; h++)
                    if (p = S.relative[c[h].type]) n = [G(A(n), p)];
                    else {
                        p = S.filter[c[h].type].apply(null, c[h].matches);
                        if (p[E]) {
                            for (b = ++h; b < d && !S.relative[c[b].type]; b++);
                            return x(1 < h && A(n), 1 < h && k(c.slice(0, h - 1).concat({
                                value: " " === c[h - 2].type ? "*" : ""
                            })).replace(aa, "$1"), p, h < b && w(c.slice(h, b)), b < d && w(c = c.slice(b)), b < d && k(c))
                        }
                        n.push(p)
                    } return A(n)
            }

            function t(c, b) {
                var g = 0 < b.length,
                    p = 0 < c.length,
                    h = function(d, h, e, m, n) {
                        var v, f, k = 0,
                            G =
                            "0",
                            A = d && [],
                            x = [],
                            w = r,
                            l = d || p && S.find.TAG("*", n),
                            t = P += null == w ? 1 : Math.random() || .1,
                            z = l.length;
                        for (n && (r = h === C || h || n); G !== z && null != (v = l[G]); G++) {
                            if (p && v) {
                                var Ia = 0;
                                h || v.ownerDocument === C || (wa(v), e = !D);
                                for (; f = c[Ia++];)
                                    if (f(v, h || C, e)) {
                                        m.push(v);
                                        break
                                    } n && (P = t)
                            }
                            g && ((v = !f && v) && k--, d && A.push(v))
                        }
                        k += G;
                        if (g && G !== k) {
                            for (Ia = 0; f = b[Ia++];) f(A, x, h, e);
                            if (d) {
                                if (0 < k)
                                    for (; G--;) A[G] || x[G] || (x[G] = Q.call(m));
                                x = u(x)
                            }
                            R.apply(m, x);
                            n && !d && 0 < x.length && 1 < k + b.length && a.uniqueSort(m)
                        }
                        n && (P = t, r = w);
                        return A
                    };
                return g ? d(h) : h
            }
            var z,
                r, B, y, C, q, D, F, H, L, K, E = "sizzle" + 1 * new Date,
                N = c.document,
                P = 0,
                J = 0,
                Z = b(),
                O = b(),
                fa = b(),
                ca = function(c, a) {
                    c === a && (y = !0);
                    return 0
                },
                V = {}.hasOwnProperty,
                I = [],
                Q = I.pop,
                X = I.push,
                R = I.push,
                M = I.slice,
                ha = function(c, a) {
                    for (var b = 0, d = c.length; b < d; b++)
                        if (c[b] === a) return b;
                    return -1
                },
                ia = /[\x20\t\r\n\f]+/g,
                aa = /^[\x20\t\r\n\f]+|((?:^|[^\\])(?:\\.)*)[\x20\t\r\n\f]+$/g,
                U = /^[\x20\t\r\n\f]*,[\x20\t\r\n\f]*/,
                T = /^[\x20\t\r\n\f]*([>+~]|[\x20\t\r\n\f])[\x20\t\r\n\f]*/,
                da = /=[\x20\t\r\n\f]*([^\]'"]*?)[\x20\t\r\n\f]*\]/g,
                Y = /:((?:\\.|[\w-]|[^\x00-\xa0])+)(?:\((('((?:\\.|[^\\'])*)'|"((?:\\.|[^\\"])*)")|((?:\\.|[^\\()[\]]|\[[\x20\t\r\n\f]*((?:\\.|[\w-]|[^\x00-\xa0])+)(?:[\x20\t\r\n\f]*([*^$|!~]?=)[\x20\t\r\n\f]*(?:'((?:\\.|[^\\'])*)'|"((?:\\.|[^\\"])*)"|((?:\\.|[\w-]|[^\x00-\xa0])+))|)[\x20\t\r\n\f]*\])*)|.*)\)|)/,
                ea = /^(?:\\.|[\w-]|[^\x00-\xa0])+$/,
                ba = {
                    ID: /^#((?:\\.|[\w-]|[^\x00-\xa0])+)/,
                    CLASS: /^\.((?:\\.|[\w-]|[^\x00-\xa0])+)/,
                    TAG: /^((?:\\.|[\w-]|[^\x00-\xa0])+|[*])/,
                    ATTR: /^\[[\x20\t\r\n\f]*((?:\\.|[\w-]|[^\x00-\xa0])+)(?:[\x20\t\r\n\f]*([*^$|!~]?=)[\x20\t\r\n\f]*(?:'((?:\\.|[^\\'])*)'|"((?:\\.|[^\\"])*)"|((?:\\.|[\w-]|[^\x00-\xa0])+))|)[\x20\t\r\n\f]*\]/,
                    PSEUDO: /^:((?:\\.|[\w-]|[^\x00-\xa0])+)(?:\((('((?:\\.|[^\\'])*)'|"((?:\\.|[^\\"])*)")|((?:\\.|[^\\()[\]]|\[[\x20\t\r\n\f]*((?:\\.|[\w-]|[^\x00-\xa0])+)(?:[\x20\t\r\n\f]*([*^$|!~]?=)[\x20\t\r\n\f]*(?:'((?:\\.|[^\\'])*)'|"((?:\\.|[^\\"])*)"|((?:\\.|[\w-]|[^\x00-\xa0])+))|)[\x20\t\r\n\f]*\])*)|.*)\)|)/,
                    CHILD: /^:(only|first|last|nth|nth-last)-(child|of-type)(?:\([\x20\t\r\n\f]*(even|odd|(([+-]|)(\d*)n|)[\x20\t\r\n\f]*(?:([+-]|)[\x20\t\r\n\f]*(\d+)|))[\x20\t\r\n\f]*\)|)/i,
                    bool: /^(?:checked|selected|async|autofocus|autoplay|controls|defer|disabled|hidden|ismap|loop|multiple|open|readonly|required|scoped)$/i,
                    needsContext: /^[\x20\t\r\n\f]*[>+~]|:(even|odd|eq|gt|lt|nth|first|last)(?:\([\x20\t\r\n\f]*((?:-\d)?\d*)[\x20\t\r\n\f]*\)|)(?=[^-]|$)/i
                },
                ka = /^(?:input|select|textarea|button)$/i,
                na = /^h\d$/i,
                ja =
                /^[^{]+\{\s*\[native \w/,
                oa = /^(?:#([\w-]+)|(\w+)|\.([\w-]+))$/,
                la = /[+~]/,
                ta = /'|\\/g,
                qa = /\\([\da-f]{1,6}[\x20\t\r\n\f]?|([\x20\t\r\n\f])|.)/ig,
                ra = function(c, a, b) {
                    c = "0x" + a - 65536;
                    return c !== c || b ? a : 0 > c ? String.fromCharCode(c + 65536) : String.fromCharCode(c >> 10 | 55296, c & 1023 | 56320)
                },
                sa = function() {
                    wa()
                };
            try {
                R.apply(I = M.call(N.childNodes), N.childNodes), I[N.childNodes.length].nodeType
            } catch (gc) {
                R = {
                    apply: I.length ? function(c, a) {
                        X.apply(c, M.call(a))
                    } : function(c, a) {
                        for (var b = c.length, d = 0; c[b++] = a[d++];);
                        c.length =
                            b - 1
                    }
                }
            }
            var W = a.support = {};
            var va = a.isXML = function(c) {
                return (c = c && (c.ownerDocument || c).documentElement) ? "HTML" !== c.nodeName : !1
            };
            var wa = a.setDocument = function(c) {
                var a;
                c = c ? c.ownerDocument || c : N;
                if (c === C || 9 !== c.nodeType || !c.documentElement) return C;
                C = c;
                q = C.documentElement;
                D = !va(C);
                (a = C.defaultView) && a.top !== a && (a.addEventListener ? a.addEventListener("unload", sa, !1) : a.attachEvent && a.attachEvent("onunload", sa));
                W.attributes = g(function(c) {
                    c.className = "i";
                    return !c.getAttribute("className")
                });
                W.getElementsByTagName =
                    g(function(c) {
                        c.appendChild(C.createComment(""));
                        return !c.getElementsByTagName("*").length
                    });
                W.getElementsByClassName = ja.test(C.getElementsByClassName);
                W.getById = g(function(c) {
                    q.appendChild(c).id = E;
                    return !C.getElementsByName || !C.getElementsByName(E).length
                });
                W.getById ? (S.find.ID = function(c, a) {
                    if ("undefined" !== typeof a.getElementById && D) return (c = a.getElementById(c)) ? [c] : []
                }, S.filter.ID = function(c) {
                    var a = c.replace(qa, ra);
                    return function(c) {
                        return c.getAttribute("id") === a
                    }
                }) : (delete S.find.ID, S.filter.ID =
                    function(c) {
                        var a = c.replace(qa, ra);
                        return function(c) {
                            return (c = "undefined" !== typeof c.getAttributeNode && c.getAttributeNode("id")) && c.value === a
                        }
                    });
                S.find.TAG = W.getElementsByTagName ? function(c, a) {
                    if ("undefined" !== typeof a.getElementsByTagName) return a.getElementsByTagName(c);
                    if (W.qsa) return a.querySelectorAll(c)
                } : function(c, a) {
                    var b = [],
                        d = 0;
                    a = a.getElementsByTagName(c);
                    if ("*" === c) {
                        for (; c = a[d++];) 1 === c.nodeType && b.push(c);
                        return b
                    }
                    return a
                };
                S.find.CLASS = W.getElementsByClassName && function(c, a) {
                    if ("undefined" !==
                        typeof a.getElementsByClassName && D) return a.getElementsByClassName(c)
                };
                H = [];
                F = [];
                if (W.qsa = ja.test(C.querySelectorAll)) g(function(c) {
                    q.appendChild(c).innerHTML = "\x3ca id\x3d'" + E + "'\x3e\x3c/a\x3e\x3cselect id\x3d'" + E + "-\r\\' msallowcapture\x3d''\x3e\x3coption selected\x3d''\x3e\x3c/option\x3e\x3c/select\x3e";
                    c.querySelectorAll("[msallowcapture^\x3d'']").length && F.push("[*^$]\x3d[\\x20\\t\\r\\n\\f]*(?:''|\"\")");
                    c.querySelectorAll("[selected]").length || F.push("\\[[\\x20\\t\\r\\n\\f]*(?:value|checked|selected|async|autofocus|autoplay|controls|defer|disabled|hidden|ismap|loop|multiple|open|readonly|required|scoped)");
                    c.querySelectorAll("[id~\x3d" + E + "-]").length || F.push("~\x3d");
                    c.querySelectorAll(":checked").length || F.push(":checked");
                    c.querySelectorAll("a#" + E + "+*").length || F.push(".#.+[+~]")
                }), g(function(c) {
                    var a = C.createElement("input");
                    a.setAttribute("type", "hidden");
                    c.appendChild(a).setAttribute("name", "D");
                    c.querySelectorAll("[name\x3dd]").length && F.push("name[\\x20\\t\\r\\n\\f]*[*^$|!~]?\x3d");
                    c.querySelectorAll(":enabled").length || F.push(":enabled", ":disabled");
                    c.querySelectorAll("*,:x");
                    F.push(",.*:")
                });
                (W.matchesSelector = ja.test(L = q.matches || q.webkitMatchesSelector || q.mozMatchesSelector || q.oMatchesSelector || q.msMatchesSelector)) && g(function(c) {
                    W.disconnectedMatch = L.call(c, "div");
                    L.call(c, "[s!\x3d'']:x");
                    H.push("!\x3d", ":((?:\\\\.|[\\w-]|[^\\x00-\\xa0])+)(?:\\((('((?:\\\\.|[^\\\\'])*)'|\"((?:\\\\.|[^\\\\\"])*)\")|((?:\\\\.|[^\\\\()[\\]]|\\[[\\x20\\t\\r\\n\\f]*((?:\\\\.|[\\w-]|[^\\x00-\\xa0])+)(?:[\\x20\\t\\r\\n\\f]*([*^$|!~]?\x3d)[\\x20\\t\\r\\n\\f]*(?:'((?:\\\\.|[^\\\\'])*)'|\"((?:\\\\.|[^\\\\\"])*)\"|((?:\\\\.|[\\w-]|[^\\x00-\\xa0])+))|)[\\x20\\t\\r\\n\\f]*\\])*)|.*)\\)|)")
                });
                F = F.length && new RegExp(F.join("|"));
                H = H.length && new RegExp(H.join("|"));
                K = (a = ja.test(q.compareDocumentPosition)) || ja.test(q.contains) ? function(c, a) {
                    var b = 9 === c.nodeType ? c.documentElement : c;
                    a = a && a.parentNode;
                    return c === a || !!(a && 1 === a.nodeType && (b.contains ? b.contains(a) : c.compareDocumentPosition && c.compareDocumentPosition(a) & 16))
                } : function(c, a) {
                    if (a)
                        for (; a = a.parentNode;)
                            if (a === c) return !0;
                    return !1
                };
                ca = a ? function(c, a) {
                    if (c === a) return y = !0, 0;
                    var b = !c.compareDocumentPosition - !a.compareDocumentPosition;
                    if (b) return b;
                    b = (c.ownerDocument || c) === (a.ownerDocument || a) ? c.compareDocumentPosition(a) : 1;
                    return b & 1 || !W.sortDetached && a.compareDocumentPosition(c) === b ? c === C || c.ownerDocument === N && K(N, c) ? -1 : a === C || a.ownerDocument === N && K(N, a) ? 1 : B ? ha(B, c) - ha(B, a) : 0 : b & 4 ? -1 : 1
                } : function(c, a) {
                    if (c === a) return y = !0, 0;
                    var b = 0,
                        d = c.parentNode,
                        g = a.parentNode,
                        p = [c],
                        e = [a];
                    if (!d || !g) return c === C ? -1 : a === C ? 1 : d ? -1 : g ? 1 : B ? ha(B, c) - ha(B, a) : 0;
                    if (d === g) return h(c, a);
                    for (; c = c.parentNode;) p.unshift(c);
                    for (c = a; c = c.parentNode;) e.unshift(c);
                    for (; p[b] === e[b];) b++;
                    return b ? h(p[b], e[b]) : p[b] === N ? -1 : e[b] === N ? 1 : 0
                };
                return C
            };
            a.matches = function(c, b) {
                return a(c, null, null, b)
            };
            a.matchesSelector = function(c, b) {
                (c.ownerDocument || c) !== C && wa(c);
                b = b.replace(da, "\x3d'$1']");
                if (!(!W.matchesSelector || !D || fa[b + " "] || H && H.test(b) || F && F.test(b))) try {
                    var d = L.call(c, b);
                    if (d || W.disconnectedMatch || c.document && 11 !== c.document.nodeType) return d
                } catch (ic) {}
                return 0 < a(b, C, null, [c]).length
            };
            a.contains = function(c, a) {
                (c.ownerDocument || c) !== C && wa(c);
                return K(c, a)
            };
            a.attr =
                function(c, a) {
                    (c.ownerDocument || c) !== C && wa(c);
                    var b = S.attrHandle[a.toLowerCase()];
                    b = b && V.call(S.attrHandle, a.toLowerCase()) ? b(c, a, !D) : l;
                    return b !== l ? b : W.attributes || !D ? c.getAttribute(a) : (b = c.getAttributeNode(a)) && b.specified ? b.value : null
                };
            a.error = function(c) {
                throw Error("Syntax error, unrecognized expression: " + c);
            };
            a.uniqueSort = function(c) {
                var a, b = [],
                    d = 0,
                    g = 0;
                y = !W.detectDuplicates;
                B = !W.sortStable && c.slice(0);
                c.sort(ca);
                if (y) {
                    for (; a = c[g++];) a === c[g] && (d = b.push(g));
                    for (; d--;) c.splice(b[d], 1)
                }
                B = null;
                return c
            };
            var pa = a.getText = function(c) {
                var a = "",
                    b = 0;
                var d = c.nodeType;
                if (!d)
                    for (; d = c[b++];) a += pa(d);
                else if (1 === d || 9 === d || 11 === d) {
                    if ("string" === typeof c.textContent) return c.textContent;
                    for (c = c.firstChild; c; c = c.nextSibling) a += pa(c)
                } else if (3 === d || 4 === d) return c.nodeValue;
                return a
            };
            var S = a.selectors = {
                cacheLength: 50,
                createPseudo: d,
                match: ba,
                attrHandle: {},
                find: {},
                relative: {
                    "\x3e": {
                        dir: "parentNode",
                        first: !0
                    },
                    " ": {
                        dir: "parentNode"
                    },
                    "+": {
                        dir: "previousSibling",
                        first: !0
                    },
                    "~": {
                        dir: "previousSibling"
                    }
                },
                preFilter: {
                    ATTR: function(c) {
                        c[1] =
                            c[1].replace(qa, ra);
                        c[3] = (c[3] || c[4] || c[5] || "").replace(qa, ra);
                        "~\x3d" === c[2] && (c[3] = " " + c[3] + " ");
                        return c.slice(0, 4)
                    },
                    CHILD: function(c) {
                        c[1] = c[1].toLowerCase();
                        "nth" === c[1].slice(0, 3) ? (c[3] || a.error(c[0]), c[4] = +(c[4] ? c[5] + (c[6] || 1) : 2 * ("even" === c[3] || "odd" === c[3])), c[5] = +(c[7] + c[8] || "odd" === c[3])) : c[3] && a.error(c[0]);
                        return c
                    },
                    PSEUDO: function(c) {
                        var a, b = !c[6] && c[2];
                        if (ba.CHILD.test(c[0])) return null;
                        c[3] ? c[2] = c[4] || c[5] || "" : b && Y.test(b) && (a = ma(b, !0)) && (a = b.indexOf(")", b.length - a) - b.length) && (c[0] =
                            c[0].slice(0, a), c[2] = b.slice(0, a));
                        return c.slice(0, 3)
                    }
                },
                filter: {
                    TAG: function(c) {
                        var a = c.replace(qa, ra).toLowerCase();
                        return "*" === c ? function() {
                            return !0
                        } : function(c) {
                            return c.nodeName && c.nodeName.toLowerCase() === a
                        }
                    },
                    CLASS: function(c) {
                        var a = Z[c + " "];
                        return a || (a = new RegExp("(^|[\\x20\\t\\r\\n\\f])" + c + "([\\x20\\t\\r\\n\\f]|$)"), Z(c, function(c) {
                            return a.test("string" === typeof c.className && c.className || "undefined" !== typeof c.getAttribute && c.getAttribute("class") || "")
                        }))
                    },
                    ATTR: function(c, b, d) {
                        return function(g) {
                            g =
                                a.attr(g, c);
                            if (null == g) return "!\x3d" === b;
                            if (!b) return !0;
                            g += "";
                            return "\x3d" === b ? g === d : "!\x3d" === b ? g !== d : "^\x3d" === b ? d && 0 === g.indexOf(d) : "*\x3d" === b ? d && -1 < g.indexOf(d) : "$\x3d" === b ? d && g.slice(-d.length) === d : "~\x3d" === b ? -1 < (" " + g.replace(ia, " ") + " ").indexOf(d) : "|\x3d" === b ? g === d || g.slice(0, d.length + 1) === d + "-" : !1
                        }
                    },
                    CHILD: function(c, a, b, d, g) {
                        var p = "nth" !== c.slice(0, 3),
                            h = "last" !== c.slice(-4),
                            e = "of-type" === a;
                        return 1 === d && 0 === g ? function(c) {
                            return !!c.parentNode
                        } : function(a, b, m) {
                            var n, v;
                            b = p !== h ? "nextSibling" :
                                "previousSibling";
                            var f = a.parentNode,
                                k = e && a.nodeName.toLowerCase();
                            m = !m && !e;
                            var G = !1;
                            if (f) {
                                if (p) {
                                    for (; b;) {
                                        for (n = a; n = n[b];)
                                            if (e ? n.nodeName.toLowerCase() === k : 1 === n.nodeType) return !1;
                                        var A = b = "only" === c && !A && "nextSibling"
                                    }
                                    return !0
                                }
                                A = [h ? f.firstChild : f.lastChild];
                                if (h && m) {
                                    n = f;
                                    var x = n[E] || (n[E] = {});
                                    x = x[n.uniqueID] || (x[n.uniqueID] = {});
                                    G = x[c] || [];
                                    G = (v = G[0] === P && G[1]) && G[2];
                                    for (n = v && f.childNodes[v]; n = ++v && n && n[b] || (G = v = 0) || A.pop();)
                                        if (1 === n.nodeType && ++G && n === a) {
                                            x[c] = [P, v, G];
                                            break
                                        }
                                } else if (m && (n = a, x = n[E] ||
                                        (n[E] = {}), x = x[n.uniqueID] || (x[n.uniqueID] = {}), G = x[c] || [], G = v = G[0] === P && G[1]), !1 === G)
                                    for (;
                                        (n = ++v && n && n[b] || (G = v = 0) || A.pop()) && ((e ? n.nodeName.toLowerCase() !== k : 1 !== n.nodeType) || !++G || (m && (x = n[E] || (n[E] = {}), x = x[n.uniqueID] || (x[n.uniqueID] = {}), x[c] = [P, G]), n !== a)););
                                G -= g;
                                return G === d || 0 === G % d && 0 <= G / d
                            }
                        }
                    },
                    PSEUDO: function(c, b) {
                        var g = S.pseudos[c] || S.setFilters[c.toLowerCase()] || a.error("unsupported pseudo: " + c);
                        if (g[E]) return g(b);
                        if (1 < g.length) {
                            var p = [c, c, "", b];
                            return S.setFilters.hasOwnProperty(c.toLowerCase()) ?
                                d(function(c, a) {
                                    for (var d, p = g(c, b), h = p.length; h--;) d = ha(c, p[h]), c[d] = !(a[d] = p[h])
                                }) : function(c) {
                                    return g(c, 0, p)
                                }
                        }
                        return g
                    }
                },
                pseudos: {
                    not: d(function(c) {
                        var a = [],
                            b = [],
                            g = ua(c.replace(aa, "$1"));
                        return g[E] ? d(function(c, a, b, d) {
                            d = g(c, null, d, []);
                            for (var p = c.length; p--;)
                                if (b = d[p]) c[p] = !(a[p] = b)
                        }) : function(c, d, p) {
                            a[0] = c;
                            g(a, null, p, b);
                            a[0] = null;
                            return !b.pop()
                        }
                    }),
                    has: d(function(c) {
                        return function(b) {
                            return 0 < a(c, b).length
                        }
                    }),
                    contains: d(function(c) {
                        c = c.replace(qa, ra);
                        return function(a) {
                            return -1 < (a.textContent ||
                                a.innerText || pa(a)).indexOf(c)
                        }
                    }),
                    lang: d(function(c) {
                        ea.test(c || "") || a.error("unsupported lang: " + c);
                        c = c.replace(qa, ra).toLowerCase();
                        return function(a) {
                            var b;
                            do
                                if (b = D ? a.lang : a.getAttribute("xml:lang") || a.getAttribute("lang")) return b = b.toLowerCase(), b === c || 0 === b.indexOf(c + "-"); while ((a = a.parentNode) && 1 === a.nodeType);
                            return !1
                        }
                    }),
                    target: function(a) {
                        var b = c.location && c.location.hash;
                        return b && b.slice(1) === a.id
                    },
                    root: function(c) {
                        return c === q
                    },
                    focus: function(c) {
                        return c === C.activeElement && (!C.hasFocus ||
                            C.hasFocus()) && !!(c.type || c.href || ~c.tabIndex)
                    },
                    enabled: function(c) {
                        return !1 === c.disabled
                    },
                    disabled: function(c) {
                        return !0 === c.disabled
                    },
                    checked: function(c) {
                        var a = c.nodeName.toLowerCase();
                        return "input" === a && !!c.checked || "option" === a && !!c.selected
                    },
                    selected: function(c) {
                        c.parentNode && c.parentNode.selectedIndex;
                        return !0 === c.selected
                    },
                    empty: function(c) {
                        for (c = c.firstChild; c; c = c.nextSibling)
                            if (6 > c.nodeType) return !1;
                        return !0
                    },
                    parent: function(c) {
                        return !S.pseudos.empty(c)
                    },
                    header: function(c) {
                        return na.test(c.nodeName)
                    },
                    input: function(c) {
                        return ka.test(c.nodeName)
                    },
                    button: function(c) {
                        var a = c.nodeName.toLowerCase();
                        return "input" === a && "button" === c.type || "button" === a
                    },
                    text: function(c) {
                        var a;
                        return "input" === c.nodeName.toLowerCase() && "text" === c.type && (null == (a = c.getAttribute("type")) || "text" === a.toLowerCase())
                    },
                    first: n(function() {
                        return [0]
                    }),
                    last: n(function(c, a) {
                        return [a - 1]
                    }),
                    eq: n(function(c, a, b) {
                        return [0 > b ? b + a : b]
                    }),
                    even: n(function(c, a) {
                        for (var b = 0; b < a; b += 2) c.push(b);
                        return c
                    }),
                    odd: n(function(c, a) {
                        for (var b = 1; b < a; b +=
                            2) c.push(b);
                        return c
                    }),
                    lt: n(function(c, a, b) {
                        for (a = 0 > b ? b + a : b; 0 <= --a;) c.push(a);
                        return c
                    }),
                    gt: n(function(c, a, b) {
                        for (b = 0 > b ? b + a : b; ++b < a;) c.push(b);
                        return c
                    })
                }
            };
            S.pseudos.nth = S.pseudos.eq;
            for (z in {
                    radio: !0,
                    checkbox: !0,
                    file: !0,
                    password: !0,
                    image: !0
                }) S.pseudos[z] = e(z);
            for (z in {
                    submit: !0,
                    reset: !0
                }) S.pseudos[z] = m(z);
            f.prototype = S.filters = S.pseudos;
            S.setFilters = new f;
            var ma = a.tokenize = function(c, b) {
                var d, g, p, h, e;
                if (h = O[c + " "]) return b ? 0 : h.slice(0);
                h = c;
                var m = [];
                for (e = S.preFilter; h;) {
                    if (!n || (d = U.exec(h))) d && (h =
                        h.slice(d[0].length) || h), m.push(g = []);
                    var n = !1;
                    if (d = T.exec(h)) n = d.shift(), g.push({
                        value: n,
                        type: d[0].replace(aa, " ")
                    }), h = h.slice(n.length);
                    for (p in S.filter) !(d = ba[p].exec(h)) || e[p] && !(d = e[p](d)) || (n = d.shift(), g.push({
                        value: n,
                        type: p,
                        matches: d
                    }), h = h.slice(n.length));
                    if (!n) break
                }
                return b ? h.length : h ? a.error(c) : O(c, m).slice(0)
            };
            var ua = a.compile = function(c, a) {
                var b, d = [],
                    g = [],
                    p = fa[c + " "];
                if (!p) {
                    a || (a = ma(c));
                    for (b = a.length; b--;) p = w(a[b]), p[E] ? d.push(p) : g.push(p);
                    p = fa(c, t(g, d));
                    p.selector = c
                }
                return p
            };
            var xa =
                a.select = function(c, a, b, d) {
                    var g, p, h, e = "function" === typeof c && c,
                        m = !d && ma(c = e.selector || c);
                    b = b || [];
                    if (1 === m.length) {
                        var n = m[0] = m[0].slice(0);
                        if (2 < n.length && "ID" === (p = n[0]).type && W.getById && 9 === a.nodeType && D && S.relative[n[1].type]) {
                            a = (S.find.ID(p.matches[0].replace(qa, ra), a) || [])[0];
                            if (!a) return b;
                            e && (a = a.parentNode);
                            c = c.slice(n.shift().value.length)
                        }
                        for (g = ba.needsContext.test(c) ? 0 : n.length; g--;) {
                            p = n[g];
                            if (S.relative[h = p.type]) break;
                            if (h = S.find[h])
                                if (d = h(p.matches[0].replace(qa, ra), la.test(n[0].type) &&
                                        v(a.parentNode) || a)) {
                                    n.splice(g, 1);
                                    c = d.length && k(n);
                                    if (!c) return R.apply(b, d), b;
                                    break
                                }
                        }
                    }(e || ua(c, m))(d, a, !D, b, !a || la.test(c) && v(a.parentNode) || a);
                    return b
                };
            W.sortStable = E.split("").sort(ca).join("") === E;
            W.detectDuplicates = !!y;
            wa();
            W.sortDetached = g(function(c) {
                return c.compareDocumentPosition(C.createElement("div")) & 1
            });
            g(function(c) {
                c.innerHTML = "\x3ca href\x3d'#'\x3e\x3c/a\x3e";
                return "#" === c.firstChild.getAttribute("href")
            }) || p("type|href|height|width", function(c, a, b) {
                if (!b) return c.getAttribute(a,
                    "type" === a.toLowerCase() ? 1 : 2)
            });
            W.attributes && g(function(c) {
                c.innerHTML = "\x3cinput/\x3e";
                c.firstChild.setAttribute("value", "");
                return "" === c.firstChild.getAttribute("value")
            }) || p("value", function(c, a, b) {
                if (!b && "input" === c.nodeName.toLowerCase()) return c.defaultValue
            });
            g(function(c) {
                return null == c.getAttribute("disabled")
            }) || p("checked|selected|async|autofocus|autoplay|controls|defer|disabled|hidden|ismap|loop|multiple|open|readonly|required|scoped", function(c, a, b) {
                var d;
                if (!b) return !0 === c[a] ? a.toLowerCase() :
                    (d = c.getAttributeNode(a)) && d.specified ? d.value : null
            });
            return a
        }(f);
        r.find = sa;
        r.expr = sa.selectors;
        r.expr[":"] = r.expr.pseudos;
        r.uniqueSort = r.unique = sa.uniqueSort;
        r.text = sa.getText;
        r.isXMLDoc = sa.isXML;
        r.contains = sa.contains;
        var va = function(c, a, b) {
                for (var d = [], g = b !== l;
                    (c = c[a]) && 9 !== c.nodeType;)
                    if (1 === c.nodeType) {
                        if (g && r(c).is(b)) break;
                        d.push(c)
                    } return d
            },
            ab = function(c, a) {
                for (var b = []; c; c = c.nextSibling) 1 === c.nodeType && c !== a && b.push(c);
                return b
            },
            bb = r.expr.match.needsContext,
            cb = /^<([\w-]+)\s*\/?>(?:<\/\1>|)$/,
            ob = /^.[^:#\[\.,]*$/;
        r.filter = function(c, a, b) {
            var d = a[0];
            b && (c = ":not(" + c + ")");
            return 1 === a.length && 1 === d.nodeType ? r.find.matchesSelector(d, c) ? [d] : [] : r.find.matches(c, r.grep(a, function(c) {
                return 1 === c.nodeType
            }))
        };
        r.fn.extend({
            find: function(c) {
                var a, b = this.length,
                    d = [],
                    g = this;
                if ("string" !== typeof c) return this.pushStack(r(c).filter(function() {
                    for (a = 0; a < b; a++)
                        if (r.contains(g[a], this)) return !0
                }));
                for (a = 0; a < b; a++) r.find(c, g[a], d);
                d = this.pushStack(1 < b ? r.unique(d) : d);
                d.selector = this.selector ? this.selector +
                    " " + c : c;
                return d
            },
            filter: function(c) {
                return this.pushStack(b(this, c || [], !1))
            },
            not: function(c) {
                return this.pushStack(b(this, c || [], !0))
            },
            is: function(c) {
                return !!b(this, "string" === typeof c && bb.test(c) ? r(c) : c || [], !1).length
            }
        });
        var Db = /^(?:\s*(<[\w\W]+>)[^>]*|#([\w-]*))$/;
        (r.fn.init = function(c, a, b) {
            if (!c) return this;
            b = b || Eb;
            if ("string" === typeof c) {
                var d = "\x3c" === c[0] && "\x3e" === c[c.length - 1] && 3 <= c.length ? [null, c, null] : Db.exec(c);
                if (!d || !d[1] && a) return !a || a.jquery ? (a || b).find(c) : this.constructor(a).find(c);
                if (d[1]) {
                    if (a = a instanceof r ? a[0] : a, r.merge(this, r.parseHTML(d[1], a && a.nodeType ? a.ownerDocument || a : I, !0)), cb.test(d[1]) && r.isPlainObject(a))
                        for (d in a)
                            if (r.isFunction(this[d])) this[d](a[d]);
                            else this.attr(d, a[d])
                } else(a = I.getElementById(d[2])) && a.parentNode && (this.length = 1, this[0] = a), this.context = I, this.selector = c;
                return this
            }
            if (c.nodeType) return this.context = this[0] = c, this.length = 1, this;
            if (r.isFunction(c)) return b.ready !== l ? b.ready(c) : c(r);
            c.selector !== l && (this.selector = c.selector, this.context = c.context);
            return r.makeArray(c, this)
        }).prototype = r.fn;
        var Eb = r(I);
        var Fb = /^(?:parents|prev(?:Until|All))/,
            Gb = {
                children: !0,
                contents: !0,
                next: !0,
                prev: !0
            };
        r.fn.extend({
            has: function(c) {
                var a = r(c, this),
                    b = a.length;
                return this.filter(function() {
                    for (var c = 0; c < b; c++)
                        if (r.contains(this, a[c])) return !0
                })
            },
            closest: function(c, a) {
                for (var b, d = 0, g = this.length, p = [], h = bb.test(c) || "string" !== typeof c ? r(c, a || this.context) : 0; d < g; d++)
                    for (b = this[d]; b && b !== a; b = b.parentNode)
                        if (11 > b.nodeType && (h ? -1 < h.index(b) : 1 === b.nodeType && r.find.matchesSelector(b,
                                c))) {
                            p.push(b);
                            break
                        } return this.pushStack(1 < p.length ? r.uniqueSort(p) : p)
            },
            index: function(c) {
                return c ? "string" === typeof c ? Ca.call(r(c), this[0]) : Ca.call(this, c.jquery ? c[0] : c) : this[0] && this[0].parentNode ? this.first().prevAll().length : -1
            },
            add: function(c, a) {
                return this.pushStack(r.uniqueSort(r.merge(this.get(), r(c, a))))
            },
            addBack: function(c) {
                return this.add(null == c ? this.prevObject : this.prevObject.filter(c))
            }
        });
        r.each({
            parent: function(c) {
                return (c = c.parentNode) && 11 !== c.nodeType ? c : null
            },
            parents: function(c) {
                return va(c,
                    "parentNode")
            },
            parentsUntil: function(c, a, b) {
                return va(c, "parentNode", b)
            },
            next: function(c) {
                return d(c, "nextSibling")
            },
            prev: function(c) {
                return d(c, "previousSibling")
            },
            nextAll: function(c) {
                return va(c, "nextSibling")
            },
            prevAll: function(c) {
                return va(c, "previousSibling")
            },
            nextUntil: function(c, a, b) {
                return va(c, "nextSibling", b)
            },
            prevUntil: function(c, a, b) {
                return va(c, "previousSibling", b)
            },
            siblings: function(c) {
                return ab((c.parentNode || {}).firstChild, c)
            },
            children: function(c) {
                return ab(c.firstChild)
            },
            contents: function(c) {
                return c.contentDocument ||
                    r.merge([], c.childNodes)
            }
        }, function(c, a) {
            r.fn[c] = function(b, d) {
                var g = r.map(this, a, b);
                "Until" !== c.slice(-5) && (d = b);
                d && "string" === typeof d && (g = r.filter(d, g));
                1 < this.length && (Gb[c] || r.uniqueSort(g), Fb.test(c) && g.reverse());
                return this.pushStack(g)
            }
        });
        var ka = /\S+/g;
        r.Callbacks = function(c) {
            c = "string" === typeof c ? h(c) : r.extend({}, c);
            var a, b, d, g, p = [],
                e = [],
                m = -1,
                n = function() {
                    g = c.once;
                    for (d = a = !0; e.length; m = -1)
                        for (b = e.shift(); ++m < p.length;) !1 === p[m].apply(b[0], b[1]) && c.stopOnFalse && (m = p.length, b = !1);
                    c.memory ||
                        (b = !1);
                    a = !1;
                    g && (p = b ? [] : "")
                },
                v = {
                    add: function() {
                        p && (b && !a && (m = p.length - 1, e.push(b)), function ub(a) {
                            r.each(a, function(a, b) {
                                r.isFunction(b) ? c.unique && v.has(b) || p.push(b) : b && b.length && "string" !== r.type(b) && ub(b)
                            })
                        }(arguments), b && !a && n());
                        return this
                    },
                    remove: function() {
                        r.each(arguments, function(c, a) {
                            for (var b; - 1 < (b = r.inArray(a, p, b));) p.splice(b, 1), b <= m && m--
                        });
                        return this
                    },
                    has: function(c) {
                        return c ? -1 < r.inArray(c, p) : 0 < p.length
                    },
                    empty: function() {
                        p && (p = []);
                        return this
                    },
                    disable: function() {
                        g = e = [];
                        p = b = "";
                        return this
                    },
                    disabled: function() {
                        return !p
                    },
                    lock: function() {
                        g = e = [];
                        b || (p = b = "");
                        return this
                    },
                    locked: function() {
                        return !!g
                    },
                    fireWith: function(c, b) {
                        g || (b = b || [], b = [c, b.slice ? b.slice() : b], e.push(b), a || n());
                        return this
                    },
                    fire: function() {
                        v.fireWith(this, arguments);
                        return this
                    },
                    fired: function() {
                        return !!d
                    }
                };
            return v
        };
        r.extend({
            Deferred: function(c) {
                var a = [
                        ["resolve", "done", r.Callbacks("once memory"), "resolved"],
                        ["reject", "fail", r.Callbacks("once memory"), "rejected"],
                        ["notify", "progress", r.Callbacks("memory")]
                    ],
                    b = "pending",
                    d = {
                        state: function() {
                            return b
                        },
                        always: function() {
                            g.done(arguments).fail(arguments);
                            return this
                        },
                        then: function() {
                            var c = arguments;
                            return r.Deferred(function(b) {
                                r.each(a, function(a, p) {
                                    var h = r.isFunction(c[a]) && c[a];
                                    g[p[1]](function() {
                                        var c = h && h.apply(this, arguments);
                                        if (c && r.isFunction(c.promise)) c.promise().progress(b.notify).done(b.resolve).fail(b.reject);
                                        else b[p[0] + "With"](this === d ? b.promise() : this, h ? [c] : arguments)
                                    })
                                });
                                c = null
                            }).promise()
                        },
                        promise: function(c) {
                            return null != c ? r.extend(c, d) : d
                        }
                    },
                    g = {};
                d.pipe =
                    d.then;
                r.each(a, function(c, p) {
                    var h = p[2],
                        e = p[3];
                    d[p[1]] = h.add;
                    e && h.add(function() {
                        b = e
                    }, a[c ^ 1][2].disable, a[2][2].lock);
                    g[p[0]] = function() {
                        g[p[0] + "With"](this === g ? d : this, arguments);
                        return this
                    };
                    g[p[0] + "With"] = h.fireWith
                });
                d.promise(g);
                c && c.call(g, g);
                return g
            },
            when: function(c) {
                var a = 0,
                    b = oa.call(arguments),
                    d = b.length,
                    g = 1 !== d || c && r.isFunction(c.promise) ? d : 0,
                    p = 1 === g ? c : r.Deferred(),
                    h = function(c, a, b) {
                        return function(d) {
                            a[c] = this;
                            b[c] = 1 < arguments.length ? oa.call(arguments) : d;
                            b === m ? p.notifyWith(a, b) : --g || p.resolveWith(a,
                                b)
                        }
                    },
                    e;
                if (1 < d) {
                    var m = Array(d);
                    var n = Array(d);
                    for (e = Array(d); a < d; a++) b[a] && r.isFunction(b[a].promise) ? b[a].promise().progress(h(a, n, m)).done(h(a, e, b)).fail(p.reject) : --g
                }
                g || p.resolveWith(e, b);
                return p.promise()
            }
        });
        var Ga;
        r.fn.ready = function(c) {
            r.ready.promise().done(c);
            return this
        };
        r.extend({
            isReady: !1,
            readyWait: 1,
            holdReady: function(c) {
                c ? r.readyWait++ : r.ready(!0)
            },
            ready: function(c) {
                (!0 === c ? --r.readyWait : r.isReady) || (r.isReady = !0, !0 !== c && 0 < --r.readyWait || (Ga.resolveWith(I, [r]), r.fn.triggerHandler &&
                    (r(I).triggerHandler("ready"), r(I).off("ready"))))
            }
        });
        r.ready.promise = function(c) {
            Ga || (Ga = r.Deferred(), "complete" === I.readyState || "loading" !== I.readyState && !I.documentElement.doScroll ? f.setTimeout(r.ready) : (I.addEventListener("DOMContentLoaded", a), f.addEventListener("load", a)));
            return Ga.promise(c)
        };
        r.ready.promise();
        var ja = function(c, a, b, d, g, p, h) {
                var e = 0,
                    m = c.length,
                    n = null == b;
                if ("object" === r.type(b))
                    for (e in g = !0, b) ja(c, a, e, b[e], !0, p, h);
                else if (d !== l && (g = !0, r.isFunction(d) || (h = !0), n && (h ? (a.call(c,
                        d), a = null) : (n = a, a = function(c, a, b) {
                        return n.call(r(c), b)
                    })), a))
                    for (; e < m; e++) a(c[e], b, h ? d : d.call(c[e], e, a(c[e], b)));
                return g ? c : n ? a.call(c) : m ? a(c[0], b) : p
            },
            xa = function(c) {
                return 1 === c.nodeType || 9 === c.nodeType || !+c.nodeType
            };
        g.uid = 1;
        g.prototype = {
            register: function(c, a) {
                a = a || {};
                c.nodeType ? c[this.expando] = a : Object.defineProperty(c, this.expando, {
                    value: a,
                    writable: !0,
                    configurable: !0
                });
                return c[this.expando]
            },
            cache: function(c) {
                if (!xa(c)) return {};
                var a = c[this.expando];
                a || (a = {}, xa(c) && (c.nodeType ? c[this.expando] =
                    a : Object.defineProperty(c, this.expando, {
                        value: a,
                        configurable: !0
                    })));
                return a
            },
            set: function(c, a, b) {
                var d;
                c = this.cache(c);
                if ("string" === typeof a) c[a] = b;
                else
                    for (d in a) c[d] = a[d];
                return c
            },
            get: function(c, a) {
                return a === l ? this.cache(c) : c[this.expando] && c[this.expando][a]
            },
            access: function(c, a, b) {
                if (a === l || a && "string" === typeof a && b === l) return b = this.get(c, a), b !== l ? b : this.get(c, r.camelCase(a));
                this.set(c, a, b);
                return b !== l ? b : a
            },
            remove: function(c, a) {
                var b = c[this.expando];
                if (b !== l) {
                    if (a === l) this.register(c);
                    else {
                        if (r.isArray(a)) var d = a.concat(a.map(r.camelCase));
                        else {
                            var g = r.camelCase(a);
                            a in b ? d = [a, g] : (d = g, d = d in b ? [d] : d.match(ka) || [])
                        }
                        for (g = d.length; g--;) delete b[d[g]]
                    }
                    if (a === l || r.isEmptyObject(b)) c.nodeType ? c[this.expando] = l : delete c[this.expando]
                }
            },
            hasData: function(c) {
                c = c[this.expando];
                return c !== l && !r.isEmptyObject(c)
            }
        };
        var M = new g,
            Y = new g,
            pb = /^(?:\{[\w\W]*\}|\[[\w\W]*\])$/,
            Ta = /[A-Z]/g;
        r.extend({
            hasData: function(c) {
                return Y.hasData(c) || M.hasData(c)
            },
            data: function(c, a, b) {
                return Y.access(c, a, b)
            },
            removeData: function(c, a) {
                Y.remove(c, a)
            },
            _data: function(c, a, b) {
                return M.access(c, a, b)
            },
            _removeData: function(c, a) {
                M.remove(c, a)
            }
        });
        r.fn.extend({
            data: function(c, a) {
                var b, d = this[0],
                    g = d && d.attributes;
                if (c === l) {
                    if (this.length) {
                        var p = Y.get(d);
                        if (1 === d.nodeType && !M.get(d, "hasDataAttrs")) {
                            for (b = g.length; b--;)
                                if (g[b]) {
                                    var h = g[b].name;
                                    0 === h.indexOf("data-") && (h = r.camelCase(h.slice(5)), n(d, h, p[h]))
                                } M.set(d, "hasDataAttrs", !0)
                        }
                    }
                    return p
                }
                return "object" === typeof c ? this.each(function() {
                    Y.set(this, c)
                }) : ja(this, function(a) {
                    if (d &&
                        a === l) {
                        var b = Y.get(d, c) || Y.get(d, c.replace(Ta, "-$\x26").toLowerCase());
                        if (b !== l) return b;
                        var g = r.camelCase(c);
                        b = Y.get(d, g);
                        if (b !== l) return b;
                        b = n(d, g, l);
                        if (b !== l) return b
                    } else g = r.camelCase(c), this.each(function() {
                        var b = Y.get(this, g);
                        Y.set(this, g, a); - 1 < c.indexOf("-") && b !== l && Y.set(this, c, a)
                    })
                }, null, a, 1 < arguments.length, null, !0)
            },
            removeData: function(c) {
                return this.each(function() {
                    Y.remove(this, c)
                })
            }
        });
        r.extend({
            queue: function(c, a, b) {
                if (c) {
                    a = (a || "fx") + "queue";
                    var d = M.get(c, a);
                    b && (!d || r.isArray(b) ? d =
                        M.access(c, a, r.makeArray(b)) : d.push(b));
                    return d || []
                }
            },
            dequeue: function(c, a) {
                a = a || "fx";
                var b = r.queue(c, a),
                    d = b.length,
                    g = b.shift(),
                    p = r._queueHooks(c, a),
                    h = function() {
                        r.dequeue(c, a)
                    };
                "inprogress" === g && (g = b.shift(), d--);
                g && ("fx" === a && b.unshift("inprogress"), delete p.stop, g.call(c, h, p));
                !d && p && p.empty.fire()
            },
            _queueHooks: function(c, a) {
                var b = a + "queueHooks";
                return M.get(c, b) || M.access(c, b, {
                    empty: r.Callbacks("once memory").add(function() {
                        M.remove(c, [a + "queue", b])
                    })
                })
            }
        });
        r.fn.extend({
            queue: function(c, a) {
                var b =
                    2;
                "string" !== typeof c && (a = c, c = "fx", b--);
                return arguments.length < b ? r.queue(this[0], c) : a === l ? this : this.each(function() {
                    var b = r.queue(this, c, a);
                    r._queueHooks(this, c);
                    "fx" === c && "inprogress" !== b[0] && r.dequeue(this, c)
                })
            },
            dequeue: function(c) {
                return this.each(function() {
                    r.dequeue(this, c)
                })
            },
            clearQueue: function(c) {
                return this.queue(c || "fx", [])
            },
            promise: function(c, a) {
                var b, d = 1,
                    g = r.Deferred(),
                    p = this,
                    h = this.length,
                    e = function() {
                        --d || g.resolveWith(p, [p])
                    };
                "string" !== typeof c && (a = c, c = l);
                for (c = c || "fx"; h--;)(b = M.get(p[h],
                    c + "queueHooks")) && b.empty && (d++, b.empty.add(e));
                e();
                return g.promise(a)
            }
        });
        var db = /[+-]?(?:\d*\.|)\d+(?:[eE][+-]?\d+|)/.source,
            pa = new RegExp("^(?:([+-])\x3d|)(" + db + ")([a-z%]*)$", "i"),
            la = ["Top", "Right", "Bottom", "Left"],
            ma = function(c, a) {
                c = a || c;
                return "none" === r.css(c, "display") || !r.contains(c.ownerDocument, c)
            },
            eb = /^(?:checkbox|radio)$/i,
            Ua = /<([\w:-]+)/,
            Va = /^$|\/(?:java|ecma)script/i,
            ba = {
                option: [1, "\x3cselect multiple\x3d'multiple'\x3e", "\x3c/select\x3e"],
                thead: [1, "\x3ctable\x3e", "\x3c/table\x3e"],
                col: [2,
                    "\x3ctable\x3e\x3ccolgroup\x3e", "\x3c/colgroup\x3e\x3c/table\x3e"
                ],
                tr: [2, "\x3ctable\x3e\x3ctbody\x3e", "\x3c/tbody\x3e\x3c/table\x3e"],
                td: [3, "\x3ctable\x3e\x3ctbody\x3e\x3ctr\x3e", "\x3c/tr\x3e\x3c/tbody\x3e\x3c/table\x3e"],
                _default: [0, "", ""]
            };
        ba.optgroup = ba.option;
        ba.tbody = ba.tfoot = ba.colgroup = ba.caption = ba.thead;
        ba.th = ba.td;
        var rb = /<|&#?\w+;/;
        (function() {
            var c = I.createDocumentFragment().appendChild(I.createElement("div")),
                a = I.createElement("input");
            a.setAttribute("type", "radio");
            a.setAttribute("checked",
                "checked");
            a.setAttribute("name", "t");
            c.appendChild(a);
            T.checkClone = c.cloneNode(!0).cloneNode(!0).lastChild.checked;
            c.innerHTML = "\x3ctextarea\x3ex\x3c/textarea\x3e";
            T.noCloneChecked = !!c.cloneNode(!0).lastChild.defaultValue
        })();
        var Hb = /^key/,
            Ib = /^(?:mouse|pointer|contextmenu|drag|drop)|click/,
            fb = /^([^.]*)(?:\.(.+)|)/;
        r.event = {
            global: {},
            add: function(c, a, b, d, g) {
                var p, h, e, m, n;
                if (e = M.get(c)) {
                    if (b.handler) {
                        var v = b;
                        b = v.handler;
                        g = v.selector
                    }
                    b.guid || (b.guid = r.guid++);
                    (h = e.events) || (h = e.events = {});
                    (p = e.handle) ||
                    (p = e.handle = function(a) {
                        return "undefined" !== typeof r && r.event.triggered !== a.type ? r.event.dispatch.apply(c, arguments) : l
                    });
                    a = (a || "").match(ka) || [""];
                    for (e = a.length; e--;) {
                        var f = fb.exec(a[e]) || [];
                        var k = m = f[1];
                        var A = (f[2] || "").split(".").sort();
                        k && (f = r.event.special[k] || {}, k = (g ? f.delegateType : f.bindType) || k, f = r.event.special[k] || {}, m = r.extend({
                            type: k,
                            origType: m,
                            data: d,
                            handler: b,
                            guid: b.guid,
                            selector: g,
                            needsContext: g && r.expr.match.needsContext.test(g),
                            namespace: A.join(".")
                        }, v), (n = h[k]) || (n = h[k] = [], n.delegateCount =
                            0, f.setup && !1 !== f.setup.call(c, d, A, p) || c.addEventListener && c.addEventListener(k, p)), f.add && (f.add.call(c, m), m.handler.guid || (m.handler.guid = b.guid)), g ? n.splice(n.delegateCount++, 0, m) : n.push(m), r.event.global[k] = !0)
                    }
                }
            },
            remove: function(c, a, b, d, g) {
                var p, h, e, m, n, v = M.hasData(c) && M.get(c);
                if (v && (e = v.events)) {
                    a = (a || "").match(ka) || [""];
                    for (m = a.length; m--;) {
                        var f = fb.exec(a[m]) || [];
                        var k = n = f[1];
                        var A = (f[2] || "").split(".").sort();
                        if (k) {
                            var x = r.event.special[k] || {};
                            k = (d ? x.delegateType : x.bindType) || k;
                            var u = e[k] || [];
                            f = f[2] && new RegExp("(^|\\.)" + A.join("\\.(?:.*\\.|)") + "(\\.|$)");
                            for (h = p = u.length; p--;) {
                                var w = u[p];
                                !g && n !== w.origType || b && b.guid !== w.guid || f && !f.test(w.namespace) || d && d !== w.selector && ("**" !== d || !w.selector) || (u.splice(p, 1), w.selector && u.delegateCount--, x.remove && x.remove.call(c, w))
                            }
                            h && !u.length && (x.teardown && !1 !== x.teardown.call(c, A, v.handle) || r.removeEvent(c, k, v.handle), delete e[k])
                        } else
                            for (k in e) r.event.remove(c, k + a[m], b, d, !0)
                    }
                    r.isEmptyObject(e) && M.remove(c, "handle events")
                }
            },
            dispatch: function(c) {
                c =
                    r.event.fix(c);
                var a, b, d, g = oa.call(arguments);
                var p = (M.get(this, "events") || {})[c.type] || [];
                var h = r.event.special[c.type] || {};
                g[0] = c;
                c.delegateTarget = this;
                if (!h.preDispatch || !1 !== h.preDispatch.call(this, c)) {
                    var e = r.event.handlers.call(this, c, p);
                    for (p = 0;
                        (d = e[p++]) && !c.isPropagationStopped();)
                        for (c.currentTarget = d.elem, a = 0;
                            (b = d.handlers[a++]) && !c.isImmediatePropagationStopped();)
                            if (!c.rnamespace || c.rnamespace.test(b.namespace)) c.handleObj = b, c.data = b.data, b = ((r.event.special[b.origType] || {}).handle ||
                                b.handler).apply(d.elem, g), b !== l && !1 === (c.result = b) && (c.preventDefault(), c.stopPropagation());
                    h.postDispatch && h.postDispatch.call(this, c);
                    return c.result
                }
            },
            handlers: function(c, a) {
                var b, d = [],
                    g = a.delegateCount,
                    p = c.target;
                if (g && p.nodeType && ("click" !== c.type || isNaN(c.button) || 1 > c.button))
                    for (; p !== this; p = p.parentNode || this)
                        if (1 === p.nodeType && (!0 !== p.disabled || "click" !== c.type)) {
                            var h = [];
                            for (b = 0; b < g; b++) {
                                var e = a[b];
                                var m = e.selector + " ";
                                h[m] === l && (h[m] = e.needsContext ? -1 < r(m, this).index(p) : r.find(m, this,
                                    null, [p]).length);
                                h[m] && h.push(e)
                            }
                            h.length && d.push({
                                elem: p,
                                handlers: h
                            })
                        } g < a.length && d.push({
                    elem: this,
                    handlers: a.slice(g)
                });
                return d
            },
            props: "altKey bubbles cancelable ctrlKey currentTarget detail eventPhase metaKey relatedTarget shiftKey target timeStamp view which".split(" "),
            fixHooks: {},
            keyHooks: {
                props: ["char", "charCode", "key", "keyCode"],
                filter: function(c, a) {
                    null == c.which && (c.which = null != a.charCode ? a.charCode : a.keyCode);
                    return c
                }
            },
            mouseHooks: {
                props: "button buttons clientX clientY offsetX offsetY pageX pageY screenX screenY toElement".split(" "),
                filter: function(c, a) {
                    var b = a.button;
                    if (null == c.pageX && null != a.clientX) {
                        var d = c.target.ownerDocument || I;
                        var g = d.documentElement;
                        d = d.body;
                        c.pageX = a.clientX + (g && g.scrollLeft || d && d.scrollLeft || 0) - (g && g.clientLeft || d && d.clientLeft || 0);
                        c.pageY = a.clientY + (g && g.scrollTop || d && d.scrollTop || 0) - (g && g.clientTop || d && d.clientTop || 0)
                    }
                    c.which || b === l || (c.which = b & 1 ? 1 : b & 2 ? 3 : b & 4 ? 2 : 0);
                    return c
                }
            },
            fix: function(c) {
                if (c[r.expando]) return c;
                var a = c.type;
                var b = c,
                    d = this.fixHooks[a];
                d || (this.fixHooks[a] = d = Ib.test(a) ? this.mouseHooks :
                    Hb.test(a) ? this.keyHooks : {});
                var g = d.props ? this.props.concat(d.props) : this.props;
                c = new r.Event(b);
                for (a = g.length; a--;) {
                    var p = g[a];
                    c[p] = b[p]
                }
                c.target || (c.target = I);
                3 === c.target.nodeType && (c.target = c.target.parentNode);
                return d.filter ? d.filter(c, b) : c
            },
            special: {
                load: {
                    noBubble: !0
                },
                focus: {
                    trigger: function() {
                        if (this !== y() && this.focus) return this.focus(), !1
                    },
                    delegateType: "focusin"
                },
                blur: {
                    trigger: function() {
                        if (this === y() && this.blur) return this.blur(), !1
                    },
                    delegateType: "focusout"
                },
                click: {
                    trigger: function() {
                        if ("checkbox" ===
                            this.type && this.click && r.nodeName(this, "input")) return this.click(), !1
                    },
                    _default: function(c) {
                        return r.nodeName(c.target, "a")
                    }
                },
                beforeunload: {
                    postDispatch: function(c) {
                        c.result !== l && c.originalEvent && (c.originalEvent.returnValue = c.result)
                    }
                }
            }
        };
        r.removeEvent = function(c, a, b) {
            c.removeEventListener && c.removeEventListener(a, b)
        };
        r.Event = function(c, a) {
            if (!(this instanceof r.Event)) return new r.Event(c, a);
            c && c.type ? (this.originalEvent = c, this.type = c.type, this.isDefaultPrevented = c.defaultPrevented || c.defaultPrevented ===
                l && !1 === c.returnValue ? w : t) : this.type = c;
            a && r.extend(this, a);
            this.timeStamp = c && c.timeStamp || r.now();
            this[r.expando] = !0
        };
        r.Event.prototype = {
            constructor: r.Event,
            isDefaultPrevented: t,
            isPropagationStopped: t,
            isImmediatePropagationStopped: t,
            isSimulated: !1,
            preventDefault: function() {
                var c = this.originalEvent;
                this.isDefaultPrevented = w;
                c && !this.isSimulated && c.preventDefault()
            },
            stopPropagation: function() {
                var c = this.originalEvent;
                this.isPropagationStopped = w;
                c && !this.isSimulated && c.stopPropagation()
            },
            stopImmediatePropagation: function() {
                var c =
                    this.originalEvent;
                this.isImmediatePropagationStopped = w;
                c && !this.isSimulated && c.stopImmediatePropagation();
                this.stopPropagation()
            }
        };
        r.each({
            mouseenter: "mouseover",
            mouseleave: "mouseout",
            pointerenter: "pointerover",
            pointerleave: "pointerout"
        }, function(c, a) {
            r.event.special[c] = {
                delegateType: a,
                bindType: a,
                handle: function(c) {
                    var b = c.relatedTarget,
                        d = c.handleObj;
                    if (!b || b !== this && !r.contains(this, b)) {
                        c.type = d.origType;
                        var g = d.handler.apply(this, arguments);
                        c.type = a
                    }
                    return g
                }
            }
        });
        r.fn.extend({
            on: function(a, b, d,
                g) {
                return c(this, a, b, d, g)
            },
            one: function(a, b, d, g) {
                return c(this, a, b, d, g, 1)
            },
            off: function(c, a, b) {
                if (c && c.preventDefault && c.handleObj) {
                    var d = c.handleObj;
                    r(c.delegateTarget).off(d.namespace ? d.origType + "." + d.namespace : d.origType, d.selector, d.handler);
                    return this
                }
                if ("object" === typeof c) {
                    for (d in c) this.off(d, a, c[d]);
                    return this
                }
                if (!1 === a || "function" === typeof a) b = a, a = l;
                !1 === b && (b = t);
                return this.each(function() {
                    r.event.remove(this, c, b, a)
                })
            }
        });
        var Jb = /<(?!area|br|col|embed|hr|img|input|link|meta|param)(([\w:-]+)[^>]*)\/>/gi,
            Kb = /<script|<style|<link/i,
            tb = /checked\s*(?:[^=]|=\s*.checked.)/i,
            sb = /^true\/(.*)/,
            vb = /^\s*<!(?:\[CDATA\[|--)|(?:\]\]|--)>\s*$/g;
        r.extend({
            htmlPrefilter: function(c) {
                return c.replace(Jb, "\x3c$1\x3e\x3c/$2\x3e")
            },
            clone: function(c, a, b) {
                var d, g = c.cloneNode(!0),
                    p = r.contains(c.ownerDocument, c);
                if (!(T.noCloneChecked || 1 !== c.nodeType && 11 !== c.nodeType || r.isXMLDoc(c))) {
                    var h = m(g);
                    var e = m(c);
                    var n = 0;
                    for (d = e.length; n < d; n++) {
                        var v = e[n],
                            f = h[n],
                            k = f.nodeName.toLowerCase();
                        if ("input" === k && eb.test(v.type)) f.checked =
                            v.checked;
                        else if ("input" === k || "textarea" === k) f.defaultValue = v.defaultValue
                    }
                }
                if (a)
                    if (b)
                        for (e = e || m(c), h = h || m(g), n = 0, d = e.length; n < d; n++) C(e[n], h[n]);
                    else C(c, g);
                h = m(g, "script");
                0 < h.length && x(h, !p && m(c, "script"));
                return g
            },
            cleanData: function(c) {
                for (var a, b, d, g = r.event.special, p = 0;
                    (b = c[p]) !== l; p++)
                    if (xa(b)) {
                        if (a = b[M.expando]) {
                            if (a.events)
                                for (d in a.events) g[d] ? r.event.remove(b, d) : r.removeEvent(b, d, a.handle);
                            b[M.expando] = l
                        }
                        b[Y.expando] && (b[Y.expando] = l)
                    }
            }
        });
        r.fn.extend({
            domManip: q,
            detach: function(c) {
                return F(this,
                    c, !0)
            },
            remove: function(c) {
                return F(this, c)
            },
            text: function(c) {
                return ja(this, function(c) {
                    return c === l ? r.text(this) : this.empty().each(function() {
                        if (1 === this.nodeType || 11 === this.nodeType || 9 === this.nodeType) this.textContent = c
                    })
                }, null, c, arguments.length)
            },
            append: function() {
                return q(this, arguments, function(c) {
                    1 !== this.nodeType && 11 !== this.nodeType && 9 !== this.nodeType || p(this, c).appendChild(c)
                })
            },
            prepend: function() {
                return q(this, arguments, function(c) {
                    if (1 === this.nodeType || 11 === this.nodeType || 9 === this.nodeType) {
                        var a =
                            p(this, c);
                        a.insertBefore(c, a.firstChild)
                    }
                })
            },
            before: function() {
                return q(this, arguments, function(c) {
                    this.parentNode && this.parentNode.insertBefore(c, this)
                })
            },
            after: function() {
                return q(this, arguments, function(c) {
                    this.parentNode && this.parentNode.insertBefore(c, this.nextSibling)
                })
            },
            empty: function() {
                for (var c, a = 0; null != (c = this[a]); a++) 1 === c.nodeType && (r.cleanData(m(c, !1)), c.textContent = "");
                return this
            },
            clone: function(c, a) {
                c = null == c ? !1 : c;
                a = null == a ? c : a;
                return this.map(function() {
                    return r.clone(this, c, a)
                })
            },
            html: function(c) {
                return ja(this, function(c) {
                    var a = this[0] || {},
                        b = 0,
                        d = this.length;
                    if (c === l && 1 === a.nodeType) return a.innerHTML;
                    if ("string" === typeof c && !Kb.test(c) && !ba[(Ua.exec(c) || ["", ""])[1].toLowerCase()]) {
                        c = r.htmlPrefilter(c);
                        try {
                            for (; b < d; b++) a = this[b] || {}, 1 === a.nodeType && (r.cleanData(m(a, !1)), a.innerHTML = c);
                            a = 0
                        } catch (fc) {}
                    }
                    a && this.empty().append(c)
                }, null, c, arguments.length)
            },
            replaceWith: function() {
                var c = [];
                return q(this, arguments, function(a) {
                    var b = this.parentNode;
                    0 > r.inArray(this, c) && (r.cleanData(m(this)),
                        b && b.replaceChild(a, this))
                }, c)
            }
        });
        r.each({
            appendTo: "append",
            prependTo: "prepend",
            insertBefore: "before",
            insertAfter: "after",
            replaceAll: "replaceWith"
        }, function(c, a) {
            r.fn[c] = function(c) {
                for (var b = [], d = r(c), g = d.length - 1, p = 0; p <= g; p++) c = p === g ? this : this.clone(!0), r(d[p])[a](c), La.apply(b, c.get());
                return this.pushStack(b)
            }
        });
        var Da, Xa = {
                HTML: "block",
                BODY: "block"
            },
            Ya = /^margin/,
            Ja = new RegExp("^(" + db + ")(?!px)[a-z%]+$", "i"),
            Ea = function(c) {
                var a = c.ownerDocument.defaultView;
                a && a.opener || (a = f);
                return a.getComputedStyle(c)
            },
            Na = function(c, a, b, d) {
                var g, p = {};
                for (g in a) p[g] = c.style[g], c.style[g] = a[g];
                b = b.apply(c, d || []);
                for (g in a) c.style[g] = p[g];
                return b
            },
            ya = I.documentElement;
        (function() {
            function c() {
                h.style.cssText = "-webkit-box-sizing:border-box;-moz-box-sizing:border-box;box-sizing:border-box;position:relative;display:block;margin:auto;border:1px;padding:1px;top:1%;width:50%";
                h.innerHTML = "";
                ya.appendChild(p);
                var c = f.getComputedStyle(h);
                a = "1%" !== c.top;
                g = "2px" === c.marginLeft;
                b = "4px" === c.width;
                h.style.marginRight = "50%";
                d = "4px" === c.marginRight;
                ya.removeChild(p)
            }
            var a, b, d, g, p = I.createElement("div"),
                h = I.createElement("div");
            h.style && (h.style.backgroundClip = "content-box", h.cloneNode(!0).style.backgroundClip = "", T.clearCloneStyle = "content-box" === h.style.backgroundClip, p.style.cssText = "border:0;width:8px;height:0;top:0;left:-9999px;padding:0;margin-top:1px;position:absolute", p.appendChild(h), r.extend(T, {
                pixelPosition: function() {
                    c();
                    return a
                },
                boxSizingReliable: function() {
                    null == b && c();
                    return b
                },
                pixelMarginRight: function() {
                    null ==
                        b && c();
                    return d
                },
                reliableMarginLeft: function() {
                    null == b && c();
                    return g
                },
                reliableMarginRight: function() {
                    var c = h.appendChild(I.createElement("div"));
                    c.style.cssText = h.style.cssText = "-webkit-box-sizing:content-box;box-sizing:content-box;display:block;margin:0;border:0;padding:0";
                    c.style.marginRight = c.style.width = "0";
                    h.style.width = "1px";
                    ya.appendChild(p);
                    var a = !parseFloat(f.getComputedStyle(c).marginRight);
                    ya.removeChild(p);
                    h.removeChild(c);
                    return a
                }
            }))
        })();
        var Lb = /^(none|table(?!-c[ea]).+)/,
            Mb = {
                position: "absolute",
                visibility: "hidden",
                display: "block"
            },
            gb = {
                letterSpacing: "0",
                fontWeight: "400"
            },
            $a = ["Webkit", "O", "Moz", "ms"],
            Za = I.createElement("div").style;
        r.extend({
            cssHooks: {
                opacity: {
                    get: function(c, a) {
                        if (a) return c = K(c, "opacity"), "" === c ? "1" : c
                    }
                }
            },
            cssNumber: {
                animationIterationCount: !0,
                columnCount: !0,
                fillOpacity: !0,
                flexGrow: !0,
                flexShrink: !0,
                fontWeight: !0,
                lineHeight: !0,
                opacity: !0,
                order: !0,
                orphans: !0,
                widows: !0,
                zIndex: !0,
                zoom: !0
            },
            cssProps: {
                "float": "cssFloat"
            },
            style: function(c, a, b, d) {
                if (c && 3 !== c.nodeType && 8 !== c.nodeType &&
                    c.style) {
                    var g, p = r.camelCase(a),
                        h = c.style;
                    a = r.cssProps[p] || (r.cssProps[p] = P(p) || p);
                    var e = r.cssHooks[a] || r.cssHooks[p];
                    if (b !== l) {
                        var m = typeof b;
                        "string" === m && (g = pa.exec(b)) && g[1] && (b = v(c, a, g), m = "number");
                        null != b && b === b && ("number" === m && (b += g && g[3] || (r.cssNumber[p] ? "" : "px")), T.clearCloneStyle || "" !== b || 0 !== a.indexOf("background") || (h[a] = "inherit"), e && "set" in e && (b = e.set(c, b, d)) === l || (h[a] = b))
                    } else return e && "get" in e && (g = e.get(c, !1, d)) !== l ? g : h[a]
                }
            },
            css: function(c, a, b, d) {
                var g;
                var p = r.camelCase(a);
                a = r.cssProps[p] ||
                    (r.cssProps[p] = P(p) || p);
                (p = r.cssHooks[a] || r.cssHooks[p]) && "get" in p && (g = p.get(c, !0, b));
                g === l && (g = K(c, a, d));
                "normal" === g && a in gb && (g = gb[a]);
                return "" === b || b ? (c = parseFloat(g), !0 === b || isFinite(c) ? c || 0 : g) : g
            }
        });
        r.each(["height", "width"], function(c, a) {
            r.cssHooks[a] = {
                get: function(c, b, d) {
                    if (b) return Lb.test(r.css(c, "display")) && 0 === c.offsetWidth ? Na(c, Mb, function() {
                        return fa(c, a, d)
                    }) : fa(c, a, d)
                },
                set: function(c, b, d) {
                    var g, p = d && Ea(c);
                    (d = d && E(c, a, d, "border-box" === r.css(c, "boxSizing", !1, p), p)) && (g = pa.exec(b)) &&
                    "px" !== (g[3] || "px") && (c.style[a] = b, b = r.css(c, a));
                    return Z(c, b, d)
                }
            }
        });
        r.cssHooks.marginLeft = N(T.reliableMarginLeft, function(c, a) {
            if (a) return (parseFloat(K(c, "marginLeft")) || c.getBoundingClientRect().left - Na(c, {
                marginLeft: 0
            }, function() {
                return c.getBoundingClientRect().left
            })) + "px"
        });
        r.cssHooks.marginRight = N(T.reliableMarginRight, function(c, a) {
            if (a) return Na(c, {
                display: "inline-block"
            }, K, [c, "marginRight"])
        });
        r.each({
            margin: "",
            padding: "",
            border: "Width"
        }, function(c, a) {
            r.cssHooks[c + a] = {
                expand: function(b) {
                    var d =
                        0,
                        g = {};
                    for (b = "string" === typeof b ? b.split(" ") : [b]; 4 > d; d++) g[c + la[d] + a] = b[d] || b[d - 2] || b[0];
                    return g
                }
            };
            Ya.test(c) || (r.cssHooks[c + a].set = Z)
        });
        r.fn.extend({
            css: function(c, a) {
                return ja(this, function(c, a, b) {
                    var d, g = {},
                        p = 0;
                    if (r.isArray(a)) {
                        b = Ea(c);
                        for (d = a.length; p < d; p++) g[a[p]] = r.css(c, a[p], !1, b);
                        return g
                    }
                    return b !== l ? r.style(c, a, b) : r.css(c, a)
                }, c, a, 1 < arguments.length)
            },
            show: function() {
                return J(this, !0)
            },
            hide: function() {
                return J(this)
            },
            toggle: function(c) {
                return "boolean" === typeof c ? c ? this.show() : this.hide() :
                    this.each(function() {
                        ma(this) ? r(this).show() : r(this).hide()
                    })
            }
        });
        r.Tween = O;
        O.prototype = {
            constructor: O,
            init: function(c, a, b, d, g, p) {
                this.elem = c;
                this.prop = b;
                this.easing = g || r.easing._default;
                this.options = a;
                this.start = this.now = this.cur();
                this.end = d;
                this.unit = p || (r.cssNumber[b] ? "" : "px")
            },
            cur: function() {
                var c = O.propHooks[this.prop];
                return c && c.get ? c.get(this) : O.propHooks._default.get(this)
            },
            run: function(c) {
                var a, b = O.propHooks[this.prop];
                this.pos = this.options.duration ? a = r.easing[this.easing](c, this.options.duration *
                    c, 0, 1, this.options.duration) : a = c;
                this.now = (this.end - this.start) * a + this.start;
                this.options.step && this.options.step.call(this.elem, this.now, this);
                b && b.set ? b.set(this) : O.propHooks._default.set(this);
                return this
            }
        };
        O.prototype.init.prototype = O.prototype;
        O.propHooks = {
            _default: {
                get: function(c) {
                    return 1 !== c.elem.nodeType || null != c.elem[c.prop] && null == c.elem.style[c.prop] ? c.elem[c.prop] : (c = r.css(c.elem, c.prop, "")) && "auto" !== c ? c : 0
                },
                set: function(c) {
                    if (r.fx.step[c.prop]) r.fx.step[c.prop](c);
                    else 1 !== c.elem.nodeType ||
                        null == c.elem.style[r.cssProps[c.prop]] && !r.cssHooks[c.prop] ? c.elem[c.prop] = c.now : r.style(c.elem, c.prop, c.now + c.unit)
                }
            }
        };
        O.propHooks.scrollTop = O.propHooks.scrollLeft = {
            set: function(c) {
                c.elem.nodeType && c.elem.parentNode && (c.elem[c.prop] = c.now)
            }
        };
        r.easing = {
            linear: function(c) {
                return c
            },
            swing: function(c) {
                return .5 - Math.cos(c * Math.PI) / 2
            },
            _default: "swing"
        };
        r.fx = O.prototype.init;
        r.fx.step = {};
        var ta, Ha, Nb = /^(?:toggle|show|hide)$/,
            Ob = /queueHooks$/;
        r.Animation = r.extend(R, {
            tweeners: {
                "*": [function(c, a) {
                    var b = this.createTween(c,
                        a);
                    v(b.elem, c, pa.exec(a), b);
                    return b
                }]
            },
            tweener: function(c, a) {
                r.isFunction(c) ? (a = c, c = ["*"]) : c = c.match(ka);
                for (var b, d = 0, g = c.length; d < g; d++) b = c[d], R.tweeners[b] = R.tweeners[b] || [], R.tweeners[b].unshift(a)
            },
            prefilters: [function(c, a, b) {
                var d, g = this,
                    p = {},
                    h = c.style,
                    e = c.nodeType && ma(c),
                    m = M.get(c, "fxshow");
                if (!b.queue) {
                    var n = r._queueHooks(c, "fx");
                    if (null == n.unqueued) {
                        n.unqueued = 0;
                        var v = n.empty.fire;
                        n.empty.fire = function() {
                            n.unqueued || v()
                        }
                    }
                    n.unqueued++;
                    g.always(function() {
                        g.always(function() {
                            n.unqueued--;
                            r.queue(c, "fx").length || n.empty.fire()
                        })
                    })
                }
                if (1 === c.nodeType && ("height" in a || "width" in a)) {
                    b.overflow = [h.overflow, h.overflowX, h.overflowY];
                    var f = r.css(c, "display");
                    var k = "none" === f ? M.get(c, "olddisplay") || H(c.nodeName) : f;
                    "inline" === k && "none" === r.css(c, "float") && (h.display = "inline-block")
                }
                b.overflow && (h.overflow = "hidden", g.always(function() {
                    h.overflow = b.overflow[0];
                    h.overflowX = b.overflow[1];
                    h.overflowY = b.overflow[2]
                }));
                for (d in a)
                    if (k = a[d], Nb.exec(k)) {
                        delete a[d];
                        var A = A || "toggle" === k;
                        if (k === (e ? "hide" :
                                "show"))
                            if ("show" === k && m && m[d] !== l) e = !0;
                            else continue;
                        p[d] = m && m[d] || r.style(c, d)
                    } else f = l;
                if (r.isEmptyObject(p)) "inline" === ("none" === f ? H(c.nodeName) : f) && (h.display = f);
                else
                    for (d in m ? "hidden" in m && (e = m.hidden) : m = M.access(c, "fxshow", {}), A && (m.hidden = !e), e ? r(c).show() : g.done(function() {
                            r(c).hide()
                        }), g.done(function() {
                            var a;
                            M.remove(c, "fxshow");
                            for (a in p) r.style(c, a, p[a])
                        }), p) a = X(e ? m[d] : 0, d, g), d in m || (m[d] = a.start, e && (a.end = a.start, a.start = "width" === d || "height" === d ? 1 : 0))
            }],
            prefilter: function(c, a) {
                a ?
                    R.prefilters.unshift(c) : R.prefilters.push(c)
            }
        });
        r.speed = function(c, a, b) {
            var d = c && "object" === typeof c ? r.extend({}, c) : {
                complete: b || !b && a || r.isFunction(c) && c,
                duration: c,
                easing: b && a || a && !r.isFunction(a) && a
            };
            d.duration = r.fx.off ? 0 : "number" === typeof d.duration ? d.duration : d.duration in r.fx.speeds ? r.fx.speeds[d.duration] : r.fx.speeds._default;
            if (null == d.queue || !0 === d.queue) d.queue = "fx";
            d.old = d.complete;
            d.complete = function() {
                r.isFunction(d.old) && d.old.call(this);
                d.queue && r.dequeue(this, d.queue)
            };
            return d
        };
        r.fn.extend({
            fadeTo: function(c, a, b, d) {
                return this.filter(ma).css("opacity", 0).show().end().animate({
                    opacity: a
                }, c, b, d)
            },
            animate: function(c, a, b, d) {
                var g = r.isEmptyObject(c),
                    p = r.speed(a, b, d);
                a = function() {
                    var a = R(this, r.extend({}, c), p);
                    (g || M.get(this, "finish")) && a.stop(!0)
                };
                a.finish = a;
                return g || !1 === p.queue ? this.each(a) : this.queue(p.queue, a)
            },
            stop: function(c, a, b) {
                var d = function(c) {
                    var a = c.stop;
                    delete c.stop;
                    a(b)
                };
                "string" !== typeof c && (b = a, a = c, c = l);
                a && !1 !== c && this.queue(c || "fx", []);
                return this.each(function() {
                    var a = !0,
                        g = null != c && c + "queueHooks",
                        p = r.timers,
                        h = M.get(this);
                    if (g) h[g] && h[g].stop && d(h[g]);
                    else
                        for (g in h) h[g] && h[g].stop && Ob.test(g) && d(h[g]);
                    for (g = p.length; g--;) p[g].elem !== this || null != c && p[g].queue !== c || (p[g].anim.stop(b), a = !1, p.splice(g, 1));
                    !a && b || r.dequeue(this, c)
                })
            },
            finish: function(c) {
                !1 !== c && (c = c || "fx");
                return this.each(function() {
                    var a = M.get(this),
                        b = a[c + "queue"];
                    var d = a[c + "queueHooks"];
                    var g = r.timers,
                        p = b ? b.length : 0;
                    a.finish = !0;
                    r.queue(this, c, []);
                    d && d.stop && d.stop.call(this, !0);
                    for (d = g.length; d--;) g[d].elem ===
                        this && g[d].queue === c && (g[d].anim.stop(!0), g.splice(d, 1));
                    for (d = 0; d < p; d++) b[d] && b[d].finish && b[d].finish.call(this);
                    delete a.finish
                })
            }
        });
        r.each(["toggle", "show", "hide"], function(c, a) {
            var b = r.fn[a];
            r.fn[a] = function(c, d, g) {
                return null == c || "boolean" === typeof c ? b.apply(this, arguments) : this.animate(V(a, !0), c, d, g)
            }
        });
        r.each({
            slideDown: V("show"),
            slideUp: V("hide"),
            slideToggle: V("toggle"),
            fadeIn: {
                opacity: "show"
            },
            fadeOut: {
                opacity: "hide"
            },
            fadeToggle: {
                opacity: "toggle"
            }
        }, function(c, a) {
            r.fn[c] = function(c, b, d) {
                return this.animate(a,
                    c, b, d)
            }
        });
        r.timers = [];
        r.fx.tick = function() {
            var c = 0,
                a = r.timers;
            for (ta = r.now(); c < a.length; c++) {
                var b = a[c];
                b() || a[c] !== b || a.splice(c--, 1)
            }
            a.length || r.fx.stop();
            ta = l
        };
        r.fx.timer = function(c) {
            r.timers.push(c);
            c() ? r.fx.start() : r.timers.pop()
        };
        r.fx.interval = 13;
        r.fx.start = function() {
            Ha || (Ha = f.setInterval(r.fx.tick, r.fx.interval))
        };
        r.fx.stop = function() {
            f.clearInterval(Ha);
            Ha = null
        };
        r.fx.speeds = {
            slow: 600,
            fast: 200,
            _default: 400
        };
        r.fn.delay = function(c, a) {
            c = r.fx ? r.fx.speeds[c] || c : c;
            return this.queue(a || "fx", function(a,
                b) {
                var d = f.setTimeout(a, c);
                b.stop = function() {
                    f.clearTimeout(d)
                }
            })
        };
        (function() {
            var c = I.createElement("input"),
                a = I.createElement("select"),
                b = a.appendChild(I.createElement("option"));
            c.type = "checkbox";
            T.checkOn = "" !== c.value;
            T.optSelected = b.selected;
            a.disabled = !0;
            T.optDisabled = !b.disabled;
            c = I.createElement("input");
            c.value = "t";
            c.type = "radio";
            T.radioValue = "t" === c.value
        })();
        var za = r.expr.attrHandle;
        r.fn.extend({
            attr: function(c, a) {
                return ja(this, r.attr, c, a, 1 < arguments.length)
            },
            removeAttr: function(c) {
                return this.each(function() {
                    r.removeAttr(this,
                        c)
                })
            }
        });
        r.extend({
            attr: function(c, a, b) {
                var d, g = c.nodeType;
                if (3 !== g && 8 !== g && 2 !== g) {
                    if ("undefined" === typeof c.getAttribute) return r.prop(c, a, b);
                    if (1 !== g || !r.isXMLDoc(c)) {
                        a = a.toLowerCase();
                        var p = r.attrHooks[a] || (r.expr.match.bool.test(a) ? Pb : l)
                    }
                    if (b !== l) {
                        if (null === b) {
                            r.removeAttr(c, a);
                            return
                        }
                        if (p && "set" in p && (d = p.set(c, b, a)) !== l) return d;
                        c.setAttribute(a, b + "");
                        return b
                    }
                    if (p && "get" in p && null !== (d = p.get(c, a))) return d;
                    d = r.find.attr(c, a);
                    return null == d ? l : d
                }
            },
            attrHooks: {
                type: {
                    set: function(c, a) {
                        if (!T.radioValue &&
                            "radio" === a && r.nodeName(c, "input")) {
                            var b = c.value;
                            c.setAttribute("type", a);
                            b && (c.value = b);
                            return a
                        }
                    }
                }
            },
            removeAttr: function(c, a) {
                var b = 0,
                    d = a && a.match(ka);
                if (d && 1 === c.nodeType)
                    for (; a = d[b++];) {
                        var g = r.propFix[a] || a;
                        r.expr.match.bool.test(a) && (c[g] = !1);
                        c.removeAttribute(a)
                    }
            }
        });
        var Pb = {
            set: function(c, a, b) {
                !1 === a ? r.removeAttr(c, b) : c.setAttribute(b, b);
                return b
            }
        };
        r.each(r.expr.match.bool.source.match(/\w+/g), function(c, a) {
            var b = za[a] || r.find.attr;
            za[a] = function(c, a, d) {
                if (!d) {
                    var g = za[a];
                    za[a] = p;
                    var p = null !=
                        b(c, a, d) ? a.toLowerCase() : null;
                    za[a] = g
                }
                return p
            }
        });
        var Qb = /^(?:input|select|textarea|button)$/i,
            Rb = /^(?:a|area)$/i;
        r.fn.extend({
            prop: function(c, a) {
                return ja(this, r.prop, c, a, 1 < arguments.length)
            },
            removeProp: function(c) {
                return this.each(function() {
                    delete this[r.propFix[c] || c]
                })
            }
        });
        r.extend({
            prop: function(c, a, b) {
                var d, g = c.nodeType;
                if (3 !== g && 8 !== g && 2 !== g) {
                    if (1 !== g || !r.isXMLDoc(c)) {
                        a = r.propFix[a] || a;
                        var p = r.propHooks[a]
                    }
                    return b !== l ? p && "set" in p && (d = p.set(c, b, a)) !== l ? d : c[a] = b : p && "get" in p && null !== (d = p.get(c,
                        a)) ? d : c[a]
                }
            },
            propHooks: {
                tabIndex: {
                    get: function(c) {
                        var a = r.find.attr(c, "tabindex");
                        return a ? parseInt(a, 10) : Qb.test(c.nodeName) || Rb.test(c.nodeName) && c.href ? 0 : -1
                    }
                }
            },
            propFix: {
                "for": "htmlFor",
                "class": "className"
            }
        });
        T.optSelected || (r.propHooks.selected = {
            get: function(c) {
                (c = c.parentNode) && c.parentNode && c.parentNode.selectedIndex;
                return null
            },
            set: function(c) {
                if (c = c.parentNode) c.selectedIndex, c.parentNode && c.parentNode.selectedIndex
            }
        });
        r.each("tabIndex readOnly maxLength cellSpacing cellPadding rowSpan colSpan useMap frameBorder contentEditable".split(" "),
            function() {
                r.propFix[this.toLowerCase()] = this
            });
        var Oa = /[\t\r\n\f]/g;
        r.fn.extend({
            addClass: function(c) {
                var a, b, d, g, p, h = 0;
                if (r.isFunction(c)) return this.each(function(a) {
                    r(this).addClass(c.call(this, a, U(this)))
                });
                if ("string" === typeof c && c)
                    for (a = c.match(ka) || []; b = this[h++];) {
                        var e = U(b);
                        if (d = 1 === b.nodeType && (" " + e + " ").replace(Oa, " ")) {
                            for (p = 0; g = a[p++];) 0 > d.indexOf(" " + g + " ") && (d += g + " ");
                            d = r.trim(d);
                            e !== d && b.setAttribute("class", d)
                        }
                    }
                return this
            },
            removeClass: function(c) {
                var a, b, d, g, p, h = 0;
                if (r.isFunction(c)) return this.each(function(a) {
                    r(this).removeClass(c.call(this,
                        a, U(this)))
                });
                if (!arguments.length) return this.attr("class", "");
                if ("string" === typeof c && c)
                    for (a = c.match(ka) || []; b = this[h++];) {
                        var e = U(b);
                        if (d = 1 === b.nodeType && (" " + e + " ").replace(Oa, " ")) {
                            for (p = 0; g = a[p++];)
                                for (; - 1 < d.indexOf(" " + g + " ");) d = d.replace(" " + g + " ", " ");
                            d = r.trim(d);
                            e !== d && b.setAttribute("class", d)
                        }
                    }
                return this
            },
            toggleClass: function(c, a) {
                var b = typeof c;
                return "boolean" === typeof a && "string" === b ? a ? this.addClass(c) : this.removeClass(c) : r.isFunction(c) ? this.each(function(b) {
                    r(this).toggleClass(c.call(this,
                        b, U(this), a), a)
                }) : this.each(function() {
                    var a, d;
                    if ("string" === b) {
                        var g = 0;
                        var p = r(this);
                        for (d = c.match(ka) || []; a = d[g++];) p.hasClass(a) ? p.removeClass(a) : p.addClass(a)
                    } else if (c === l || "boolean" === b)(a = U(this)) && M.set(this, "__className__", a), this.setAttribute && this.setAttribute("class", a || !1 === c ? "" : M.get(this, "__className__") || "")
                })
            },
            hasClass: function(c) {
                var a, b = 0;
                for (c = " " + c + " "; a = this[b++];)
                    if (1 === a.nodeType && -1 < (" " + U(a) + " ").replace(Oa, " ").indexOf(c)) return !0;
                return !1
            }
        });
        var Sb = /\r/g,
            Tb = /[\x20\t\r\n\f]+/g;
        r.fn.extend({
            val: function(c) {
                var a, b, d = this[0];
                if (arguments.length) {
                    var g = r.isFunction(c);
                    return this.each(function(b) {
                        1 === this.nodeType && (b = g ? c.call(this, b, r(this).val()) : c, null == b ? b = "" : "number" === typeof b ? b += "" : r.isArray(b) && (b = r.map(b, function(c) {
                            return null == c ? "" : c + ""
                        })), a = r.valHooks[this.type] || r.valHooks[this.nodeName.toLowerCase()], a && "set" in a && a.set(this, b, "value") !== l || (this.value = b))
                    })
                }
                if (d) {
                    if ((a = r.valHooks[d.type] || r.valHooks[d.nodeName.toLowerCase()]) && "get" in a && (b = a.get(d, "value")) !==
                        l) return b;
                    b = d.value;
                    return "string" === typeof b ? b.replace(Sb, "") : null == b ? "" : b
                }
            }
        });
        r.extend({
            valHooks: {
                option: {
                    get: function(c) {
                        var a = r.find.attr(c, "value");
                        return null != a ? a : r.trim(r.text(c)).replace(Tb, " ")
                    }
                },
                select: {
                    get: function(c) {
                        for (var a, b = c.options, d = c.selectedIndex, g = (c = "select-one" === c.type || 0 > d) ? null : [], p = c ? d + 1 : b.length, h = 0 > d ? p : c ? d : 0; h < p; h++)
                            if (a = b[h], !(!a.selected && h !== d || (T.optDisabled ? a.disabled : null !== a.getAttribute("disabled")) || a.parentNode.disabled && r.nodeName(a.parentNode, "optgroup"))) {
                                a =
                                    r(a).val();
                                if (c) return a;
                                g.push(a)
                            } return g
                    },
                    set: function(c, a) {
                        for (var b, d = c.options, g = r.makeArray(a), p = d.length; p--;)
                            if (a = d[p], a.selected = -1 < r.inArray(r.valHooks.option.get(a), g)) b = !0;
                        b || (c.selectedIndex = -1);
                        return g
                    }
                }
            }
        });
        r.each(["radio", "checkbox"], function() {
            r.valHooks[this] = {
                set: function(c, a) {
                    if (r.isArray(a)) return c.checked = -1 < r.inArray(r(c).val(), a)
                }
            };
            T.checkOn || (r.valHooks[this].get = function(c) {
                return null === c.getAttribute("value") ? "on" : c.value
            })
        });
        var hb = /^(?:focusinfocus|focusoutblur)$/;
        r.extend(r.event, {
            trigger: function(c, a, b, d) {
                var g, p, h = [b || I],
                    e = ua.call(c, "type") ? c.type : c;
                var m = ua.call(c, "namespace") ? c.namespace.split(".") : [];
                var n = g = b = b || I;
                if (3 !== b.nodeType && 8 !== b.nodeType && !hb.test(e + r.event.triggered)) {
                    -1 < e.indexOf(".") && (m = e.split("."), e = m.shift(), m.sort());
                    var v = 0 > e.indexOf(":") && "on" + e;
                    c = c[r.expando] ? c : new r.Event(e, "object" === typeof c && c);
                    c.isTrigger = d ? 2 : 3;
                    c.namespace = m.join(".");
                    c.rnamespace = c.namespace ? new RegExp("(^|\\.)" + m.join("\\.(?:.*\\.|)") + "(\\.|$)") : null;
                    c.result =
                        l;
                    c.target || (c.target = b);
                    a = null == a ? [c] : r.makeArray(a, [c]);
                    m = r.event.special[e] || {};
                    if (d || !m.trigger || !1 !== m.trigger.apply(b, a)) {
                        if (!d && !m.noBubble && !r.isWindow(b)) {
                            var k = m.delegateType || e;
                            hb.test(k + e) || (n = n.parentNode);
                            for (; n; n = n.parentNode) h.push(n), g = n;
                            g === (b.ownerDocument || I) && h.push(g.defaultView || g.parentWindow || f)
                        }
                        for (g = 0;
                            (n = h[g++]) && !c.isPropagationStopped();) c.type = 1 < g ? k : m.bindType || e, (p = (M.get(n, "events") || {})[c.type] && M.get(n, "handle")) && p.apply(n, a), (p = v && n[v]) && p.apply && xa(n) && (c.result =
                            p.apply(n, a), !1 === c.result && c.preventDefault());
                        c.type = e;
                        d || c.isDefaultPrevented() || m._default && !1 !== m._default.apply(h.pop(), a) || !xa(b) || !v || !r.isFunction(b[e]) || r.isWindow(b) || ((g = b[v]) && (b[v] = null), r.event.triggered = e, b[e](), r.event.triggered = l, g && (b[v] = g));
                        return c.result
                    }
                }
            },
            simulate: function(c, a, b) {
                c = r.extend(new r.Event, b, {
                    type: c,
                    isSimulated: !0
                });
                r.event.trigger(c, null, a)
            }
        });
        r.fn.extend({
            trigger: function(c, a) {
                return this.each(function() {
                    r.event.trigger(c, a, this)
                })
            },
            triggerHandler: function(c,
                a) {
                var b = this[0];
                if (b) return r.event.trigger(c, a, b, !0)
            }
        });
        r.each("blur focus focusin focusout load resize scroll unload click dblclick mousedown mouseup mousemove mouseover mouseout mouseenter mouseleave change select submit keydown keypress keyup error contextmenu".split(" "), function(c, a) {
            r.fn[a] = function(c, b) {
                return 0 < arguments.length ? this.on(a, null, c, b) : this.trigger(a)
            }
        });
        r.fn.extend({
            hover: function(c, a) {
                return this.mouseenter(c).mouseleave(a || c)
            }
        });
        T.focusin = "onfocusin" in f;
        T.focusin || r.each({
            focus: "focusin",
            blur: "focusout"
        }, function(c, a) {
            var b = function(c) {
                r.event.simulate(a, c.target, r.event.fix(c))
            };
            r.event.special[a] = {
                setup: function() {
                    var d = this.ownerDocument || this,
                        g = M.access(d, a);
                    g || d.addEventListener(c, b, !0);
                    M.access(d, a, (g || 0) + 1)
                },
                teardown: function() {
                    var d = this.ownerDocument || this,
                        g = M.access(d, a) - 1;
                    g ? M.access(d, a, g) : (d.removeEventListener(c, b, !0), M.remove(d, a))
                }
            }
        });
        var Aa = f.location,
            Pa = r.now(),
            Qa = /\?/;
        r.parseJSON = function(c) {
            return JSON.parse(c + "")
        };
        r.parseXML = function(c) {
            if (!c || "string" !== typeof c) return null;
            try {
                var a = (new f.DOMParser).parseFromString(c, "text/xml")
            } catch (dc) {
                a = l
            }
            a && !a.getElementsByTagName("parsererror").length || r.error("Invalid XML: " + c);
            return a
        };
        var Ub = /#.*$/,
            ib = /([?&])_=[^&]*/,
            Vb = /^(.*?):[ \t]*([^\r\n]*)$/mg,
            Wb = /^(?:GET|HEAD)$/,
            Xb = /^\/\//,
            jb = {},
            Ka = {},
            kb = "*/".concat("*"),
            Ra = I.createElement("a");
        Ra.href = Aa.href;
        r.extend({
            active: 0,
            lastModified: {},
            etag: {},
            ajaxSettings: {
                url: Aa.href,
                type: "GET",
                isLocal: /^(?:about|app|app-storage|.+-extension|file|res|widget):$/.test(Aa.protocol),
                global: !0,
                processData: !0,
                async: !0,
                contentType: "application/x-www-form-urlencoded; charset\x3dUTF-8",
                accepts: {
                    "*": kb,
                    text: "text/plain",
                    html: "text/html",
                    xml: "application/xml, text/xml",
                    json: "application/json, text/javascript"
                },
                contents: {
                    xml: /\bxml\b/,
                    html: /\bhtml/,
                    json: /\bjson\b/
                },
                responseFields: {
                    xml: "responseXML",
                    text: "responseText",
                    json: "responseJSON"
                },
                converters: {
                    "* text": String,
                    "text html": !0,
                    "text json": r.parseJSON,
                    "text xml": r.parseXML
                },
                flatOptions: {
                    url: !0,
                    context: !0
                }
            },
            ajaxSetup: function(c, a) {
                return a ?
                    aa(aa(c, r.ajaxSettings), a) : aa(r.ajaxSettings, c)
            },
            ajaxPrefilter: ca(jb),
            ajaxTransport: ca(Ka),
            ajax: function(c, a) {
                function b(c, a, b, p) {
                    var m = a;
                    if (2 !== z) {
                        z = 2;
                        h && f.clearTimeout(h);
                        d = l;
                        g = p || "";
                        B.readyState = 0 < c ? 4 : 0;
                        p = 200 <= c && 300 > c || 304 === c;
                        if (b) {
                            var w = n;
                            for (var t = B, C, q, D, F, H = w.contents, L = w.dataTypes;
                                "*" === L[0];) L.shift(), C === l && (C = w.mimeType || t.getResponseHeader("Content-Type"));
                            if (C)
                                for (q in H)
                                    if (H[q] && H[q].test(C)) {
                                        L.unshift(q);
                                        break
                                    } if (L[0] in b) D = L[0];
                            else {
                                for (q in b) {
                                    if (!L[0] || w.converters[q + " " + L[0]]) {
                                        D =
                                            q;
                                        break
                                    }
                                    F || (F = q)
                                }
                                D = D || F
                            }
                            D ? (D !== L[0] && L.unshift(D), w = b[D]) : w = void 0
                        }
                        a: {
                            b = n;C = w;q = B;D = p;
                            var G;t = {};H = b.dataTypes.slice();
                            if (H[1])
                                for (E in b.converters) t[E.toLowerCase()] = b.converters[E];
                            for (F = H.shift(); F;) {
                                b.responseFields[F] && (q[b.responseFields[F]] = C);
                                !K && D && b.dataFilter && (C = b.dataFilter(C, b.dataType));
                                var K = F;
                                if (F = H.shift())
                                    if ("*" === F) F = K;
                                    else if ("*" !== K && K !== F) {
                                    var E = t[K + " " + F] || t["* " + F];
                                    if (!E)
                                        for (G in t)
                                            if (w = G.split(" "), w[1] === F && (E = t[K + " " + w[0]] || t["* " + w[0]])) {
                                                !0 === E ? E = t[G] : !0 !== t[G] && (F = w[0],
                                                    H.unshift(w[1]));
                                                break
                                            } if (!0 !== E)
                                        if (E && b.throws) C = E(C);
                                        else try {
                                            C = E(C)
                                        } catch (Cb) {
                                            w = {
                                                state: "parsererror",
                                                error: E ? Cb : "No conversion from " + K + " to " + F
                                            };
                                            break a
                                        }
                                }
                            }
                            w = {
                                state: "success",
                                data: C
                            }
                        }
                        if (p)
                            if (n.ifModified && ((m = B.getResponseHeader("Last-Modified")) && (r.lastModified[y] = m), (m = B.getResponseHeader("etag")) && (r.etag[y] = m)), 204 === c || "HEAD" === n.type) m = "nocontent";
                            else if (304 === c) m = "notmodified";
                        else {
                            m = w.state;
                            var N = w.data;
                            var P = w.error;
                            p = !P
                        } else if (P = m, c || !m) m = "error", 0 > c && (c = 0);
                        B.status = c;
                        B.statusText =
                            (a || m) + "";
                        p ? A.resolveWith(v, [N, m, B]) : A.rejectWith(v, [B, m, P]);
                        B.statusCode(u);
                        u = l;
                        e && k.trigger(p ? "ajaxSuccess" : "ajaxError", [B, n, p ? N : P]);
                        x.fireWith(v, [B, m]);
                        e && (k.trigger("ajaxComplete", [B, n]), --r.active || r.event.trigger("ajaxStop"))
                    }
                }
                "object" === typeof c && (a = c, c = l);
                a = a || {};
                var d, g, p, h, e, m, n = r.ajaxSetup({}, a),
                    v = n.context || n,
                    k = n.context && (v.nodeType || v.jquery) ? r(v) : r.event,
                    A = r.Deferred(),
                    x = r.Callbacks("once memory"),
                    u = n.statusCode || {},
                    w = {},
                    t = {},
                    z = 0,
                    C = "canceled",
                    B = {
                        readyState: 0,
                        getResponseHeader: function(c) {
                            var a;
                            if (2 === z) {
                                if (!p)
                                    for (p = {}; a = Vb.exec(g);) p[a[1].toLowerCase()] = a[2];
                                a = p[c.toLowerCase()]
                            }
                            return null == a ? null : a
                        },
                        getAllResponseHeaders: function() {
                            return 2 === z ? g : null
                        },
                        setRequestHeader: function(c, a) {
                            var b = c.toLowerCase();
                            z || (c = t[b] = t[b] || c, w[c] = a);
                            return this
                        },
                        overrideMimeType: function(c) {
                            z || (n.mimeType = c);
                            return this
                        },
                        statusCode: function(c) {
                            var a;
                            if (c)
                                if (2 > z)
                                    for (a in c) u[a] = [u[a], c[a]];
                                else B.always(c[B.status]);
                            return this
                        },
                        abort: function(c) {
                            c = c || C;
                            d && d.abort(c);
                            b(0, c);
                            return this
                        }
                    };
                A.promise(B).complete =
                    x.add;
                B.success = B.done;
                B.error = B.fail;
                n.url = ((c || n.url || Aa.href) + "").replace(Ub, "").replace(Xb, Aa.protocol + "//");
                n.type = a.method || a.type || n.method || n.type;
                n.dataTypes = r.trim(n.dataType || "*").toLowerCase().match(ka) || [""];
                if (null == n.crossDomain) {
                    c = I.createElement("a");
                    try {
                        c.href = n.url, c.href = c.href, n.crossDomain = Ra.protocol + "//" + Ra.host !== c.protocol + "//" + c.host
                    } catch (Ma) {
                        n.crossDomain = !0
                    }
                }
                n.data && n.processData && "string" !== typeof n.data && (n.data = r.param(n.data, n.traditional));
                ia(jb, n, a, B);
                if (2 === z) return B;
                (e = r.event && n.global) && 0 === r.active++ && r.event.trigger("ajaxStart");
                n.type = n.type.toUpperCase();
                n.hasContent = !Wb.test(n.type);
                var y = n.url;
                n.hasContent || (n.data && (y = n.url += (Qa.test(y) ? "\x26" : "?") + n.data, delete n.data), !1 === n.cache && (n.url = ib.test(y) ? y.replace(ib, "$1_\x3d" + Pa++) : y + (Qa.test(y) ? "\x26" : "?") + "_\x3d" + Pa++));
                n.ifModified && (r.lastModified[y] && B.setRequestHeader("If-Modified-Since", r.lastModified[y]), r.etag[y] && B.setRequestHeader("If-None-Match", r.etag[y]));
                (n.data && n.hasContent && !1 !== n.contentType ||
                    a.contentType) && B.setRequestHeader("Content-Type", n.contentType);
                B.setRequestHeader("Accept", n.dataTypes[0] && n.accepts[n.dataTypes[0]] ? n.accepts[n.dataTypes[0]] + ("*" !== n.dataTypes[0] ? ", " + kb + "; q\x3d0.01" : "") : n.accepts["*"]);
                for (m in n.headers) B.setRequestHeader(m, n.headers[m]);
                if (n.beforeSend && (!1 === n.beforeSend.call(v, B, n) || 2 === z)) return B.abort();
                C = "abort";
                for (m in {
                        success: 1,
                        error: 1,
                        complete: 1
                    }) B[m](n[m]);
                if (d = ia(Ka, n, a, B)) {
                    B.readyState = 1;
                    e && k.trigger("ajaxSend", [B, n]);
                    if (2 === z) return B;
                    n.async &&
                        0 < n.timeout && (h = f.setTimeout(function() {
                            B.abort("timeout")
                        }, n.timeout));
                    try {
                        z = 1, d.send(w, b)
                    } catch (Ma) {
                        if (2 > z) b(-1, Ma);
                        else throw Ma;
                    }
                } else b(-1, "No Transport");
                return B
            },
            getJSON: function(c, a, b) {
                return r.get(c, a, b, "json")
            },
            getScript: function(c, a) {
                return r.get(c, l, a, "script")
            }
        });
        r.each(["get", "post"], function(c, a) {
            r[a] = function(c, b, d, g) {
                r.isFunction(b) && (g = g || d, d = b, b = l);
                return r.ajax(r.extend({
                    url: c,
                    type: a,
                    dataType: g,
                    data: b,
                    success: d
                }, r.isPlainObject(c) && c))
            }
        });
        r._evalUrl = function(c) {
            return r.ajax({
                url: c,
                type: "GET",
                dataType: "script",
                async: !1,
                global: !1,
                "throws": !0
            })
        };
        r.fn.extend({
            wrapAll: function(c) {
                if (r.isFunction(c)) return this.each(function(a) {
                    r(this).wrapAll(c.call(this, a))
                });
                if (this[0]) {
                    var a = r(c, this[0].ownerDocument).eq(0).clone(!0);
                    this[0].parentNode && a.insertBefore(this[0]);
                    a.map(function() {
                        for (var c = this; c.firstElementChild;) c = c.firstElementChild;
                        return c
                    }).append(this)
                }
                return this
            },
            wrapInner: function(c) {
                return r.isFunction(c) ? this.each(function(a) {
                    r(this).wrapInner(c.call(this, a))
                }) : this.each(function() {
                    var a =
                        r(this),
                        b = a.contents();
                    b.length ? b.wrapAll(c) : a.append(c)
                })
            },
            wrap: function(c) {
                var a = r.isFunction(c);
                return this.each(function(b) {
                    r(this).wrapAll(a ? c.call(this, b) : c)
                })
            },
            unwrap: function() {
                return this.parent().each(function() {
                    r.nodeName(this, "body") || r(this).replaceWith(this.childNodes)
                }).end()
            }
        });
        r.expr.filters.hidden = function(c) {
            return !r.expr.filters.visible(c)
        };
        r.expr.filters.visible = function(c) {
            return 0 < c.offsetWidth || 0 < c.offsetHeight || 0 < c.getClientRects().length
        };
        var Yb = /%20/g,
            wb = /\[\]$/,
            lb = /\r?\n/g,
            Zb = /^(?:submit|button|image|reset|file)$/i,
            $b = /^(?:input|select|textarea|keygen)/i;
        r.param = function(c, a) {
            var b, d = [],
                g = function(c, a) {
                    a = r.isFunction(a) ? a() : null == a ? "" : a;
                    d[d.length] = encodeURIComponent(c) + "\x3d" + encodeURIComponent(a)
                };
            a === l && (a = r.ajaxSettings && r.ajaxSettings.traditional);
            if (r.isArray(c) || c.jquery && !r.isPlainObject(c)) r.each(c, function() {
                g(this.name, this.value)
            });
            else
                for (b in c) da(b, c[b], a, g);
            return d.join("\x26").replace(Yb, "+")
        };
        r.fn.extend({
            serialize: function() {
                return r.param(this.serializeArray())
            },
            serializeArray: function() {
                return this.map(function() {
                    var c = r.prop(this, "elements");
                    return c ? r.makeArray(c) : this
                }).filter(function() {
                    var c = this.type;
                    return this.name && !r(this).is(":disabled") && $b.test(this.nodeName) && !Zb.test(c) && (this.checked || !eb.test(c))
                }).map(function(c, a) {
                    c = r(this).val();
                    return null == c ? null : r.isArray(c) ? r.map(c, function(c) {
                        return {
                            name: a.name,
                            value: c.replace(lb, "\r\n")
                        }
                    }) : {
                        name: a.name,
                        value: c.replace(lb, "\r\n")
                    }
                }).get()
            }
        });
        r.ajaxSettings.xhr = function() {
            try {
                return new f.XMLHttpRequest
            } catch (G) {}
        };
        var ac = {
                0: 200,
                1223: 204
            },
            Ba = r.ajaxSettings.xhr();
        T.cors = !!Ba && "withCredentials" in Ba;
        T.ajax = Ba = !!Ba;
        r.ajaxTransport(function(c) {
            var a, b;
            if (T.cors || Ba && !c.crossDomain) return {
                send: function(d, g) {
                    var p, h = c.xhr();
                    h.open(c.type, c.url, c.async, c.username, c.password);
                    if (c.xhrFields)
                        for (p in c.xhrFields) h[p] = c.xhrFields[p];
                    c.mimeType && h.overrideMimeType && h.overrideMimeType(c.mimeType);
                    c.crossDomain || d["X-Requested-With"] || (d["X-Requested-With"] = "XMLHttpRequest");
                    for (p in d) h.setRequestHeader(p, d[p]);
                    a = function(c) {
                        return function() {
                            a &&
                                (a = b = h.onload = h.onerror = h.onabort = h.onreadystatechange = null, "abort" === c ? h.abort() : "error" === c ? "number" !== typeof h.status ? g(0, "error") : g(h.status, h.statusText) : g(ac[h.status] || h.status, h.statusText, "text" !== (h.responseType || "text") || "string" !== typeof h.responseText ? {
                                    binary: h.response
                                } : {
                                    text: h.responseText
                                }, h.getAllResponseHeaders()))
                        }
                    };
                    h.onload = a();
                    b = h.onerror = a("error");
                    h.onabort !== l ? h.onabort = b : h.onreadystatechange = function() {
                        4 === h.readyState && f.setTimeout(function() {
                            a && b()
                        })
                    };
                    a = a("abort");
                    try {
                        h.send(c.hasContent &&
                            c.data || null)
                    } catch (qb) {
                        if (a) throw qb;
                    }
                },
                abort: function() {
                    a && a()
                }
            }
        });
        r.ajaxSetup({
            accepts: {
                script: "text/javascript, application/javascript, application/ecmascript, application/x-ecmascript"
            },
            contents: {
                script: /\b(?:java|ecma)script\b/
            },
            converters: {
                "text script": function(c) {
                    r.globalEval(c);
                    return c
                }
            }
        });
        r.ajaxPrefilter("script", function(c) {
            c.cache === l && (c.cache = !1);
            c.crossDomain && (c.type = "GET")
        });
        r.ajaxTransport("script", function(c) {
            if (c.crossDomain) {
                var a, b;
                return {
                    send: function(d, g) {
                        a = r("\x3cscript\x3e").prop({
                            charset: c.scriptCharset,
                            src: c.url
                        }).on("load error", b = function(c) {
                            a.remove();
                            b = null;
                            c && g("error" === c.type ? 404 : 200, c.type)
                        });
                        I.head.appendChild(a[0])
                    },
                    abort: function() {
                        b && b()
                    }
                }
            }
        });
        var mb = [],
            Sa = /(=)\?(?=&|$)|\?\?/;
        r.ajaxSetup({
            jsonp: "callback",
            jsonpCallback: function() {
                var c = mb.pop() || r.expando + "_" + Pa++;
                this[c] = !0;
                return c
            }
        });
        r.ajaxPrefilter("json jsonp", function(c, a, b) {
            var d, g = !1 !== c.jsonp && (Sa.test(c.url) ? "url" : "string" === typeof c.data && 0 === (c.contentType || "").indexOf("application/x-www-form-urlencoded") && Sa.test(c.data) &&
                "data");
            if (g || "jsonp" === c.dataTypes[0]) {
                var p = c.jsonpCallback = r.isFunction(c.jsonpCallback) ? c.jsonpCallback() : c.jsonpCallback;
                g ? c[g] = c[g].replace(Sa, "$1" + p) : !1 !== c.jsonp && (c.url += (Qa.test(c.url) ? "\x26" : "?") + c.jsonp + "\x3d" + p);
                c.converters["script json"] = function() {
                    d || r.error(p + " was not called");
                    return d[0]
                };
                c.dataTypes[0] = "json";
                var h = f[p];
                f[p] = function() {
                    d = arguments
                };
                b.always(function() {
                    h === l ? r(f).removeProp(p) : f[p] = h;
                    c[p] && (c.jsonpCallback = a.jsonpCallback, mb.push(p));
                    d && r.isFunction(h) && h(d[0]);
                    d = h = l
                });
                return "script"
            }
        });
        r.parseHTML = function(c, a, b) {
            if (!c || "string" !== typeof c) return null;
            "boolean" === typeof a && (b = a, a = !1);
            a = a || I;
            var d = cb.exec(c);
            b = !b && [];
            if (d) return [a.createElement(d[1])];
            d = u([c], a, b);
            b && b.length && r(b).remove();
            return r.merge([], d.childNodes)
        };
        var nb = r.fn.load;
        r.fn.load = function(c, a, b) {
            if ("string" !== typeof c && nb) return nb.apply(this, arguments);
            var d, g, p = this,
                h = c.indexOf(" ");
            if (-1 < h) {
                var e = r.trim(c.slice(h));
                c = c.slice(0, h)
            }
            r.isFunction(a) ? (b = a, a = l) : a && "object" === typeof a && (d =
                "POST");
            0 < p.length && r.ajax({
                url: c,
                type: d || "GET",
                dataType: "html",
                data: a
            }).done(function(c) {
                g = arguments;
                p.html(e ? r("\x3cdiv\x3e").append(r.parseHTML(c)).find(e) : c)
            }).always(b && function(c, a) {
                p.each(function() {
                    b.apply(this, g || [c.responseText, a, c])
                })
            });
            return this
        };
        r.each("ajaxStart ajaxStop ajaxComplete ajaxError ajaxSuccess ajaxSend".split(" "), function(c, a) {
            r.fn[a] = function(c) {
                return this.on(a, c)
            }
        });
        r.expr.filters.animated = function(c) {
            return r.grep(r.timers, function(a) {
                return c === a.elem
            }).length
        };
        r.offset = {
            setOffset: function(c, a, b) {
                var d = r.css(c, "position"),
                    g = r(c),
                    p = {};
                "static" === d && (c.style.position = "relative");
                var h = g.offset();
                var e = r.css(c, "top");
                var m = r.css(c, "left");
                ("absolute" === d || "fixed" === d) && -1 < (e + m).indexOf("auto") ? (m = g.position(), e = m.top, m = m.left) : (e = parseFloat(e) || 0, m = parseFloat(m) || 0);
                r.isFunction(a) && (a = a.call(c, b, r.extend({}, h)));
                null != a.top && (p.top = a.top - h.top + e);
                null != a.left && (p.left = a.left - h.left + m);
                "using" in a ? a.using.call(c, p) : g.css(p)
            }
        };
        r.fn.extend({
            offset: function(c) {
                if (arguments.length) return c ===
                    l ? this : this.each(function(a) {
                        r.offset.setOffset(this, c, a)
                    });
                var a = this[0];
                var b = {
                        top: 0,
                        left: 0
                    },
                    d = a && a.ownerDocument;
                if (d) {
                    var g = d.documentElement;
                    if (!r.contains(g, a)) return b;
                    b = a.getBoundingClientRect();
                    a = na(d);
                    return {
                        top: b.top + a.pageYOffset - g.clientTop,
                        left: b.left + a.pageXOffset - g.clientLeft
                    }
                }
            },
            position: function() {
                if (this[0]) {
                    var c = this[0],
                        a = {
                            top: 0,
                            left: 0
                        };
                    if ("fixed" === r.css(c, "position")) var b = c.getBoundingClientRect();
                    else {
                        var d = this.offsetParent();
                        b = this.offset();
                        r.nodeName(d[0], "html") || (a = d.offset());
                        a.top += r.css(d[0], "borderTopWidth", !0);
                        a.left += r.css(d[0], "borderLeftWidth", !0)
                    }
                    return {
                        top: b.top - a.top - r.css(c, "marginTop", !0),
                        left: b.left - a.left - r.css(c, "marginLeft", !0)
                    }
                }
            },
            offsetParent: function() {
                return this.map(function() {
                    for (var c = this.offsetParent; c && "static" === r.css(c, "position");) c = c.offsetParent;
                    return c || ya
                })
            }
        });
        r.each({
            scrollLeft: "pageXOffset",
            scrollTop: "pageYOffset"
        }, function(c, a) {
            var b = "pageYOffset" === a;
            r.fn[c] = function(d) {
                return ja(this, function(c, d, g) {
                    var p = na(c);
                    if (g === l) return p ? p[a] :
                        c[d];
                    p ? p.scrollTo(b ? p.pageXOffset : g, b ? g : p.pageYOffset) : c[d] = g
                }, c, d, arguments.length)
            }
        });
        r.each(["top", "left"], function(c, a) {
            r.cssHooks[a] = N(T.pixelPosition, function(c, b) {
                if (b) return b = K(c, a), Ja.test(b) ? r(c).position()[a] + "px" : b
            })
        });
        r.each({
            Height: "height",
            Width: "width"
        }, function(c, a) {
            r.each({
                padding: "inner" + c,
                content: a,
                "": "outer" + c
            }, function(b, d) {
                r.fn[d] = function(d, g) {
                    var p = arguments.length && (b || "boolean" !== typeof d),
                        h = b || (!0 === d || !0 === g ? "margin" : "border");
                    return ja(this, function(a, b, d) {
                        return r.isWindow(a) ?
                            a.document.documentElement["client" + c] : 9 === a.nodeType ? (b = a.documentElement, Math.max(a.body["scroll" + c], b["scroll" + c], a.body["offset" + c], b["offset" + c], b["client" + c])) : d === l ? r.css(a, b, h) : r.style(a, b, d, h)
                    }, a, p ? d : l, p, null)
                }
            })
        });
        r.fn.extend({
            bind: function(c, a, b) {
                return this.on(c, null, a, b)
            },
            unbind: function(c, a) {
                return this.off(c, null, a)
            },
            delegate: function(c, a, b, d) {
                return this.on(a, c, b, d)
            },
            undelegate: function(c, a, b) {
                return 1 === arguments.length ? this.off(c, "**") : this.off(a, c || "**", b)
            },
            size: function() {
                return this.length
            }
        });
        r.fn.andSelf = r.fn.addBack;
        "function" === typeof define && define.amd && define("jquery", [], function() {
            return r
        });
        var bc = f.jQuery,
            cc = f.$;
        r.noConflict = function(c) {
            f.$ === r && (f.$ = cc);
            c && f.jQuery === r && (f.jQuery = bc);
            return r
        };
        e || (f.jQuery = f.$ = r);
        return r
    });
    q.jQuery = jQuery;
    jQuery.noConflict(!0)
})(window, ChemDoodle.lib);
(function(f) {
    "function" === typeof define && define.amd ? define(["jquery"], f) : "object" === typeof exports ? module.exports = f : f(ChemDoodle.lib.jQuery)
})(function(f) {
    function q(g) {
        var h = g || window.event,
            e = k.call(arguments, 1),
            m = 0,
            x = 0,
            u = 0,
            w = 0;
        g = f.event.fix(h);
        g.type = "mousewheel";
        "detail" in h && (x = -1 * h.detail);
        "wheelDelta" in h && (x = h.wheelDelta);
        "wheelDeltaY" in h && (x = h.wheelDeltaY);
        "wheelDeltaX" in h && (m = -1 * h.wheelDeltaX);
        "axis" in h && h.axis === h.HORIZONTAL_AXIS && (m = -1 * x, x = 0);
        var t = 0 === x ? m : x;
        "deltaY" in h && (t = x = -1 * h.deltaY);
        "deltaX" in h && (m = h.deltaX, 0 === x && (t = -1 * m));
        if (0 !== x || 0 !== m) {
            if (1 === h.deltaMode) {
                var y = f.data(this, "mousewheel-line-height");
                t *= y;
                x *= y;
                m *= y
            } else 2 === h.deltaMode && (y = f.data(this, "mousewheel-page-height"), t *= y, x *= y, m *= y);
            y = Math.max(Math.abs(x), Math.abs(m));
            if (!d || y < d) d = y, a.settings.adjustOldDeltas && "mousewheel" === h.type && 0 === y % 120 && (d /= 40);
            a.settings.adjustOldDeltas && "mousewheel" === h.type && 0 === y % 120 && (t /= 40, m /= 40, x /= 40);
            t = Math[1 <= t ? "floor" : "ceil"](t / d);
            m = Math[1 <= m ? "floor" : "ceil"](m / d);
            x = Math[1 <= x ? "floor" :
                "ceil"](x / d);
            a.settings.normalizeOffset && this.getBoundingClientRect && (h = this.getBoundingClientRect(), u = g.clientX - h.left, w = g.clientY - h.top);
            g.deltaX = m;
            g.deltaY = x;
            g.deltaFactor = d;
            g.offsetX = u;
            g.offsetY = w;
            g.deltaMode = 0;
            e.unshift(g, t, m, x);
            b && clearTimeout(b);
            b = setTimeout(l, 200);
            return (f.event.dispatch || f.event.handle).apply(this, e)
        }
    }

    function l() {
        d = null
    }
    var t = ["wheel", "mousewheel", "DOMMouseScroll", "MozMousePixelScroll"],
        e = "onwheel" in document || 9 <= document.documentMode ? ["wheel"] : ["mousewheel", "DomMouseScroll",
            "MozMousePixelScroll"
        ],
        k = Array.prototype.slice,
        b, d;
    if (f.event.fixHooks)
        for (var h = t.length; h;) f.event.fixHooks[t[--h]] = f.event.mouseHooks;
    var a = f.event.special.mousewheel = {
        version: "3.1.12",
        setup: function() {
            if (this.addEventListener)
                for (var b = e.length; b;) this.addEventListener(e[--b], q, !1);
            else this.onmousewheel = q;
            f.data(this, "mousewheel-line-height", a.getLineHeight(this));
            f.data(this, "mousewheel-page-height", a.getPageHeight(this))
        },
        teardown: function() {
            if (this.removeEventListener)
                for (var a = e.length; a;) this.removeEventListener(e[--a],
                    q, !1);
            else this.onmousewheel = null;
            f.removeData(this, "mousewheel-line-height");
            f.removeData(this, "mousewheel-page-height")
        },
        getLineHeight: function(a) {
            a = f(a);
            var b = a["offsetParent" in f.fn ? "offsetParent" : "parent"]();
            b.length || (b = f("body"));
            return parseInt(b.css("fontSize"), 10) || parseInt(a.css("fontSize"), 10) || 16
        },
        getPageHeight: function(a) {
            return f(a).height()
        },
        settings: {
            adjustOldDeltas: !0,
            normalizeOffset: !0
        }
    };
    f.fn.extend({
        mousewheel: function(a) {
            return a ? this.bind("mousewheel", a) : this.trigger("mousewheel")
        },
        unmousewheel: function(a) {
            return this.unbind("mousewheel", a)
        }
    })
});
(function(f, q) {
    "object" === typeof exports ? module.exports = q(global) : "function" === typeof define && define.amd ? define([], function() {
        return q(f)
    }) : q(f)
})(ChemDoodle.lib, function(f) {
    function q(c) {
        return e = c
    }

    function l() {
        return e = "undefined" !== typeof Float32Array ? Float32Array : Array
    }
    var t = {};
    (function() {
        if ("undefined" != typeof Float32Array) {
            var c = new Float32Array(1),
                a = new Int32Array(c.buffer);
            t.invsqrt = function(b) {
                c[0] = b;
                a[0] = 1597463007 - (a[0] >> 1);
                var d = c[0];
                return d * (1.5 - .5 * b * d * d)
            }
        } else t.invsqrt = function(c) {
            return 1 /
                Math.sqrt(c)
        }
    })();
    var e = null;
    l();
    var k = {
            create: function(c) {
                var a = new e(3);
                c ? (a[0] = c[0], a[1] = c[1], a[2] = c[2]) : a[0] = a[1] = a[2] = 0;
                return a
            },
            createFrom: function(c, a, b) {
                var d = new e(3);
                d[0] = c;
                d[1] = a;
                d[2] = b;
                return d
            },
            set: function(c, a) {
                a[0] = c[0];
                a[1] = c[1];
                a[2] = c[2];
                return a
            },
            equal: function(c, a) {
                return c === a || 1E-6 > Math.abs(c[0] - a[0]) && 1E-6 > Math.abs(c[1] - a[1]) && 1E-6 > Math.abs(c[2] - a[2])
            },
            add: function(c, a, b) {
                if (!b || c === b) return c[0] += a[0], c[1] += a[1], c[2] += a[2], c;
                b[0] = c[0] + a[0];
                b[1] = c[1] + a[1];
                b[2] = c[2] + a[2];
                return b
            },
            subtract: function(c, a, b) {
                if (!b || c === b) return c[0] -= a[0], c[1] -= a[1], c[2] -= a[2], c;
                b[0] = c[0] - a[0];
                b[1] = c[1] - a[1];
                b[2] = c[2] - a[2];
                return b
            },
            multiply: function(c, a, b) {
                if (!b || c === b) return c[0] *= a[0], c[1] *= a[1], c[2] *= a[2], c;
                b[0] = c[0] * a[0];
                b[1] = c[1] * a[1];
                b[2] = c[2] * a[2];
                return b
            },
            negate: function(c, a) {
                a || (a = c);
                a[0] = -c[0];
                a[1] = -c[1];
                a[2] = -c[2];
                return a
            },
            scale: function(c, a, b) {
                if (!b || c === b) return c[0] *= a, c[1] *= a, c[2] *= a, c;
                b[0] = c[0] * a;
                b[1] = c[1] * a;
                b[2] = c[2] * a;
                return b
            },
            normalize: function(c, a) {
                a || (a = c);
                var b = c[0],
                    d = c[1];
                c = c[2];
                var g = Math.sqrt(b * b + d * d + c * c);
                if (!g) return a[0] = 0, a[1] = 0, a[2] = 0, a;
                if (1 === g) return a[0] = b, a[1] = d, a[2] = c, a;
                g = 1 / g;
                a[0] = b * g;
                a[1] = d * g;
                a[2] = c * g;
                return a
            },
            cross: function(c, a, b) {
                b || (b = c);
                var d = c[0],
                    g = c[1];
                c = c[2];
                var p = a[0],
                    h = a[1];
                a = a[2];
                b[0] = g * a - c * h;
                b[1] = c * p - d * a;
                b[2] = d * h - g * p;
                return b
            },
            length: function(c) {
                var a = c[0],
                    b = c[1];
                c = c[2];
                return Math.sqrt(a * a + b * b + c * c)
            },
            squaredLength: function(c) {
                var a = c[0],
                    b = c[1];
                c = c[2];
                return a * a + b * b + c * c
            },
            dot: function(c, a) {
                return c[0] * a[0] + c[1] * a[1] + c[2] * a[2]
            },
            direction: function(c,
                a, b) {
                b || (b = c);
                var d = c[0] - a[0],
                    g = c[1] - a[1];
                c = c[2] - a[2];
                a = Math.sqrt(d * d + g * g + c * c);
                if (!a) return b[0] = 0, b[1] = 0, b[2] = 0, b;
                a = 1 / a;
                b[0] = d * a;
                b[1] = g * a;
                b[2] = c * a;
                return b
            },
            lerp: function(c, a, b, d) {
                d || (d = c);
                d[0] = c[0] + b * (a[0] - c[0]);
                d[1] = c[1] + b * (a[1] - c[1]);
                d[2] = c[2] + b * (a[2] - c[2]);
                return d
            },
            dist: function(c, a) {
                var b = a[0] - c[0],
                    d = a[1] - c[1];
                c = a[2] - c[2];
                return Math.sqrt(b * b + d * d + c * c)
            }
        },
        b = null,
        d = new e(4);
    k.unproject = function(c, a, g, h, e) {
        e || (e = c);
        b || (b = m.create());
        var p = b;
        d[0] = 2 * (c[0] - h[0]) / h[2] - 1;
        d[1] = 2 * (c[1] - h[1]) / h[3] - 1;
        d[2] =
            2 * c[2] - 1;
        d[3] = 1;
        m.multiply(g, a, p);
        if (!m.inverse(p)) return null;
        m.multiplyVec4(p, d);
        if (0 === d[3]) return null;
        e[0] = d[0] / d[3];
        e[1] = d[1] / d[3];
        e[2] = d[2] / d[3];
        return e
    };
    var h = k.createFrom(1, 0, 0),
        a = k.createFrom(0, 1, 0),
        g = k.createFrom(0, 0, 1),
        n = k.create();
    k.rotationTo = function(c, b, d) {
        d || (d = x.create());
        var p = k.dot(c, b);
        if (1 <= p) x.set(u, d);
        else if (-.999999 > p) k.cross(h, c, n), 1E-6 > k.length(n) && k.cross(a, c, n), 1E-6 > k.length(n) && k.cross(g, c, n), k.normalize(n), x.fromAngleAxis(Math.PI, n, d);
        else {
            p = Math.sqrt(2 * (1 + p));
            var e =
                1 / p;
            k.cross(c, b, n);
            d[0] = n[0] * e;
            d[1] = n[1] * e;
            d[2] = n[2] * e;
            d[3] = .5 * p;
            x.normalize(d)
        }
        1 < d[3] ? d[3] = 1 : -1 > d[3] && (d[3] = -1);
        return d
    };
    k.str = function(c) {
        return "[" + c[0] + ", " + c[1] + ", " + c[2] + "]"
    };
    var v = {
            create: function(c) {
                var a = new e(9);
                c ? (a[0] = c[0], a[1] = c[1], a[2] = c[2], a[3] = c[3], a[4] = c[4], a[5] = c[5], a[6] = c[6], a[7] = c[7], a[8] = c[8]) : a[0] = a[1] = a[2] = a[3] = a[4] = a[5] = a[6] = a[7] = a[8] = 0;
                return a
            },
            createFrom: function(c, a, b, d, g, h, m, n, v) {
                var p = new e(9);
                p[0] = c;
                p[1] = a;
                p[2] = b;
                p[3] = d;
                p[4] = g;
                p[5] = h;
                p[6] = m;
                p[7] = n;
                p[8] = v;
                return p
            },
            determinant: function(c) {
                var a =
                    c[3],
                    b = c[4],
                    d = c[5],
                    g = c[6],
                    h = c[7],
                    e = c[8];
                return c[0] * (e * b - d * h) + c[1] * (-e * a + d * g) + c[2] * (h * a - b * g)
            },
            inverse: function(c, a) {
                var b = c[0],
                    d = c[1],
                    g = c[2],
                    h = c[3],
                    p = c[4],
                    e = c[5],
                    m = c[6],
                    n = c[7];
                c = c[8];
                var k = c * p - e * n,
                    f = -c * h + e * m,
                    x = n * h - p * m,
                    u = b * k + d * f + g * x;
                if (!u) return null;
                u = 1 / u;
                a || (a = v.create());
                a[0] = k * u;
                a[1] = (-c * d + g * n) * u;
                a[2] = (e * d - g * p) * u;
                a[3] = f * u;
                a[4] = (c * b - g * m) * u;
                a[5] = (-e * b + g * h) * u;
                a[6] = x * u;
                a[7] = (-n * b + d * m) * u;
                a[8] = (p * b - d * h) * u;
                return a
            },
            multiply: function(c, a, b) {
                b || (b = c);
                var d = c[0],
                    g = c[1],
                    h = c[2],
                    p = c[3],
                    e = c[4],
                    m = c[5],
                    n = c[6],
                    v = c[7];
                c = c[8];
                var k = a[0],
                    f = a[1],
                    x = a[2],
                    u = a[3],
                    w = a[4],
                    A = a[5],
                    t = a[6],
                    l = a[7];
                a = a[8];
                b[0] = k * d + f * p + x * n;
                b[1] = k * g + f * e + x * v;
                b[2] = k * h + f * m + x * c;
                b[3] = u * d + w * p + A * n;
                b[4] = u * g + w * e + A * v;
                b[5] = u * h + w * m + A * c;
                b[6] = t * d + l * p + a * n;
                b[7] = t * g + l * e + a * v;
                b[8] = t * h + l * m + a * c;
                return b
            },
            multiplyVec2: function(c, a, b) {
                b || (b = a);
                var d = a[0];
                a = a[1];
                b[0] = d * c[0] + a * c[3] + c[6];
                b[1] = d * c[1] + a * c[4] + c[7];
                return b
            },
            multiplyVec3: function(c, a, b) {
                b || (b = a);
                var d = a[0],
                    g = a[1];
                a = a[2];
                b[0] = d * c[0] + g * c[3] + a * c[6];
                b[1] = d * c[1] + g * c[4] + a * c[7];
                b[2] = d * c[2] + g * c[5] + a * c[8];
                return b
            },
            set: function(c, a) {
                a[0] = c[0];
                a[1] = c[1];
                a[2] = c[2];
                a[3] = c[3];
                a[4] = c[4];
                a[5] = c[5];
                a[6] = c[6];
                a[7] = c[7];
                a[8] = c[8];
                return a
            },
            equal: function(c, a) {
                return c === a || 1E-6 > Math.abs(c[0] - a[0]) && 1E-6 > Math.abs(c[1] - a[1]) && 1E-6 > Math.abs(c[2] - a[2]) && 1E-6 > Math.abs(c[3] - a[3]) && 1E-6 > Math.abs(c[4] - a[4]) && 1E-6 > Math.abs(c[5] - a[5]) && 1E-6 > Math.abs(c[6] - a[6]) && 1E-6 > Math.abs(c[7] - a[7]) && 1E-6 > Math.abs(c[8] - a[8])
            },
            identity: function(c) {
                c || (c = v.create());
                c[0] = 1;
                c[1] = 0;
                c[2] = 0;
                c[3] = 0;
                c[4] = 1;
                c[5] = 0;
                c[6] = 0;
                c[7] = 0;
                c[8] = 1;
                return c
            },
            transpose: function(c,
                a) {
                if (!a || c === a) {
                    a = c[1];
                    var b = c[2],
                        d = c[5];
                    c[1] = c[3];
                    c[2] = c[6];
                    c[3] = a;
                    c[5] = c[7];
                    c[6] = b;
                    c[7] = d;
                    return c
                }
                a[0] = c[0];
                a[1] = c[3];
                a[2] = c[6];
                a[3] = c[1];
                a[4] = c[4];
                a[5] = c[7];
                a[6] = c[2];
                a[7] = c[5];
                a[8] = c[8];
                return a
            },
            toMat4: function(c, a) {
                a || (a = m.create());
                a[15] = 1;
                a[14] = 0;
                a[13] = 0;
                a[12] = 0;
                a[11] = 0;
                a[10] = c[8];
                a[9] = c[7];
                a[8] = c[6];
                a[7] = 0;
                a[6] = c[5];
                a[5] = c[4];
                a[4] = c[3];
                a[3] = 0;
                a[2] = c[2];
                a[1] = c[1];
                a[0] = c[0];
                return a
            },
            str: function(c) {
                return "[" + c[0] + ", " + c[1] + ", " + c[2] + ", " + c[3] + ", " + c[4] + ", " + c[5] + ", " + c[6] + ", " + c[7] + ", " +
                    c[8] + "]"
            }
        },
        m = {
            create: function(c) {
                var a = new e(16);
                c && (a[0] = c[0], a[1] = c[1], a[2] = c[2], a[3] = c[3], a[4] = c[4], a[5] = c[5], a[6] = c[6], a[7] = c[7], a[8] = c[8], a[9] = c[9], a[10] = c[10], a[11] = c[11], a[12] = c[12], a[13] = c[13], a[14] = c[14], a[15] = c[15]);
                return a
            },
            createFrom: function(c, a, b, d, g, h, m, n, v, k, f, x, u, w, t, l) {
                var p = new e(16);
                p[0] = c;
                p[1] = a;
                p[2] = b;
                p[3] = d;
                p[4] = g;
                p[5] = h;
                p[6] = m;
                p[7] = n;
                p[8] = v;
                p[9] = k;
                p[10] = f;
                p[11] = x;
                p[12] = u;
                p[13] = w;
                p[14] = t;
                p[15] = l;
                return p
            },
            set: function(c, a) {
                a[0] = c[0];
                a[1] = c[1];
                a[2] = c[2];
                a[3] = c[3];
                a[4] = c[4];
                a[5] = c[5];
                a[6] = c[6];
                a[7] = c[7];
                a[8] = c[8];
                a[9] = c[9];
                a[10] = c[10];
                a[11] = c[11];
                a[12] = c[12];
                a[13] = c[13];
                a[14] = c[14];
                a[15] = c[15];
                return a
            },
            equal: function(c, a) {
                return c === a || 1E-6 > Math.abs(c[0] - a[0]) && 1E-6 > Math.abs(c[1] - a[1]) && 1E-6 > Math.abs(c[2] - a[2]) && 1E-6 > Math.abs(c[3] - a[3]) && 1E-6 > Math.abs(c[4] - a[4]) && 1E-6 > Math.abs(c[5] - a[5]) && 1E-6 > Math.abs(c[6] - a[6]) && 1E-6 > Math.abs(c[7] - a[7]) && 1E-6 > Math.abs(c[8] - a[8]) && 1E-6 > Math.abs(c[9] - a[9]) && 1E-6 > Math.abs(c[10] - a[10]) && 1E-6 > Math.abs(c[11] - a[11]) && 1E-6 > Math.abs(c[12] -
                    a[12]) && 1E-6 > Math.abs(c[13] - a[13]) && 1E-6 > Math.abs(c[14] - a[14]) && 1E-6 > Math.abs(c[15] - a[15])
            },
            identity: function(c) {
                c || (c = m.create());
                c[0] = 1;
                c[1] = 0;
                c[2] = 0;
                c[3] = 0;
                c[4] = 0;
                c[5] = 1;
                c[6] = 0;
                c[7] = 0;
                c[8] = 0;
                c[9] = 0;
                c[10] = 1;
                c[11] = 0;
                c[12] = 0;
                c[13] = 0;
                c[14] = 0;
                c[15] = 1;
                return c
            },
            transpose: function(c, a) {
                if (!a || c === a) {
                    a = c[1];
                    var b = c[2],
                        d = c[3],
                        g = c[6],
                        h = c[7],
                        p = c[11];
                    c[1] = c[4];
                    c[2] = c[8];
                    c[3] = c[12];
                    c[4] = a;
                    c[6] = c[9];
                    c[7] = c[13];
                    c[8] = b;
                    c[9] = g;
                    c[11] = c[14];
                    c[12] = d;
                    c[13] = h;
                    c[14] = p;
                    return c
                }
                a[0] = c[0];
                a[1] = c[4];
                a[2] = c[8];
                a[3] = c[12];
                a[4] = c[1];
                a[5] = c[5];
                a[6] = c[9];
                a[7] = c[13];
                a[8] = c[2];
                a[9] = c[6];
                a[10] = c[10];
                a[11] = c[14];
                a[12] = c[3];
                a[13] = c[7];
                a[14] = c[11];
                a[15] = c[15];
                return a
            },
            determinant: function(c) {
                var a = c[0],
                    b = c[1],
                    d = c[2],
                    g = c[3],
                    h = c[4],
                    e = c[5],
                    m = c[6],
                    n = c[7],
                    v = c[8],
                    k = c[9],
                    f = c[10],
                    x = c[11],
                    u = c[12],
                    w = c[13],
                    t = c[14];
                c = c[15];
                return u * k * m * g - v * w * m * g - u * e * f * g + h * w * f * g + v * e * t * g - h * k * t * g - u * k * d * n + v * w * d * n + u * b * f * n - a * w * f * n - v * b * t * n + a * k * t * n + u * e * d * x - h * w * d * x - u * b * m * x + a * w * m * x + h * b * t * x - a * e * t * x - v * e * d * c + h * k * d * c + v * b * m * c - a * k * m * c - h * b * f * c + a * e * f * c
            },
            inverse: function(c,
                a) {
                a || (a = c);
                var b = c[0],
                    d = c[1],
                    g = c[2],
                    h = c[3],
                    p = c[4],
                    e = c[5],
                    m = c[6],
                    n = c[7],
                    v = c[8],
                    k = c[9],
                    f = c[10],
                    x = c[11],
                    u = c[12],
                    w = c[13],
                    t = c[14];
                c = c[15];
                var l = b * e - d * p,
                    z = b * m - g * p,
                    y = b * n - h * p,
                    q = d * m - g * e,
                    R = d * n - h * e,
                    U = g * n - h * m,
                    ca = v * w - k * u,
                    ia = v * t - f * u,
                    aa = v * c - x * u,
                    da = k * t - f * w,
                    na = k * c - x * w,
                    ea = f * c - x * t,
                    I = l * ea - z * na + y * da + q * aa - R * ia + U * ca;
                if (!I) return null;
                I = 1 / I;
                a[0] = (e * ea - m * na + n * da) * I;
                a[1] = (-d * ea + g * na - h * da) * I;
                a[2] = (w * U - t * R + c * q) * I;
                a[3] = (-k * U + f * R - x * q) * I;
                a[4] = (-p * ea + m * aa - n * ia) * I;
                a[5] = (b * ea - g * aa + h * ia) * I;
                a[6] = (-u * U + t * y - c * z) * I;
                a[7] = (v * U - f * y + x * z) *
                    I;
                a[8] = (p * na - e * aa + n * ca) * I;
                a[9] = (-b * na + d * aa - h * ca) * I;
                a[10] = (u * R - w * y + c * l) * I;
                a[11] = (-v * R + k * y - x * l) * I;
                a[12] = (-p * da + e * ia - m * ca) * I;
                a[13] = (b * da - d * ia + g * ca) * I;
                a[14] = (-u * q + w * z - t * l) * I;
                a[15] = (v * q - k * z + f * l) * I;
                return a
            },
            toRotationMat: function(c, a) {
                a || (a = m.create());
                a[0] = c[0];
                a[1] = c[1];
                a[2] = c[2];
                a[3] = c[3];
                a[4] = c[4];
                a[5] = c[5];
                a[6] = c[6];
                a[7] = c[7];
                a[8] = c[8];
                a[9] = c[9];
                a[10] = c[10];
                a[11] = c[11];
                a[12] = 0;
                a[13] = 0;
                a[14] = 0;
                a[15] = 1;
                return a
            },
            toMat3: function(c, a) {
                a || (a = v.create());
                a[0] = c[0];
                a[1] = c[1];
                a[2] = c[2];
                a[3] = c[4];
                a[4] = c[5];
                a[5] = c[6];
                a[6] = c[8];
                a[7] = c[9];
                a[8] = c[10];
                return a
            },
            toInverseMat3: function(c, a) {
                var b = c[0],
                    d = c[1],
                    g = c[2],
                    h = c[4],
                    e = c[5],
                    p = c[6],
                    m = c[8],
                    n = c[9];
                c = c[10];
                var k = c * e - p * n,
                    f = -c * h + p * m,
                    x = n * h - e * m,
                    u = b * k + d * f + g * x;
                if (!u) return null;
                u = 1 / u;
                a || (a = v.create());
                a[0] = k * u;
                a[1] = (-c * d + g * n) * u;
                a[2] = (p * d - g * e) * u;
                a[3] = f * u;
                a[4] = (c * b - g * m) * u;
                a[5] = (-p * b + g * h) * u;
                a[6] = x * u;
                a[7] = (-n * b + d * m) * u;
                a[8] = (e * b - d * h) * u;
                return a
            },
            multiply: function(c, a, b) {
                b || (b = c);
                var d = c[0],
                    g = c[1],
                    h = c[2],
                    e = c[3],
                    m = c[4],
                    p = c[5],
                    n = c[6],
                    v = c[7],
                    k = c[8],
                    f = c[9],
                    x = c[10],
                    u = c[11],
                    w = c[12],
                    t = c[13],
                    A = c[14];
                c = c[15];
                var l = a[0],
                    z = a[1],
                    y = a[2],
                    q = a[3];
                b[0] = l * d + z * m + y * k + q * w;
                b[1] = l * g + z * p + y * f + q * t;
                b[2] = l * h + z * n + y * x + q * A;
                b[3] = l * e + z * v + y * u + q * c;
                l = a[4];
                z = a[5];
                y = a[6];
                q = a[7];
                b[4] = l * d + z * m + y * k + q * w;
                b[5] = l * g + z * p + y * f + q * t;
                b[6] = l * h + z * n + y * x + q * A;
                b[7] = l * e + z * v + y * u + q * c;
                l = a[8];
                z = a[9];
                y = a[10];
                q = a[11];
                b[8] = l * d + z * m + y * k + q * w;
                b[9] = l * g + z * p + y * f + q * t;
                b[10] = l * h + z * n + y * x + q * A;
                b[11] = l * e + z * v + y * u + q * c;
                l = a[12];
                z = a[13];
                y = a[14];
                q = a[15];
                b[12] = l * d + z * m + y * k + q * w;
                b[13] = l * g + z * p + y * f + q * t;
                b[14] = l * h + z * n + y * x + q * A;
                b[15] = l * e + z * v + y * u + q * c;
                return b
            },
            multiplyVec3: function(c, a, b) {
                b || (b = a);
                var d = a[0],
                    g = a[1];
                a = a[2];
                b[0] = c[0] * d + c[4] * g + c[8] * a + c[12];
                b[1] = c[1] * d + c[5] * g + c[9] * a + c[13];
                b[2] = c[2] * d + c[6] * g + c[10] * a + c[14];
                return b
            },
            multiplyVec4: function(c, a, b) {
                b || (b = a);
                var d = a[0],
                    g = a[1],
                    h = a[2];
                a = a[3];
                b[0] = c[0] * d + c[4] * g + c[8] * h + c[12] * a;
                b[1] = c[1] * d + c[5] * g + c[9] * h + c[13] * a;
                b[2] = c[2] * d + c[6] * g + c[10] * h + c[14] * a;
                b[3] = c[3] * d + c[7] * g + c[11] * h + c[15] * a;
                return b
            },
            translate: function(c, a, b) {
                var d = a[0],
                    g = a[1];
                a = a[2];
                if (!b || c === b) return c[12] = c[0] * d + c[4] * g + c[8] * a + c[12], c[13] = c[1] *
                    d + c[5] * g + c[9] * a + c[13], c[14] = c[2] * d + c[6] * g + c[10] * a + c[14], c[15] = c[3] * d + c[7] * g + c[11] * a + c[15], c;
                var h = c[0];
                var e = c[1];
                var m = c[2];
                var p = c[3];
                var n = c[4];
                var v = c[5];
                var k = c[6];
                var f = c[7];
                var x = c[8];
                var u = c[9];
                var w = c[10];
                var t = c[11];
                b[0] = h;
                b[1] = e;
                b[2] = m;
                b[3] = p;
                b[4] = n;
                b[5] = v;
                b[6] = k;
                b[7] = f;
                b[8] = x;
                b[9] = u;
                b[10] = w;
                b[11] = t;
                b[12] = h * d + n * g + x * a + c[12];
                b[13] = e * d + v * g + u * a + c[13];
                b[14] = m * d + k * g + w * a + c[14];
                b[15] = p * d + f * g + t * a + c[15];
                return b
            },
            scale: function(c, a, b) {
                var d = a[0],
                    g = a[1];
                a = a[2];
                if (!b || c === b) return c[0] *= d, c[1] *= d,
                    c[2] *= d, c[3] *= d, c[4] *= g, c[5] *= g, c[6] *= g, c[7] *= g, c[8] *= a, c[9] *= a, c[10] *= a, c[11] *= a, c;
                b[0] = c[0] * d;
                b[1] = c[1] * d;
                b[2] = c[2] * d;
                b[3] = c[3] * d;
                b[4] = c[4] * g;
                b[5] = c[5] * g;
                b[6] = c[6] * g;
                b[7] = c[7] * g;
                b[8] = c[8] * a;
                b[9] = c[9] * a;
                b[10] = c[10] * a;
                b[11] = c[11] * a;
                b[12] = c[12];
                b[13] = c[13];
                b[14] = c[14];
                b[15] = c[15];
                return b
            },
            rotate: function(c, a, b, d) {
                var g = b[0],
                    h = b[1];
                b = b[2];
                var e = Math.sqrt(g * g + h * h + b * b);
                if (!e) return null;
                1 !== e && (e = 1 / e, g *= e, h *= e, b *= e);
                var m = Math.sin(a);
                var n = Math.cos(a);
                var p = 1 - n;
                a = c[0];
                e = c[1];
                var v = c[2];
                var k = c[3];
                var f =
                    c[4];
                var x = c[5];
                var u = c[6];
                var w = c[7];
                var t = c[8];
                var l = c[9];
                var A = c[10];
                var z = c[11];
                var y = g * g * p + n;
                var q = h * g * p + b * m;
                var B = b * g * p - h * m;
                var ca = g * h * p - b * m;
                var ia = h * h * p + n;
                var aa = b * h * p + g * m;
                var da = g * b * p + h * m;
                g = h * b * p - g * m;
                h = b * b * p + n;
                d ? c !== d && (d[12] = c[12], d[13] = c[13], d[14] = c[14], d[15] = c[15]) : d = c;
                d[0] = a * y + f * q + t * B;
                d[1] = e * y + x * q + l * B;
                d[2] = v * y + u * q + A * B;
                d[3] = k * y + w * q + z * B;
                d[4] = a * ca + f * ia + t * aa;
                d[5] = e * ca + x * ia + l * aa;
                d[6] = v * ca + u * ia + A * aa;
                d[7] = k * ca + w * ia + z * aa;
                d[8] = a * da + f * g + t * h;
                d[9] = e * da + x * g + l * h;
                d[10] = v * da + u * g + A * h;
                d[11] = k * da + w * g + z *
                    h;
                return d
            },
            rotateX: function(c, a, b) {
                var d = Math.sin(a);
                a = Math.cos(a);
                var g = c[4],
                    h = c[5],
                    e = c[6],
                    m = c[7],
                    n = c[8],
                    p = c[9],
                    v = c[10],
                    k = c[11];
                b ? c !== b && (b[0] = c[0], b[1] = c[1], b[2] = c[2], b[3] = c[3], b[12] = c[12], b[13] = c[13], b[14] = c[14], b[15] = c[15]) : b = c;
                b[4] = g * a + n * d;
                b[5] = h * a + p * d;
                b[6] = e * a + v * d;
                b[7] = m * a + k * d;
                b[8] = g * -d + n * a;
                b[9] = h * -d + p * a;
                b[10] = e * -d + v * a;
                b[11] = m * -d + k * a;
                return b
            },
            rotateY: function(c, a, b) {
                var d = Math.sin(a);
                a = Math.cos(a);
                var g = c[0],
                    h = c[1],
                    e = c[2],
                    m = c[3],
                    n = c[8],
                    p = c[9],
                    v = c[10],
                    k = c[11];
                b ? c !== b && (b[4] = c[4], b[5] = c[5],
                    b[6] = c[6], b[7] = c[7], b[12] = c[12], b[13] = c[13], b[14] = c[14], b[15] = c[15]) : b = c;
                b[0] = g * a + n * -d;
                b[1] = h * a + p * -d;
                b[2] = e * a + v * -d;
                b[3] = m * a + k * -d;
                b[8] = g * d + n * a;
                b[9] = h * d + p * a;
                b[10] = e * d + v * a;
                b[11] = m * d + k * a;
                return b
            },
            rotateZ: function(c, a, b) {
                var d = Math.sin(a);
                a = Math.cos(a);
                var g = c[0],
                    h = c[1],
                    e = c[2],
                    m = c[3],
                    n = c[4],
                    p = c[5],
                    v = c[6],
                    k = c[7];
                b ? c !== b && (b[8] = c[8], b[9] = c[9], b[10] = c[10], b[11] = c[11], b[12] = c[12], b[13] = c[13], b[14] = c[14], b[15] = c[15]) : b = c;
                b[0] = g * a + n * d;
                b[1] = h * a + p * d;
                b[2] = e * a + v * d;
                b[3] = m * a + k * d;
                b[4] = g * -d + n * a;
                b[5] = h * -d + p * a;
                b[6] =
                    e * -d + v * a;
                b[7] = m * -d + k * a;
                return b
            },
            frustum: function(c, a, b, d, g, h, e) {
                e || (e = m.create());
                var n = a - c,
                    p = d - b,
                    v = h - g;
                e[0] = 2 * g / n;
                e[1] = 0;
                e[2] = 0;
                e[3] = 0;
                e[4] = 0;
                e[5] = 2 * g / p;
                e[6] = 0;
                e[7] = 0;
                e[8] = (a + c) / n;
                e[9] = (d + b) / p;
                e[10] = -(h + g) / v;
                e[11] = -1;
                e[12] = 0;
                e[13] = 0;
                e[14] = -(h * g * 2) / v;
                e[15] = 0;
                return e
            },
            perspective: function(c, a, b, d, g) {
                c = b * Math.tan(c * Math.PI / 360);
                a *= c;
                return m.frustum(-a, a, -c, c, b, d, g)
            },
            ortho: function(c, a, b, d, g, h, e) {
                e || (e = m.create());
                var n = a - c,
                    p = d - b,
                    v = h - g;
                e[0] = 2 / n;
                e[1] = 0;
                e[2] = 0;
                e[3] = 0;
                e[4] = 0;
                e[5] = 2 / p;
                e[6] = 0;
                e[7] = 0;
                e[8] =
                    0;
                e[9] = 0;
                e[10] = -2 / v;
                e[11] = 0;
                e[12] = -(c + a) / n;
                e[13] = -(d + b) / p;
                e[14] = -(h + g) / v;
                e[15] = 1;
                return e
            },
            lookAt: function(c, a, b, d) {
                d || (d = m.create());
                var g = c[0],
                    h = c[1];
                c = c[2];
                var e = b[0];
                var n = b[1];
                var p = b[2];
                var v = a[0];
                b = a[1];
                var k = a[2];
                if (g === v && h === b && c === k) return m.identity(d);
                a = g - v;
                b = h - b;
                v = c - k;
                var f = 1 / Math.sqrt(a * a + b * b + v * v);
                a *= f;
                b *= f;
                v *= f;
                k = n * v - p * b;
                p = p * a - e * v;
                e = e * b - n * a;
                (f = Math.sqrt(k * k + p * p + e * e)) ? (f = 1 / f, k *= f, p *= f, e *= f) : e = p = k = 0;
                n = b * e - v * p;
                var x = v * k - a * e;
                var u = a * p - b * k;
                (f = Math.sqrt(n * n + x * x + u * u)) ? (f = 1 / f, n *= f, x *= f, u *=
                    f) : u = x = n = 0;
                d[0] = k;
                d[1] = n;
                d[2] = a;
                d[3] = 0;
                d[4] = p;
                d[5] = x;
                d[6] = b;
                d[7] = 0;
                d[8] = e;
                d[9] = u;
                d[10] = v;
                d[11] = 0;
                d[12] = -(k * g + p * h + e * c);
                d[13] = -(n * g + x * h + u * c);
                d[14] = -(a * g + b * h + v * c);
                d[15] = 1;
                return d
            },
            fromRotationTranslation: function(c, a, b) {
                b || (b = m.create());
                var d = c[0],
                    g = c[1],
                    h = c[2],
                    e = c[3],
                    n = d + d,
                    p = g + g,
                    v = h + h;
                c = d * n;
                var k = d * p;
                d *= v;
                var f = g * p;
                g *= v;
                h *= v;
                n *= e;
                p *= e;
                e *= v;
                b[0] = 1 - (f + h);
                b[1] = k + e;
                b[2] = d - p;
                b[3] = 0;
                b[4] = k - e;
                b[5] = 1 - (c + h);
                b[6] = g + n;
                b[7] = 0;
                b[8] = d + p;
                b[9] = g - n;
                b[10] = 1 - (c + f);
                b[11] = 0;
                b[12] = a[0];
                b[13] = a[1];
                b[14] = a[2];
                b[15] = 1;
                return b
            },
            str: function(c) {
                return "[" + c[0] + ", " + c[1] + ", " + c[2] + ", " + c[3] + ", " + c[4] + ", " + c[5] + ", " + c[6] + ", " + c[7] + ", " + c[8] + ", " + c[9] + ", " + c[10] + ", " + c[11] + ", " + c[12] + ", " + c[13] + ", " + c[14] + ", " + c[15] + "]"
            }
        },
        x = {
            create: function(c) {
                var a = new e(4);
                c ? (a[0] = c[0], a[1] = c[1], a[2] = c[2], a[3] = c[3]) : a[0] = a[1] = a[2] = a[3] = 0;
                return a
            },
            createFrom: function(c, a, b, d) {
                var g = new e(4);
                g[0] = c;
                g[1] = a;
                g[2] = b;
                g[3] = d;
                return g
            },
            set: function(c, a) {
                a[0] = c[0];
                a[1] = c[1];
                a[2] = c[2];
                a[3] = c[3];
                return a
            },
            equal: function(c, a) {
                return c === a || 1E-6 > Math.abs(c[0] -
                    a[0]) && 1E-6 > Math.abs(c[1] - a[1]) && 1E-6 > Math.abs(c[2] - a[2]) && 1E-6 > Math.abs(c[3] - a[3])
            },
            identity: function(c) {
                c || (c = x.create());
                c[0] = 0;
                c[1] = 0;
                c[2] = 0;
                c[3] = 1;
                return c
            }
        },
        u = x.identity();
    x.calculateW = function(c, a) {
        var b = c[0],
            d = c[1],
            g = c[2];
        if (!a || c === a) return c[3] = -Math.sqrt(Math.abs(1 - b * b - d * d - g * g)), c;
        a[0] = b;
        a[1] = d;
        a[2] = g;
        a[3] = -Math.sqrt(Math.abs(1 - b * b - d * d - g * g));
        return a
    };
    x.dot = function(c, a) {
        return c[0] * a[0] + c[1] * a[1] + c[2] * a[2] + c[3] * a[3]
    };
    x.inverse = function(c, a) {
        var b = c[0],
            d = c[1],
            g = c[2],
            h = c[3];
        b = (b = b * b + d * d +
            g * g + h * h) ? 1 / b : 0;
        if (!a || c === a) return c[0] *= -b, c[1] *= -b, c[2] *= -b, c[3] *= b, c;
        a[0] = -c[0] * b;
        a[1] = -c[1] * b;
        a[2] = -c[2] * b;
        a[3] = c[3] * b;
        return a
    };
    x.conjugate = function(c, a) {
        if (!a || c === a) return c[0] *= -1, c[1] *= -1, c[2] *= -1, c;
        a[0] = -c[0];
        a[1] = -c[1];
        a[2] = -c[2];
        a[3] = c[3];
        return a
    };
    x.length = function(c) {
        var a = c[0],
            b = c[1],
            d = c[2];
        c = c[3];
        return Math.sqrt(a * a + b * b + d * d + c * c)
    };
    x.normalize = function(c, a) {
        a || (a = c);
        var b = c[0],
            d = c[1],
            g = c[2];
        c = c[3];
        var h = Math.sqrt(b * b + d * d + g * g + c * c);
        if (0 === h) return a[0] = 0, a[1] = 0, a[2] = 0, a[3] = 0, a;
        h = 1 / h;
        a[0] = b * h;
        a[1] = d * h;
        a[2] = g * h;
        a[3] = c * h;
        return a
    };
    x.add = function(c, a, b) {
        if (!b || c === b) return c[0] += a[0], c[1] += a[1], c[2] += a[2], c[3] += a[3], c;
        b[0] = c[0] + a[0];
        b[1] = c[1] + a[1];
        b[2] = c[2] + a[2];
        b[3] = c[3] + a[3];
        return b
    };
    x.multiply = function(c, a, b) {
        b || (b = c);
        var d = c[0],
            g = c[1],
            h = c[2];
        c = c[3];
        var e = a[0],
            m = a[1],
            n = a[2];
        a = a[3];
        b[0] = d * a + c * e + g * n - h * m;
        b[1] = g * a + c * m + h * e - d * n;
        b[2] = h * a + c * n + d * m - g * e;
        b[3] = c * a - d * e - g * m - h * n;
        return b
    };
    x.multiplyVec3 = function(c, a, b) {
        b || (b = a);
        var d = a[0],
            g = a[1],
            h = a[2];
        a = c[0];
        var e = c[1],
            m = c[2];
        c = c[3];
        var n =
            c * d + e * h - m * g,
            p = c * g + m * d - a * h,
            v = c * h + a * g - e * d;
        d = -a * d - e * g - m * h;
        b[0] = n * c + d * -a + p * -m - v * -e;
        b[1] = p * c + d * -e + v * -a - n * -m;
        b[2] = v * c + d * -m + n * -e - p * -a;
        return b
    };
    x.scale = function(c, a, b) {
        if (!b || c === b) return c[0] *= a, c[1] *= a, c[2] *= a, c[3] *= a, c;
        b[0] = c[0] * a;
        b[1] = c[1] * a;
        b[2] = c[2] * a;
        b[3] = c[3] * a;
        return b
    };
    x.toMat3 = function(c, a) {
        a || (a = v.create());
        var b = c[0],
            d = c[1],
            g = c[2],
            h = c[3],
            e = b + b,
            m = d + d,
            n = g + g;
        c = b * e;
        var p = b * m;
        b *= n;
        var k = d * m;
        d *= n;
        g *= n;
        e *= h;
        m *= h;
        h *= n;
        a[0] = 1 - (k + g);
        a[1] = p + h;
        a[2] = b - m;
        a[3] = p - h;
        a[4] = 1 - (c + g);
        a[5] = d + e;
        a[6] = b + m;
        a[7] = d - e;
        a[8] =
            1 - (c + k);
        return a
    };
    x.toMat4 = function(c, a) {
        a || (a = m.create());
        var b = c[0],
            d = c[1],
            g = c[2],
            h = c[3],
            e = b + b,
            n = d + d,
            p = g + g;
        c = b * e;
        var v = b * n;
        b *= p;
        var k = d * n;
        d *= p;
        g *= p;
        e *= h;
        n *= h;
        h *= p;
        a[0] = 1 - (k + g);
        a[1] = v + h;
        a[2] = b - n;
        a[3] = 0;
        a[4] = v - h;
        a[5] = 1 - (c + g);
        a[6] = d + e;
        a[7] = 0;
        a[8] = b + n;
        a[9] = d - e;
        a[10] = 1 - (c + k);
        a[11] = 0;
        a[12] = 0;
        a[13] = 0;
        a[14] = 0;
        a[15] = 1;
        return a
    };
    x.slerp = function(a, b, d, g) {
        g || (g = a);
        var c = a[0] * b[0] + a[1] * b[1] + a[2] * b[2] + a[3] * b[3];
        if (1 <= Math.abs(c)) return g !== a && (g[0] = a[0], g[1] = a[1], g[2] = a[2], g[3] = a[3]), g;
        var h = Math.acos(c);
        var e =
            Math.sqrt(1 - c * c);
        if (.001 > Math.abs(e)) return g[0] = .5 * a[0] + .5 * b[0], g[1] = .5 * a[1] + .5 * b[1], g[2] = .5 * a[2] + .5 * b[2], g[3] = .5 * a[3] + .5 * b[3], g;
        c = Math.sin((1 - d) * h) / e;
        d = Math.sin(d * h) / e;
        g[0] = a[0] * c + b[0] * d;
        g[1] = a[1] * c + b[1] * d;
        g[2] = a[2] * c + b[2] * d;
        g[3] = a[3] * c + b[3] * d;
        return g
    };
    x.fromRotationMatrix = function(a, b) {
        b || (b = x.create());
        var c = a[0] + a[4] + a[8];
        if (0 < c) {
            var d = Math.sqrt(c + 1);
            b[3] = .5 * d;
            d = .5 / d;
            b[0] = (a[7] - a[5]) * d;
            b[1] = (a[2] - a[6]) * d;
            b[2] = (a[3] - a[1]) * d
        } else {
            d = x.fromRotationMatrix.s_iNext = x.fromRotationMatrix.s_iNext || [1,
                2, 0
            ];
            c = 0;
            a[4] > a[0] && (c = 1);
            a[8] > a[3 * c + c] && (c = 2);
            var g = d[c],
                h = d[g];
            d = Math.sqrt(a[3 * c + c] - a[3 * g + g] - a[3 * h + h] + 1);
            b[c] = .5 * d;
            d = .5 / d;
            b[3] = (a[3 * h + g] - a[3 * g + h]) * d;
            b[g] = (a[3 * g + c] + a[3 * c + g]) * d;
            b[h] = (a[3 * h + c] + a[3 * c + h]) * d
        }
        return b
    };
    v.toQuat4 = x.fromRotationMatrix;
    (function() {
        var a = v.create();
        x.fromAxes = function(c, b, d, g) {
            a[0] = b[0];
            a[3] = b[1];
            a[6] = b[2];
            a[1] = d[0];
            a[4] = d[1];
            a[7] = d[2];
            a[2] = c[0];
            a[5] = c[1];
            a[8] = c[2];
            return x.fromRotationMatrix(a, g)
        }
    })();
    x.identity = function(a) {
        a || (a = x.create());
        a[0] = 0;
        a[1] = 0;
        a[2] = 0;
        a[3] = 1;
        return a
    };
    x.fromAngleAxis = function(a, b, d) {
        d || (d = x.create());
        a *= .5;
        var c = Math.sin(a);
        d[3] = Math.cos(a);
        d[0] = c * b[0];
        d[1] = c * b[1];
        d[2] = c * b[2];
        return d
    };
    x.toAngleAxis = function(a, b) {
        b || (b = a);
        var c = a[0] * a[0] + a[1] * a[1] + a[2] * a[2];
        0 < c ? (b[3] = 2 * Math.acos(a[3]), c = t.invsqrt(c), b[0] = a[0] * c, b[1] = a[1] * c, b[2] = a[2] * c) : (b[3] = 0, b[0] = 1, b[1] = 0, b[2] = 0);
        return b
    };
    x.str = function(a) {
        return "[" + a[0] + ", " + a[1] + ", " + a[2] + ", " + a[3] + "]"
    };
    var w = {
            create: function(a) {
                var c = new e(2);
                a ? (c[0] = a[0], c[1] = a[1]) : (c[0] = 0, c[1] = 0);
                return c
            },
            createFrom: function(a,
                b) {
                var c = new e(2);
                c[0] = a;
                c[1] = b;
                return c
            },
            add: function(a, b, d) {
                d || (d = b);
                d[0] = a[0] + b[0];
                d[1] = a[1] + b[1];
                return d
            },
            subtract: function(a, b, d) {
                d || (d = b);
                d[0] = a[0] - b[0];
                d[1] = a[1] - b[1];
                return d
            },
            multiply: function(a, b, d) {
                d || (d = b);
                d[0] = a[0] * b[0];
                d[1] = a[1] * b[1];
                return d
            },
            divide: function(a, b, d) {
                d || (d = b);
                d[0] = a[0] / b[0];
                d[1] = a[1] / b[1];
                return d
            },
            scale: function(a, b, d) {
                d || (d = a);
                d[0] = a[0] * b;
                d[1] = a[1] * b;
                return d
            },
            dist: function(a, b) {
                var c = b[0] - a[0];
                a = b[1] - a[1];
                return Math.sqrt(c * c + a * a)
            },
            set: function(a, b) {
                b[0] = a[0];
                b[1] =
                    a[1];
                return b
            },
            equal: function(a, b) {
                return a === b || 1E-6 > Math.abs(a[0] - b[0]) && 1E-6 > Math.abs(a[1] - b[1])
            },
            negate: function(a, b) {
                b || (b = a);
                b[0] = -a[0];
                b[1] = -a[1];
                return b
            },
            normalize: function(a, b) {
                b || (b = a);
                var c = a[0] * a[0] + a[1] * a[1];
                0 < c ? (c = Math.sqrt(c), b[0] = a[0] / c, b[1] = a[1] / c) : b[0] = b[1] = 0;
                return b
            },
            cross: function(a, b, d) {
                a = a[0] * b[1] - a[1] * b[0];
                if (!d) return a;
                d[0] = d[1] = 0;
                d[2] = a;
                return d
            },
            length: function(a) {
                var c = a[0];
                a = a[1];
                return Math.sqrt(c * c + a * a)
            },
            squaredLength: function(a) {
                var c = a[0];
                a = a[1];
                return c * c + a * a
            },
            dot: function(a, b) {
                return a[0] * b[0] + a[1] * b[1]
            },
            direction: function(a, b, d) {
                d || (d = a);
                var c = a[0] - b[0];
                a = a[1] - b[1];
                b = c * c + a * a;
                if (!b) return d[0] = 0, d[1] = 0, d[2] = 0, d;
                b = 1 / Math.sqrt(b);
                d[0] = c * b;
                d[1] = a * b;
                return d
            },
            lerp: function(a, b, d, g) {
                g || (g = a);
                g[0] = a[0] + d * (b[0] - a[0]);
                g[1] = a[1] + d * (b[1] - a[1]);
                return g
            },
            str: function(a) {
                return "[" + a[0] + ", " + a[1] + "]"
            }
        },
        z = {
            create: function(a) {
                var c = new e(4);
                a ? (c[0] = a[0], c[1] = a[1], c[2] = a[2], c[3] = a[3]) : c[0] = c[1] = c[2] = c[3] = 0;
                return c
            },
            createFrom: function(a, b, d, g) {
                var c = new e(4);
                c[0] = a;
                c[1] = b;
                c[2] = d;
                c[3] = g;
                return c
            },
            set: function(a, b) {
                b[0] = a[0];
                b[1] = a[1];
                b[2] = a[2];
                b[3] = a[3];
                return b
            },
            equal: function(a, b) {
                return a === b || 1E-6 > Math.abs(a[0] - b[0]) && 1E-6 > Math.abs(a[1] - b[1]) && 1E-6 > Math.abs(a[2] - b[2]) && 1E-6 > Math.abs(a[3] - b[3])
            },
            identity: function(a) {
                a || (a = z.create());
                a[0] = 1;
                a[1] = 0;
                a[2] = 0;
                a[3] = 1;
                return a
            },
            transpose: function(a, b) {
                if (!b || a === b) return b = a[1], a[1] = a[2], a[2] = b, a;
                b[0] = a[0];
                b[1] = a[2];
                b[2] = a[1];
                b[3] = a[3];
                return b
            },
            determinant: function(a) {
                return a[0] * a[3] - a[2] * a[1]
            },
            inverse: function(a,
                b) {
                b || (b = a);
                var c = a[0],
                    d = a[1],
                    g = a[2];
                a = a[3];
                var h = c * a - g * d;
                if (!h) return null;
                h = 1 / h;
                b[0] = a * h;
                b[1] = -d * h;
                b[2] = -g * h;
                b[3] = c * h;
                return b
            },
            multiply: function(a, b, d) {
                d || (d = a);
                var c = a[0],
                    g = a[1],
                    h = a[2];
                a = a[3];
                d[0] = c * b[0] + g * b[2];
                d[1] = c * b[1] + g * b[3];
                d[2] = h * b[0] + a * b[2];
                d[3] = h * b[1] + a * b[3];
                return d
            },
            rotate: function(a, b, d) {
                d || (d = a);
                var c = a[0],
                    g = a[1],
                    h = a[2];
                a = a[3];
                var e = Math.sin(b);
                b = Math.cos(b);
                d[0] = c * b + g * e;
                d[1] = c * -e + g * b;
                d[2] = h * b + a * e;
                d[3] = h * -e + a * b;
                return d
            },
            multiplyVec2: function(a, b, d) {
                d || (d = b);
                var c = b[0];
                b = b[1];
                d[0] =
                    c * a[0] + b * a[1];
                d[1] = c * a[2] + b * a[3];
                return d
            },
            scale: function(a, b, d) {
                d || (d = a);
                var c = a[1],
                    g = a[2],
                    h = a[3],
                    e = b[0];
                b = b[1];
                d[0] = a[0] * e;
                d[1] = c * b;
                d[2] = g * e;
                d[3] = h * b;
                return d
            },
            str: function(a) {
                return "[" + a[0] + ", " + a[1] + ", " + a[2] + ", " + a[3] + "]"
            }
        },
        y = {
            create: function(a) {
                var c = new e(4);
                a ? (c[0] = a[0], c[1] = a[1], c[2] = a[2], c[3] = a[3]) : (c[0] = 0, c[1] = 0, c[2] = 0, c[3] = 0);
                return c
            },
            createFrom: function(a, b, d, g) {
                var c = new e(4);
                c[0] = a;
                c[1] = b;
                c[2] = d;
                c[3] = g;
                return c
            },
            add: function(a, b, d) {
                d || (d = b);
                d[0] = a[0] + b[0];
                d[1] = a[1] + b[1];
                d[2] = a[2] +
                    b[2];
                d[3] = a[3] + b[3];
                return d
            },
            subtract: function(a, b, d) {
                d || (d = b);
                d[0] = a[0] - b[0];
                d[1] = a[1] - b[1];
                d[2] = a[2] - b[2];
                d[3] = a[3] - b[3];
                return d
            },
            multiply: function(a, b, d) {
                d || (d = b);
                d[0] = a[0] * b[0];
                d[1] = a[1] * b[1];
                d[2] = a[2] * b[2];
                d[3] = a[3] * b[3];
                return d
            },
            divide: function(a, b, d) {
                d || (d = b);
                d[0] = a[0] / b[0];
                d[1] = a[1] / b[1];
                d[2] = a[2] / b[2];
                d[3] = a[3] / b[3];
                return d
            },
            scale: function(a, b, d) {
                d || (d = a);
                d[0] = a[0] * b;
                d[1] = a[1] * b;
                d[2] = a[2] * b;
                d[3] = a[3] * b;
                return d
            },
            set: function(a, b) {
                b[0] = a[0];
                b[1] = a[1];
                b[2] = a[2];
                b[3] = a[3];
                return b
            },
            equal: function(a,
                b) {
                return a === b || 1E-6 > Math.abs(a[0] - b[0]) && 1E-6 > Math.abs(a[1] - b[1]) && 1E-6 > Math.abs(a[2] - b[2]) && 1E-6 > Math.abs(a[3] - b[3])
            },
            negate: function(a, b) {
                b || (b = a);
                b[0] = -a[0];
                b[1] = -a[1];
                b[2] = -a[2];
                b[3] = -a[3];
                return b
            },
            length: function(a) {
                var c = a[0],
                    b = a[1],
                    d = a[2];
                a = a[3];
                return Math.sqrt(c * c + b * b + d * d + a * a)
            },
            squaredLength: function(a) {
                var c = a[0],
                    b = a[1],
                    d = a[2];
                a = a[3];
                return c * c + b * b + d * d + a * a
            },
            lerp: function(a, b, d, g) {
                g || (g = a);
                g[0] = a[0] + d * (b[0] - a[0]);
                g[1] = a[1] + d * (b[1] - a[1]);
                g[2] = a[2] + d * (b[2] - a[2]);
                g[3] = a[3] + d * (b[3] - a[3]);
                return g
            },
            str: function(a) {
                return "[" + a[0] + ", " + a[1] + ", " + a[2] + ", " + a[3] + "]"
            }
        };
    f && (f.glMatrixArrayType = e, f.MatrixArray = e, f.setMatrixArrayType = q, f.determineMatrixArrayType = l, f.glMath = t, f.vec2 = w, f.vec3 = k, f.vec4 = y, f.mat2 = z, f.mat3 = v, f.mat4 = m, f.quat4 = x);
    return {
        glMatrixArrayType: e,
        MatrixArray: e,
        setMatrixArrayType: q,
        determineMatrixArrayType: l,
        glMath: t,
        vec2: w,
        vec3: k,
        vec4: y,
        mat2: z,
        mat3: v,
        mat4: m,
        quat4: x
    }
});
(function(f) {
    function q(a) {
        return 0 == a ? 0 : 0 < a ? 1 : -1
    }
    var l = {
            subtract: function(a, b) {
                return {
                    x: a.x - b.x,
                    y: a.y - b.y
                }
            },
            dotProduct: function(a, b) {
                return a.x * b.x + a.y * b.y
            },
            square: function(a) {
                return Math.sqrt(a.x * a.x + a.y * a.y)
            },
            scale: function(a, b) {
                return {
                    x: a.x * b,
                    y: a.y * b
                }
            }
        },
        t = Math.pow(2, -65),
        e = function(a, d) {
            for (var g = [], h = d.length - 1, e = 2 * h - 1, m = [], c = [], n = [], v = [], f = [
                    [1, .6, .3, .1],
                    [.4, .6, .6, .4],
                    [.1, .3, .6, 1]
                ], x = 0; x <= h; x++) m[x] = l.subtract(d[x], a);
            for (x = 0; x <= h - 1; x++) c[x] = l.subtract(d[x + 1], d[x]), c[x] = l.scale(c[x], 3);
            for (x =
                0; x <= h - 1; x++)
                for (var t = 0; t <= h; t++) n[x] || (n[x] = []), n[x][t] = l.dotProduct(c[x], m[t]);
            for (x = 0; x <= e; x++) v[x] || (v[x] = []), v[x].y = 0, v[x].x = parseFloat(x) / e;
            e = h - 1;
            for (m = 0; m <= h + e; m++)
                for (c = Math.min(m, h), x = Math.max(0, m - e); x <= c; x++) t = m - x, v[x + t].y += n[t][x] * f[t][x];
            h = d.length - 1;
            v = k(v, 2 * h - 1, g, 0);
            e = l.subtract(a, d[0]);
            n = l.square(e);
            for (x = f = 0; x < v; x++) e = l.subtract(a, b(d, h, g[x], null, null)), e = l.square(e), e < n && (n = e, f = g[x]);
            e = l.subtract(a, d[h]);
            e = l.square(e);
            e < n && (n = e, f = 1);
            return {
                location: f,
                distance: n
            }
        },
        k = function(a, d, g,
            h) {
            var e = [],
                n = [],
                c = [],
                m = [],
                v = 0;
            var f = q(a[0].y);
            for (var x = 1; x <= d; x++) {
                var u = q(a[x].y);
                u != f && v++;
                f = u
            }
            switch (v) {
                case 0:
                    return 0;
                case 1:
                    if (64 <= h) return g[0] = (a[0].x + a[d].x) / 2, 1;
                    var w, l;
                    v = a[0].y - a[d].y;
                    u = a[d].x - a[0].x;
                    f = a[0].x * a[d].y - a[d].x * a[0].y;
                    x = w = 0;
                    for (l = 1; l < d; l++) {
                        var H = v * a[l].x + u * a[l].y + f;
                        H > w ? w = H : H < x && (x = H)
                    }
                    l = u;
                    w = 1 / (0 * l - 1 * v) * (f - w - 0 * l);
                    l = u;
                    v = 1 / (0 * l - 1 * v) * (f - x - 0 * l);
                    if (Math.max(w, v) - Math.min(w, v) < t) return c = a[d].x - a[0].x, m = a[d].y - a[0].y, g[0] = 1 / (0 * c - 1 * m) * (c * (a[0].y - 0) - m * (a[0].x - 0)), 1
            }
            b(a, d, .5, e, n);
            a =
                k(e, d, c, h + 1);
            d = k(n, d, m, h + 1);
            for (h = 0; h < a; h++) g[h] = c[h];
            for (h = 0; h < d; h++) g[h + a] = m[h];
            return a + d
        },
        b = function(a, b, d, g, h) {
            for (var e = [
                    []
                ], c = 0; c <= b; c++) e[0][c] = a[c];
            for (a = 1; a <= b; a++)
                for (c = 0; c <= b - a; c++) e[a] || (e[a] = []), e[a][c] || (e[a][c] = {}), e[a][c].x = (1 - d) * e[a - 1][c].x + d * e[a - 1][c + 1].x, e[a][c].y = (1 - d) * e[a - 1][c].y + d * e[a - 1][c + 1].y;
            if (null != g)
                for (c = 0; c <= b; c++) g[c] = e[c][0];
            if (null != h)
                for (c = 0; c <= b; c++) h[c] = e[b - c][c];
            return e[b][0]
        },
        d = {},
        h = function(a) {
            var b = d[a];
            if (!b) {
                b = [];
                var g = function(a) {
                        return function(c) {
                            return a
                        }
                    },
                    h = function() {
                        return function(a) {
                            return a
                        }
                    },
                    e = function() {
                        return function(a) {
                            return 1 - a
                        }
                    },
                    n = function(a) {
                        return function(c) {
                            for (var b = 1, d = 0; d < a.length; d++) b *= a[d](c);
                            return b
                        }
                    };
                b.push(new function() {
                    return function(c) {
                        return Math.pow(c, a)
                    }
                });
                for (var c = 1; c < a; c++) {
                    for (var m = [new g(a)], v = 0; v < a - c; v++) m.push(new h);
                    for (v = 0; v < c; v++) m.push(new e);
                    b.push(new n(m))
                }
                b.push(new function() {
                    return function(c) {
                        return Math.pow(1 - c, a)
                    }
                });
                d[a] = b
            }
            return b
        },
        a = function(a, b) {
            for (var d = h(a.length - 1), g = 0, e = 0, n = 0; n < a.length; n++) g +=
                a[n].x * d[n](b), e += a[n].y * d[n](b);
            return {
                x: g,
                y: e
            }
        },
        g = function(a, b) {
            return Math.sqrt(Math.pow(a.x - b.x, 2) + Math.pow(a.y - b.y, 2))
        },
        n = function(b, d, h) {
            for (var e = a(b, d), n = 0, m = 0 < h ? 1 : -1, c = null; n < Math.abs(h);) d += .005 * m, c = a(b, d), n += g(c, e), e = c;
            return {
                point: c,
                location: d
            }
        },
        v = function(b, d) {
            var g = a(b, d);
            d = a(b.slice(0, b.length - 1), d);
            b = d.y - g.y;
            g = d.x - g.x;
            return 0 == b ? Infinity : Math.atan(b / g)
        };
    ChemDoodle.lib.jsBezier = {
        distanceFromCurve: e,
        gradientAtPoint: v,
        gradientAtPointAlongCurveFrom: function(a, b, d) {
            b = n(a, b, d);
            1 < b.location &&
                (b.location = 1);
            0 > b.location && (b.location = 0);
            return v(a, b.location)
        },
        nearestPointOnCurve: function(a, d) {
            a = e(a, d);
            return {
                point: b(d, d.length - 1, a.location, null, null),
                location: a.location
            }
        },
        pointOnCurve: a,
        pointAlongCurveFrom: function(a, b, d) {
            return n(a, b, d).point
        },
        perpendicularToCurveAt: function(a, b, d, g) {
            b = n(a, b, null == g ? 0 : g);
            a = v(a, b.location);
            g = Math.atan(-1 / a);
            a = d / 2 * Math.sin(g);
            d = d / 2 * Math.cos(g);
            return [{
                x: b.point.x + d,
                y: b.point.y + a
            }, {
                x: b.point.x - d,
                y: b.point.y - a
            }]
        },
        locationAlongCurveFrom: function(a, b, d) {
            return n(a,
                b, d).location
        },
        getLength: function(b) {
            for (var d = a(b, 0), h = 0, e = 0, n; 1 > e;) e += .005, n = a(b, e), h += g(n, d), d = n;
            return h
        }
    }
})(ChemDoodle.lib);
ChemDoodle.lib.MarchingCubes = function() {
    var f = new Uint32Array([0, 265, 515, 778, 1030, 1295, 1541, 1804, 2060, 2309, 2575, 2822, 3082, 3331, 3593, 3840, 400, 153, 915, 666, 1430, 1183, 1941, 1692, 2460, 2197, 2975, 2710, 3482, 3219, 3993, 3728, 560, 825, 51, 314, 1590, 1855, 1077, 1340, 2620, 2869, 2111, 2358, 3642, 3891, 3129, 3376, 928, 681, 419, 170, 1958, 1711, 1445, 1196, 2988, 2725, 2479, 2214, 4010, 3747, 3497, 3232, 1120, 1385, 1635, 1898, 102, 367, 613, 876, 3180, 3429, 3695, 3942, 2154, 2403, 2665, 2912, 1520, 1273, 2035, 1786, 502, 255, 1013, 764, 3580, 3317, 4095, 3830, 2554,
            2291, 3065, 2800, 1616, 1881, 1107, 1370, 598, 863, 85, 348, 3676, 3925, 3167, 3414, 2650, 2899, 2137, 2384, 1984, 1737, 1475, 1226, 966, 719, 453, 204, 4044, 3781, 3535, 3270, 3018, 2755, 2505, 2240, 2240, 2505, 2755, 3018, 3270, 3535, 3781, 4044, 204, 453, 719, 966, 1226, 1475, 1737, 1984, 2384, 2137, 2899, 2650, 3414, 3167, 3925, 3676, 348, 85, 863, 598, 1370, 1107, 1881, 1616, 2800, 3065, 2291, 2554, 3830, 4095, 3317, 3580, 764, 1013, 255, 502, 1786, 2035, 1273, 1520, 2912, 2665, 2403, 2154, 3942, 3695, 3429, 3180, 876, 613, 367, 102, 1898, 1635, 1385, 1120, 3232, 3497, 3747, 4010, 2214, 2479, 2725,
            2988, 1196, 1445, 1711, 1958, 170, 419, 681, 928, 3376, 3129, 3891, 3642, 2358, 2111, 2869, 2620, 1340, 1077, 1855, 1590, 314, 51, 825, 560, 3728, 3993, 3219, 3482, 2710, 2975, 2197, 2460, 1692, 1941, 1183, 1430, 666, 915, 153, 400, 3840, 3593, 3331, 3082, 2822, 2575, 2309, 2060, 1804, 1541, 1295, 1030, 778, 515, 265, 0
        ]),
        q = [
            [],
            [0, 8, 3],
            [0, 1, 9],
            [1, 8, 3, 9, 8, 1],
            [1, 2, 10],
            [0, 8, 3, 1, 2, 10],
            [9, 2, 10, 0, 2, 9],
            [2, 8, 3, 2, 10, 8, 10, 9, 8],
            [3, 11, 2],
            [0, 11, 2, 8, 11, 0],
            [1, 9, 0, 2, 3, 11],
            [1, 11, 2, 1, 9, 11, 9, 8, 11],
            [3, 10, 1, 11, 10, 3],
            [0, 10, 1, 0, 8, 10, 8, 11, 10],
            [3, 9, 0, 3, 11, 9, 11, 10, 9],
            [9, 8, 10, 10,
                8, 11
            ],
            [4, 7, 8],
            [4, 3, 0, 7, 3, 4],
            [0, 1, 9, 8, 4, 7],
            [4, 1, 9, 4, 7, 1, 7, 3, 1],
            [1, 2, 10, 8, 4, 7],
            [3, 4, 7, 3, 0, 4, 1, 2, 10],
            [9, 2, 10, 9, 0, 2, 8, 4, 7],
            [2, 10, 9, 2, 9, 7, 2, 7, 3, 7, 9, 4],
            [8, 4, 7, 3, 11, 2],
            [11, 4, 7, 11, 2, 4, 2, 0, 4],
            [9, 0, 1, 8, 4, 7, 2, 3, 11],
            [4, 7, 11, 9, 4, 11, 9, 11, 2, 9, 2, 1],
            [3, 10, 1, 3, 11, 10, 7, 8, 4],
            [1, 11, 10, 1, 4, 11, 1, 0, 4, 7, 11, 4],
            [4, 7, 8, 9, 0, 11, 9, 11, 10, 11, 0, 3],
            [4, 7, 11, 4, 11, 9, 9, 11, 10],
            [9, 5, 4],
            [9, 5, 4, 0, 8, 3],
            [0, 5, 4, 1, 5, 0],
            [8, 5, 4, 8, 3, 5, 3, 1, 5],
            [1, 2, 10, 9, 5, 4],
            [3, 0, 8, 1, 2, 10, 4, 9, 5],
            [5, 2, 10, 5, 4, 2, 4, 0, 2],
            [2, 10, 5, 3, 2, 5, 3, 5, 4, 3, 4, 8],
            [9, 5, 4, 2, 3, 11],
            [0, 11,
                2, 0, 8, 11, 4, 9, 5
            ],
            [0, 5, 4, 0, 1, 5, 2, 3, 11],
            [2, 1, 5, 2, 5, 8, 2, 8, 11, 4, 8, 5],
            [10, 3, 11, 10, 1, 3, 9, 5, 4],
            [4, 9, 5, 0, 8, 1, 8, 10, 1, 8, 11, 10],
            [5, 4, 0, 5, 0, 11, 5, 11, 10, 11, 0, 3],
            [5, 4, 8, 5, 8, 10, 10, 8, 11],
            [9, 7, 8, 5, 7, 9],
            [9, 3, 0, 9, 5, 3, 5, 7, 3],
            [0, 7, 8, 0, 1, 7, 1, 5, 7],
            [1, 5, 3, 3, 5, 7],
            [9, 7, 8, 9, 5, 7, 10, 1, 2],
            [10, 1, 2, 9, 5, 0, 5, 3, 0, 5, 7, 3],
            [8, 0, 2, 8, 2, 5, 8, 5, 7, 10, 5, 2],
            [2, 10, 5, 2, 5, 3, 3, 5, 7],
            [7, 9, 5, 7, 8, 9, 3, 11, 2],
            [9, 5, 7, 9, 7, 2, 9, 2, 0, 2, 7, 11],
            [2, 3, 11, 0, 1, 8, 1, 7, 8, 1, 5, 7],
            [11, 2, 1, 11, 1, 7, 7, 1, 5],
            [9, 5, 8, 8, 5, 7, 10, 1, 3, 10, 3, 11],
            [5, 7, 0, 5, 0, 9, 7, 11, 0, 1, 0, 10, 11, 10, 0],
            [11, 10,
                0, 11, 0, 3, 10, 5, 0, 8, 0, 7, 5, 7, 0
            ],
            [11, 10, 5, 7, 11, 5],
            [10, 6, 5],
            [0, 8, 3, 5, 10, 6],
            [9, 0, 1, 5, 10, 6],
            [1, 8, 3, 1, 9, 8, 5, 10, 6],
            [1, 6, 5, 2, 6, 1],
            [1, 6, 5, 1, 2, 6, 3, 0, 8],
            [9, 6, 5, 9, 0, 6, 0, 2, 6],
            [5, 9, 8, 5, 8, 2, 5, 2, 6, 3, 2, 8],
            [2, 3, 11, 10, 6, 5],
            [11, 0, 8, 11, 2, 0, 10, 6, 5],
            [0, 1, 9, 2, 3, 11, 5, 10, 6],
            [5, 10, 6, 1, 9, 2, 9, 11, 2, 9, 8, 11],
            [6, 3, 11, 6, 5, 3, 5, 1, 3],
            [0, 8, 11, 0, 11, 5, 0, 5, 1, 5, 11, 6],
            [3, 11, 6, 0, 3, 6, 0, 6, 5, 0, 5, 9],
            [6, 5, 9, 6, 9, 11, 11, 9, 8],
            [5, 10, 6, 4, 7, 8],
            [4, 3, 0, 4, 7, 3, 6, 5, 10],
            [1, 9, 0, 5, 10, 6, 8, 4, 7],
            [10, 6, 5, 1, 9, 7, 1, 7, 3, 7, 9, 4],
            [6, 1, 2, 6, 5, 1, 4, 7, 8],
            [1, 2, 5, 5, 2, 6, 3, 0, 4, 3, 4,
                7
            ],
            [8, 4, 7, 9, 0, 5, 0, 6, 5, 0, 2, 6],
            [7, 3, 9, 7, 9, 4, 3, 2, 9, 5, 9, 6, 2, 6, 9],
            [3, 11, 2, 7, 8, 4, 10, 6, 5],
            [5, 10, 6, 4, 7, 2, 4, 2, 0, 2, 7, 11],
            [0, 1, 9, 4, 7, 8, 2, 3, 11, 5, 10, 6],
            [9, 2, 1, 9, 11, 2, 9, 4, 11, 7, 11, 4, 5, 10, 6],
            [8, 4, 7, 3, 11, 5, 3, 5, 1, 5, 11, 6],
            [5, 1, 11, 5, 11, 6, 1, 0, 11, 7, 11, 4, 0, 4, 11],
            [0, 5, 9, 0, 6, 5, 0, 3, 6, 11, 6, 3, 8, 4, 7],
            [6, 5, 9, 6, 9, 11, 4, 7, 9, 7, 11, 9],
            [10, 4, 9, 6, 4, 10],
            [4, 10, 6, 4, 9, 10, 0, 8, 3],
            [10, 0, 1, 10, 6, 0, 6, 4, 0],
            [8, 3, 1, 8, 1, 6, 8, 6, 4, 6, 1, 10],
            [1, 4, 9, 1, 2, 4, 2, 6, 4],
            [3, 0, 8, 1, 2, 9, 2, 4, 9, 2, 6, 4],
            [0, 2, 4, 4, 2, 6],
            [8, 3, 2, 8, 2, 4, 4, 2, 6],
            [10, 4, 9, 10, 6, 4, 11, 2, 3],
            [0, 8, 2, 2, 8,
                11, 4, 9, 10, 4, 10, 6
            ],
            [3, 11, 2, 0, 1, 6, 0, 6, 4, 6, 1, 10],
            [6, 4, 1, 6, 1, 10, 4, 8, 1, 2, 1, 11, 8, 11, 1],
            [9, 6, 4, 9, 3, 6, 9, 1, 3, 11, 6, 3],
            [8, 11, 1, 8, 1, 0, 11, 6, 1, 9, 1, 4, 6, 4, 1],
            [3, 11, 6, 3, 6, 0, 0, 6, 4],
            [6, 4, 8, 11, 6, 8],
            [7, 10, 6, 7, 8, 10, 8, 9, 10],
            [0, 7, 3, 0, 10, 7, 0, 9, 10, 6, 7, 10],
            [10, 6, 7, 1, 10, 7, 1, 7, 8, 1, 8, 0],
            [10, 6, 7, 10, 7, 1, 1, 7, 3],
            [1, 2, 6, 1, 6, 8, 1, 8, 9, 8, 6, 7],
            [2, 6, 9, 2, 9, 1, 6, 7, 9, 0, 9, 3, 7, 3, 9],
            [7, 8, 0, 7, 0, 6, 6, 0, 2],
            [7, 3, 2, 6, 7, 2],
            [2, 3, 11, 10, 6, 8, 10, 8, 9, 8, 6, 7],
            [2, 0, 7, 2, 7, 11, 0, 9, 7, 6, 7, 10, 9, 10, 7],
            [1, 8, 0, 1, 7, 8, 1, 10, 7, 6, 7, 10, 2, 3, 11],
            [11, 2, 1, 11, 1, 7, 10, 6, 1, 6, 7, 1],
            [8,
                9, 6, 8, 6, 7, 9, 1, 6, 11, 6, 3, 1, 3, 6
            ],
            [0, 9, 1, 11, 6, 7],
            [7, 8, 0, 7, 0, 6, 3, 11, 0, 11, 6, 0],
            [7, 11, 6],
            [7, 6, 11],
            [3, 0, 8, 11, 7, 6],
            [0, 1, 9, 11, 7, 6],
            [8, 1, 9, 8, 3, 1, 11, 7, 6],
            [10, 1, 2, 6, 11, 7],
            [1, 2, 10, 3, 0, 8, 6, 11, 7],
            [2, 9, 0, 2, 10, 9, 6, 11, 7],
            [6, 11, 7, 2, 10, 3, 10, 8, 3, 10, 9, 8],
            [7, 2, 3, 6, 2, 7],
            [7, 0, 8, 7, 6, 0, 6, 2, 0],
            [2, 7, 6, 2, 3, 7, 0, 1, 9],
            [1, 6, 2, 1, 8, 6, 1, 9, 8, 8, 7, 6],
            [10, 7, 6, 10, 1, 7, 1, 3, 7],
            [10, 7, 6, 1, 7, 10, 1, 8, 7, 1, 0, 8],
            [0, 3, 7, 0, 7, 10, 0, 10, 9, 6, 10, 7],
            [7, 6, 10, 7, 10, 8, 8, 10, 9],
            [6, 8, 4, 11, 8, 6],
            [3, 6, 11, 3, 0, 6, 0, 4, 6],
            [8, 6, 11, 8, 4, 6, 9, 0, 1],
            [9, 4, 6, 9, 6, 3, 9, 3, 1, 11, 3, 6],
            [6,
                8, 4, 6, 11, 8, 2, 10, 1
            ],
            [1, 2, 10, 3, 0, 11, 0, 6, 11, 0, 4, 6],
            [4, 11, 8, 4, 6, 11, 0, 2, 9, 2, 10, 9],
            [10, 9, 3, 10, 3, 2, 9, 4, 3, 11, 3, 6, 4, 6, 3],
            [8, 2, 3, 8, 4, 2, 4, 6, 2],
            [0, 4, 2, 4, 6, 2],
            [1, 9, 0, 2, 3, 4, 2, 4, 6, 4, 3, 8],
            [1, 9, 4, 1, 4, 2, 2, 4, 6],
            [8, 1, 3, 8, 6, 1, 8, 4, 6, 6, 10, 1],
            [10, 1, 0, 10, 0, 6, 6, 0, 4],
            [4, 6, 3, 4, 3, 8, 6, 10, 3, 0, 3, 9, 10, 9, 3],
            [10, 9, 4, 6, 10, 4],
            [4, 9, 5, 7, 6, 11],
            [0, 8, 3, 4, 9, 5, 11, 7, 6],
            [5, 0, 1, 5, 4, 0, 7, 6, 11],
            [11, 7, 6, 8, 3, 4, 3, 5, 4, 3, 1, 5],
            [9, 5, 4, 10, 1, 2, 7, 6, 11],
            [6, 11, 7, 1, 2, 10, 0, 8, 3, 4, 9, 5],
            [7, 6, 11, 5, 4, 10, 4, 2, 10, 4, 0, 2],
            [3, 4, 8, 3, 5, 4, 3, 2, 5, 10, 5, 2, 11, 7, 6],
            [7, 2, 3, 7, 6, 2,
                5, 4, 9
            ],
            [9, 5, 4, 0, 8, 6, 0, 6, 2, 6, 8, 7],
            [3, 6, 2, 3, 7, 6, 1, 5, 0, 5, 4, 0],
            [6, 2, 8, 6, 8, 7, 2, 1, 8, 4, 8, 5, 1, 5, 8],
            [9, 5, 4, 10, 1, 6, 1, 7, 6, 1, 3, 7],
            [1, 6, 10, 1, 7, 6, 1, 0, 7, 8, 7, 0, 9, 5, 4],
            [4, 0, 10, 4, 10, 5, 0, 3, 10, 6, 10, 7, 3, 7, 10],
            [7, 6, 10, 7, 10, 8, 5, 4, 10, 4, 8, 10],
            [6, 9, 5, 6, 11, 9, 11, 8, 9],
            [3, 6, 11, 0, 6, 3, 0, 5, 6, 0, 9, 5],
            [0, 11, 8, 0, 5, 11, 0, 1, 5, 5, 6, 11],
            [6, 11, 3, 6, 3, 5, 5, 3, 1],
            [1, 2, 10, 9, 5, 11, 9, 11, 8, 11, 5, 6],
            [0, 11, 3, 0, 6, 11, 0, 9, 6, 5, 6, 9, 1, 2, 10],
            [11, 8, 5, 11, 5, 6, 8, 0, 5, 10, 5, 2, 0, 2, 5],
            [6, 11, 3, 6, 3, 5, 2, 10, 3, 10, 5, 3],
            [5, 8, 9, 5, 2, 8, 5, 6, 2, 3, 8, 2],
            [9, 5, 6, 9, 6, 0, 0, 6, 2],
            [1, 5, 8, 1,
                8, 0, 5, 6, 8, 3, 8, 2, 6, 2, 8
            ],
            [1, 5, 6, 2, 1, 6],
            [1, 3, 6, 1, 6, 10, 3, 8, 6, 5, 6, 9, 8, 9, 6],
            [10, 1, 0, 10, 0, 6, 9, 5, 0, 5, 6, 0],
            [0, 3, 8, 5, 6, 10],
            [10, 5, 6],
            [11, 5, 10, 7, 5, 11],
            [11, 5, 10, 11, 7, 5, 8, 3, 0],
            [5, 11, 7, 5, 10, 11, 1, 9, 0],
            [10, 7, 5, 10, 11, 7, 9, 8, 1, 8, 3, 1],
            [11, 1, 2, 11, 7, 1, 7, 5, 1],
            [0, 8, 3, 1, 2, 7, 1, 7, 5, 7, 2, 11],
            [9, 7, 5, 9, 2, 7, 9, 0, 2, 2, 11, 7],
            [7, 5, 2, 7, 2, 11, 5, 9, 2, 3, 2, 8, 9, 8, 2],
            [2, 5, 10, 2, 3, 5, 3, 7, 5],
            [8, 2, 0, 8, 5, 2, 8, 7, 5, 10, 2, 5],
            [9, 0, 1, 5, 10, 3, 5, 3, 7, 3, 10, 2],
            [9, 8, 2, 9, 2, 1, 8, 7, 2, 10, 2, 5, 7, 5, 2],
            [1, 3, 5, 3, 7, 5],
            [0, 8, 7, 0, 7, 1, 1, 7, 5],
            [9, 0, 3, 9, 3, 5, 5, 3, 7],
            [9, 8, 7, 5, 9, 7],
            [5,
                8, 4, 5, 10, 8, 10, 11, 8
            ],
            [5, 0, 4, 5, 11, 0, 5, 10, 11, 11, 3, 0],
            [0, 1, 9, 8, 4, 10, 8, 10, 11, 10, 4, 5],
            [10, 11, 4, 10, 4, 5, 11, 3, 4, 9, 4, 1, 3, 1, 4],
            [2, 5, 1, 2, 8, 5, 2, 11, 8, 4, 5, 8],
            [0, 4, 11, 0, 11, 3, 4, 5, 11, 2, 11, 1, 5, 1, 11],
            [0, 2, 5, 0, 5, 9, 2, 11, 5, 4, 5, 8, 11, 8, 5],
            [9, 4, 5, 2, 11, 3],
            [2, 5, 10, 3, 5, 2, 3, 4, 5, 3, 8, 4],
            [5, 10, 2, 5, 2, 4, 4, 2, 0],
            [3, 10, 2, 3, 5, 10, 3, 8, 5, 4, 5, 8, 0, 1, 9],
            [5, 10, 2, 5, 2, 4, 1, 9, 2, 9, 4, 2],
            [8, 4, 5, 8, 5, 3, 3, 5, 1],
            [0, 4, 5, 1, 0, 5],
            [8, 4, 5, 8, 5, 3, 9, 0, 5, 0, 3, 5],
            [9, 4, 5],
            [4, 11, 7, 4, 9, 11, 9, 10, 11],
            [0, 8, 3, 4, 9, 7, 9, 11, 7, 9, 10, 11],
            [1, 10, 11, 1, 11, 4, 1, 4, 0, 7, 4, 11],
            [3, 1, 4, 3, 4, 8,
                1, 10, 4, 7, 4, 11, 10, 11, 4
            ],
            [4, 11, 7, 9, 11, 4, 9, 2, 11, 9, 1, 2],
            [9, 7, 4, 9, 11, 7, 9, 1, 11, 2, 11, 1, 0, 8, 3],
            [11, 7, 4, 11, 4, 2, 2, 4, 0],
            [11, 7, 4, 11, 4, 2, 8, 3, 4, 3, 2, 4],
            [2, 9, 10, 2, 7, 9, 2, 3, 7, 7, 4, 9],
            [9, 10, 7, 9, 7, 4, 10, 2, 7, 8, 7, 0, 2, 0, 7],
            [3, 7, 10, 3, 10, 2, 7, 4, 10, 1, 10, 0, 4, 0, 10],
            [1, 10, 2, 8, 7, 4],
            [4, 9, 1, 4, 1, 7, 7, 1, 3],
            [4, 9, 1, 4, 1, 7, 0, 8, 1, 8, 7, 1],
            [4, 0, 3, 7, 4, 3],
            [4, 8, 7],
            [9, 10, 8, 10, 11, 8],
            [3, 0, 9, 3, 9, 11, 11, 9, 10],
            [0, 1, 10, 0, 10, 8, 8, 10, 11],
            [3, 1, 10, 11, 3, 10],
            [1, 2, 11, 1, 11, 9, 9, 11, 8],
            [3, 0, 9, 3, 9, 11, 1, 2, 9, 2, 11, 9],
            [0, 2, 11, 8, 0, 11],
            [3, 2, 11],
            [2, 3, 8, 2, 8, 10, 10, 8, 9],
            [9, 10,
                2, 0, 9, 2
            ],
            [2, 3, 8, 2, 8, 10, 0, 1, 8, 1, 10, 8],
            [1, 10, 2],
            [1, 3, 8, 9, 1, 8],
            [0, 9, 1],
            [0, 3, 8],
            []
        ],
        l = [
            [0, 0, 0],
            [1, 0, 0],
            [1, 1, 0],
            [0, 1, 0],
            [0, 0, 1],
            [1, 0, 1],
            [1, 1, 1],
            [0, 1, 1]
        ],
        t = [
            [0, 1],
            [1, 2],
            [2, 3],
            [3, 0],
            [4, 5],
            [5, 6],
            [6, 7],
            [7, 4],
            [0, 4],
            [1, 5],
            [2, 6],
            [3, 7]
        ];
    return function(e, k) {
        var b = [],
            d = [],
            h = 0,
            a = new Float32Array(8),
            g = new Int32Array(12),
            n = new Int32Array(3);
        for (n[2] = 0; n[2] < k[2] - 1; ++n[2], h += k[0])
            for (n[1] = 0; n[1] < k[1] - 1; ++n[1], ++h)
                for (n[0] = 0; n[0] < k[0] - 1; ++n[0], ++h) {
                    for (var v = 0, m = 0; 8 > m; ++m) {
                        var x = l[m];
                        x = e[h + x[0] + k[0] * (x[1] + k[1] * x[2])];
                        a[m] = x;
                        v |= 0 < x ? 1 << m : 0
                    }
                    x = f[v];
                    if (0 !== x) {
                        for (m = 0; 12 > m; ++m)
                            if (0 !== (x & 1 << m)) {
                                g[m] = b.length;
                                var u = [0, 0, 0],
                                    w = t[m],
                                    z = l[w[0]],
                                    y = l[w[1]],
                                    c = a[w[0]],
                                    p = c - a[w[1]];
                                w = 0;
                                1E-6 < Math.abs(p) && (w = c / p);
                                for (c = 0; 3 > c; ++c) u[c] = n[c] + z[c] + w * (y[c] - z[c]);
                                b.push(u)
                            } v = q[v];
                        for (m = 0; m < v.length; m += 3) d.push([g[v[m]], g[v[m + 1]], g[v[m + 2]]])
                    }
                }
        return {
            vertices: b,
            faces: d
        }
    }
}();
ChemDoodle.animations = function(f, q) {
    q = {};
    f.requestAnimFrame = function() {
        return f.requestAnimationFrame || f.webkitRequestAnimationFrame || f.mozRequestAnimationFrame || f.oRequestAnimationFrame || f.msRequestAnimationFrame || function(l, t) {
            f.setTimeout(l, 1E3 / 60)
        }
    }();
    q.requestInterval = function(l, t) {
        function e() {
            (new Date).getTime() - k >= t && (l.call(), k = (new Date).getTime());
            b.value = f.requestAnimFrame(e)
        }
        if (!(f.requestAnimationFrame || f.webkitRequestAnimationFrame || f.mozRequestAnimationFrame && f.mozCancelRequestAnimationFrame ||
                f.oRequestAnimationFrame || f.msRequestAnimationFrame)) return f.setInterval(l, t);
        let k = (new Date).getTime(),
            b = {};
        b.value = f.requestAnimFrame(e);
        return b
    };
    q.clearRequestInterval = function(l) {
        f.cancelAnimationFrame ? f.cancelAnimationFrame(l.value) : f.webkitCancelAnimationFrame ? f.webkitCancelAnimationFrame(l.value) : f.webkitCancelRequestAnimationFrame ? f.webkitCancelRequestAnimationFrame(l.value) : f.mozCancelRequestAnimationFrame ? f.mozCancelRequestAnimationFrame(l.value) : f.oCancelRequestAnimationFrame ? f.oCancelRequestAnimationFrame(l.value) :
            f.msCancelRequestAnimationFrame ? f.msCancelRequestAnimationFrame(l.value) : clearInterval(l)
    };
    q.requestTimeout = function(l, t) {
        function e() {
            (new Date).getTime() - k >= t ? l.call() : b.value = f.requestAnimFrame(e)
        }
        if (!(f.requestAnimationFrame || f.webkitRequestAnimationFrame || f.mozRequestAnimationFrame && f.mozCancelRequestAnimationFrame || f.oRequestAnimationFrame || f.msRequestAnimationFrame)) return f.setTimeout(l, t);
        let k = (new Date).getTime(),
            b = {};
        b.value = f.requestAnimFrame(e);
        return b
    };
    q.clearRequestTimeout = function(l) {
        f.cancelAnimationFrame ?
            f.cancelAnimationFrame(l.value) : f.webkitCancelAnimationFrame ? f.webkitCancelAnimationFrame(l.value) : f.webkitCancelRequestAnimationFrame ? f.webkitCancelRequestAnimationFrame(l.value) : f.mozCancelRequestAnimationFrame ? f.mozCancelRequestAnimationFrame(l.value) : f.oCancelRequestAnimationFrame ? f.oCancelRequestAnimationFrame(l.value) : f.msCancelRequestAnimationFrame ? f.msCancelRequestAnimationFrame(l.value) : clearTimeout(l)
    };
    return q
}(window);
ChemDoodle.extensions = function(f, q, l, t) {
    return {
        vec3AngleFrom: function(e, f) {
            let b = q.length(e),
                d = q.length(f);
            e = q.dot(e, f);
            return l.acos(e / b / d)
        },
        contextRoundRect: function(e, f, b, d, h, a) {
            e.beginPath();
            e.moveTo(f + a, b);
            e.lineTo(f + d - a, b);
            e.quadraticCurveTo(f + d, b, f + d, b + a);
            e.lineTo(f + d, b + h - a);
            e.quadraticCurveTo(f + d, b + h, f + d - a, b + h);
            e.lineTo(f + a, b + h);
            e.quadraticCurveTo(f, b + h, f, b + h - a);
            e.lineTo(f, b + a);
            e.quadraticCurveTo(f, b, f + a, b);
            e.closePath()
        },
        contextEllipse: function(e, f, b, d, h) {
            let a = d / 2 * .5522848,
                g = h / 2 * .5522848,
                n = f + d,
                v = b + h;
            d = f + d / 2;
            h = b + h / 2;
            e.beginPath();
            e.moveTo(f, h);
            e.bezierCurveTo(f, h - g, d - a, b, d, b);
            e.bezierCurveTo(d + a, b, n, h - g, n, h);
            e.bezierCurveTo(n, h + g, d + a, v, d, v);
            e.bezierCurveTo(d - a, v, f, h + g, f, h);
            e.closePath()
        },
        getFontString: function(e, f, b, d) {
            let h = [];
            b && h.push("bold ");
            d && h.push("italic ");
            h.push(e + "px ");
            for (let a = 0, b = f.length; a < b; a++) e = f[a], -1 !== e.indexOf(" ") && (e = '"' + e + '"'), h.push((0 !== a ? "," : "") + e);
            return h.join("")
        }
    }
}(ChemDoodle.structures, ChemDoodle.lib.vec3, Math);
(function(f, q, l) {
    q.sign || (q.sign = function(f) {
        return (0 < f) - (0 > f) || +f
    });
    "function" != typeof f.assign && (f.assign = function(t, e) {
        if (null == t) throw new TypeError("Cannot convert undefined or null to object");
        for (var k = f(t), b = 1; b < arguments.length; b++) {
            var d = arguments[b];
            if (null != d)
                for (var h in d) f.prototype.hasOwnProperty.call(d, h) && (k[h] = d[h])
        }
        return k
    });
    String.prototype.startsWith || (String.prototype.startsWith = function(f, e) {
        return this.substr(e || 0, f.length) === f
    })
})(Object, Math);
ChemDoodle.math = function(f, q, l, t, e) {
    let k = {},
        b = {
            aliceblue: "#f0f8ff",
            antiquewhite: "#faebd7",
            aqua: "#00ffff",
            aquamarine: "#7fffd4",
            azure: "#f0ffff",
            beige: "#f5f5dc",
            bisque: "#ffe4c4",
            black: "#000000",
            blanchedalmond: "#ffebcd",
            blue: "#0000ff",
            blueviolet: "#8a2be2",
            brown: "#a52a2a",
            burlywood: "#deb887",
            cadetblue: "#5f9ea0",
            chartreuse: "#7fff00",
            chocolate: "#d2691e",
            coral: "#ff7f50",
            cornflowerblue: "#6495ed",
            cornsilk: "#fff8dc",
            crimson: "#dc143c",
            cyan: "#00ffff",
            darkblue: "#00008b",
            darkcyan: "#008b8b",
            darkgoldenrod: "#b8860b",
            darkgray: "#a9a9a9",
            darkgreen: "#006400",
            darkkhaki: "#bdb76b",
            darkmagenta: "#8b008b",
            darkolivegreen: "#556b2f",
            darkorange: "#ff8c00",
            darkorchid: "#9932cc",
            darkred: "#8b0000",
            darksalmon: "#e9967a",
            darkseagreen: "#8fbc8f",
            darkslateblue: "#483d8b",
            darkslategray: "#2f4f4f",
            darkturquoise: "#00ced1",
            darkviolet: "#9400d3",
            deeppink: "#ff1493",
            deepskyblue: "#00bfff",
            dimgray: "#696969",
            dodgerblue: "#1e90ff",
            firebrick: "#b22222",
            floralwhite: "#fffaf0",
            forestgreen: "#228b22",
            fuchsia: "#ff00ff",
            gainsboro: "#dcdcdc",
            ghostwhite: "#f8f8ff",
            gold: "#ffd700",
            goldenrod: "#daa520",
            gray: "#808080",
            green: "#008000",
            greenyellow: "#adff2f",
            honeydew: "#f0fff0",
            hotpink: "#ff69b4",
            "indianred ": "#cd5c5c",
            "indigo ": "#4b0082",
            ivory: "#fffff0",
            khaki: "#f0e68c",
            lavender: "#e6e6fa",
            lavenderblush: "#fff0f5",
            lawngreen: "#7cfc00",
            lemonchiffon: "#fffacd",
            lightblue: "#add8e6",
            lightcoral: "#f08080",
            lightcyan: "#e0ffff",
            lightgoldenrodyellow: "#fafad2",
            lightgrey: "#d3d3d3",
            lightgreen: "#90ee90",
            lightpink: "#ffb6c1",
            lightsalmon: "#ffa07a",
            lightseagreen: "#20b2aa",
            lightskyblue: "#87cefa",
            lightslategray: "#778899",
            lightsteelblue: "#b0c4de",
            lightyellow: "#ffffe0",
            lime: "#00ff00",
            limegreen: "#32cd32",
            linen: "#faf0e6",
            magenta: "#ff00ff",
            maroon: "#800000",
            mediumaquamarine: "#66cdaa",
            mediumblue: "#0000cd",
            mediumorchid: "#ba55d3",
            mediumpurple: "#9370d8",
            mediumseagreen: "#3cb371",
            mediumslateblue: "#7b68ee",
            mediumspringgreen: "#00fa9a",
            mediumturquoise: "#48d1cc",
            mediumvioletred: "#c71585",
            midnightblue: "#191970",
            mintcream: "#f5fffa",
            mistyrose: "#ffe4e1",
            moccasin: "#ffe4b5",
            navajowhite: "#ffdead",
            navy: "#000080",
            oldlace: "#fdf5e6",
            olive: "#808000",
            olivedrab: "#6b8e23",
            orange: "#ffa500",
            orangered: "#ff4500",
            orchid: "#da70d6",
            palegoldenrod: "#eee8aa",
            palegreen: "#98fb98",
            paleturquoise: "#afeeee",
            palevioletred: "#d87093",
            papayawhip: "#ffefd5",
            peachpuff: "#ffdab9",
            peru: "#cd853f",
            pink: "#ffc0cb",
            plum: "#dda0dd",
            powderblue: "#b0e0e6",
            purple: "#800080",
            red: "#ff0000",
            rosybrown: "#bc8f8f",
            royalblue: "#4169e1",
            saddlebrown: "#8b4513",
            salmon: "#fa8072",
            sandybrown: "#f4a460",
            seagreen: "#2e8b57",
            seashell: "#fff5ee",
            sienna: "#a0522d",
            silver: "#c0c0c0",
            skyblue: "#87ceeb",
            slateblue: "#6a5acd",
            slategray: "#708090",
            snow: "#fffafa",
            springgreen: "#00ff7f",
            steelblue: "#4682b4",
            tan: "#d2b48c",
            teal: "#008080",
            thistle: "#d8bfd8",
            tomato: "#ff6347",
            turquoise: "#40e0d0",
            violet: "#ee82ee",
            wheat: "#f5deb3",
            white: "#ffffff",
            whitesmoke: "#f5f5f5",
            yellow: "#ffff00",
            yellowgreen: "#9acd32"
        };
    k.angleBetweenLargest = function(b) {
        if (0 === b.length) return {
            angle: 0,
            largest: 2 * t.PI
        };
        if (1 === b.length) return {
            angle: b[0] + t.PI,
            largest: 2 * t.PI
        };
        let d = 0,
            a = 0;
        for (let h = 0, e = b.length - 1; h < e; h++) {
            var g = b[h +
                1] - b[h];
            g > d && (d = g, a = (b[h + 1] + b[h]) / 2)
        }
        g = b[0] + 2 * t.PI - b[b.length - 1];
        g > d && (a = b[0] - g / 2, d = g, 0 > a && (a += 2 * t.PI));
        return {
            angle: a,
            largest: d
        }
    };
    k.isBetween = function(b, h, a) {
        if (h > a) {
            let b = h;
            h = a;
            a = b
        }
        return b >= h && b <= a
    };
    l(document).ready(function() {
        f && f.iChemLabs && f.iChemLabs.checkForUpdates && f.iChemLabs.checkForUpdates({})
    });
    k.getRGB = function(d, h) {
        let a = [0, 0, 0];
        b[d.toLowerCase()] && (d = b[d.toLowerCase()]);
        return "#" === d.charAt(0) ? (4 === d.length && (d = "#" + d.charAt(1) + d.charAt(1) + d.charAt(2) + d.charAt(2) + d.charAt(3) + d.charAt(3)),
            [parseInt(d.substring(1, 3), 16) / 255 * h, parseInt(d.substring(3, 5), 16) / 255 * h, parseInt(d.substring(5, 7), 16) / 255 * h]) : d.startsWith("rgba") ? (d = d.replace(/rgba\(|\)/g, "").split(","), 4 !== d.length ? a : [parseInt(d[0]) / 255 * h, parseInt(d[1]) / 255 * h, parseInt(d[2]) / 255 * h, parseInt(d[3]) / 255 * h]) : d.startsWith("rgb") ? (d = d.replace(/rgb\(|\)/g, "").split(","), 3 !== d.length ? a : [parseInt(d[0]) / 255 * h, parseInt(d[1]) / 255 * h, parseInt(d[2]) / 255 * h]) : a
    };
    k.hsl2rgb = function(b, h, a) {
        let d = function(a, b, d) {
            0 > d ? d += 1 : 1 < d && --d;
            return d < 1 / 6 ? a + 6 *
                (b - a) * d : .5 > d ? b : d < 2 / 3 ? a + (b - a) * (2 / 3 - d) * 6 : a
        };
        if (0 === h) a = h = b = a;
        else {
            let g = .5 > a ? a * (1 + h) : a + h - a * h,
                e = 2 * a - g;
            a = d(e, g, b + 1 / 3);
            h = d(e, g, b);
            b = d(e, g, b - 1 / 3)
        }
        return [255 * a, 255 * h, 255 * b]
    };
    k.idx2color = function(b) {
        b = b.toString(16);
        for (let d = 0, a = 6 - b.length; d < a; d++) b = "0" + b;
        return "#" + b
    };
    k.distanceFromPointToLineInclusive = function(b, h, a, g) {
        let d = h.distance(a);
        a = h.angle(a);
        a = t.PI / 2 - a;
        a = h.angle(b) + a;
        b = h.distance(b);
        b = new q.Point(b * t.cos(a), -b * t.sin(a));
        g = g ? g : 0;
        return k.isBetween(-b.y, g, d - g) ? t.abs(b.x) : -1
    };
    k.calculateDistanceInterior =
        function(b, h, a) {
            if (this.isBetween(h.x, a.x, a.x + a.w) && this.isBetween(h.y, a.y, a.y + a.h)) return b.distance(h);
            var d = [];
            d.push({
                x1: a.x,
                y1: a.y,
                x2: a.x + a.w,
                y2: a.y
            });
            d.push({
                x1: a.x,
                y1: a.y + a.h,
                x2: a.x + a.w,
                y2: a.y + a.h
            });
            d.push({
                x1: a.x,
                y1: a.y,
                x2: a.x,
                y2: a.y + a.h
            });
            d.push({
                x1: a.x + a.w,
                y1: a.y,
                x2: a.x + a.w,
                y2: a.y + a.h
            });
            a = [];
            for (var e = 0; 4 > e; e++) {
                var v = d[e];
                (v = this.intersectLines(h.x, h.y, b.x, b.y, v.x1, v.y1, v.x2, v.y2)) && a.push(v)
            }
            if (0 === a.length) return 0;
            h = 0;
            for (let g = 0, n = a.length; g < n; g++) e = a[g], d = b.x - e.x, e = b.y - e.y, h = t.max(h,
                t.sqrt(d * d + e * e));
            return h
        };
    k.intersectLines = function(b, h, a, g, e, v, m, f) {
        a -= b;
        g -= h;
        m -= e;
        f -= v;
        let d = g * m - a * f;
        if (0 === d) return !1;
        m = (f * (b - e) - m * (h - v)) / d;
        e = (g * (b - e) - a * (h - v)) / d;
        return 0 <= e && 1 >= e && 0 <= m && 1 >= m ? {
            x: b + m * a,
            y: h + m * g
        } : !1
    };
    k.clamp = function(b, h, a) {
        return b < h ? h : b > a ? a : b
    };
    k.rainbowAt = function(b, h, a) {
        1 > a.length ? a.push("#000000", "#FFFFFF") : 2 > a.length && a.push("#FFFFFF");
        var d = h / (a.length - 1);
        h = t.floor(b / d);
        b = (b - h * d) / d;
        d = k.getRGB(a[h], 1);
        a = k.getRGB(a[h + 1], 1);
        return "rgb(" + [255 * (d[0] + (a[0] - d[0]) * b), 255 * (d[1] + (a[1] -
            d[1]) * b), 255 * (d[2] + (a[2] - d[2]) * b)].join() + ")"
    };
    k.angleBounds = function(b, h, a) {
        let d = 2 * t.PI;
        for (; 0 > b;) b += d;
        for (; b > d;) b -= d;
        a && b > t.PI && (b = 2 * t.PI - b);
        h && (b = 180 * b / t.PI);
        return b
    };
    k.isPointInPoly = function(b, h) {
        for (var a = !1, d = -1, e = b.length, f = e - 1; ++d < e; f = d)(b[d].y <= h.y && h.y < b[f].y || b[f].y <= h.y && h.y < b[d].y) && h.x < (b[f].x - b[d].x) * (h.y - b[d].y) / (b[f].y - b[d].y) + b[d].x && (a = !a);
        return a
    };
    return k
}(ChemDoodle, ChemDoodle.structures, ChemDoodle.lib.jQuery, Math);
(function(f, q, l) {
    f.Bounds = function() {};
    let t = f.Bounds.prototype;
    t.minX = t.minY = t.minZ = Infinity;
    t.maxX = t.maxY = t.maxZ = -Infinity;
    t.expand = function(e, k, b, d) {
        e instanceof f.Bounds ? (this.minX = q.min(this.minX, e.minX), this.minY = q.min(this.minY, e.minY), this.maxX = q.max(this.maxX, e.maxX), this.maxY = q.max(this.maxY, e.maxY), Infinity !== e.maxZ && (this.minZ = q.min(this.minZ, e.minZ), this.maxZ = q.max(this.maxZ, e.maxZ))) : (this.minX = q.min(this.minX, e), this.maxX = q.max(this.maxX, e), this.minY = q.min(this.minY, k), this.maxY = q.max(this.maxY,
            k), b !== l && d !== l && (this.minX = q.min(this.minX, b), this.maxX = q.max(this.maxX, b), this.minY = q.min(this.minY, d), this.maxY = q.max(this.maxY, d)))
    };
    t.expand3D = function(e, f, b, d, h, a) {
        this.minX = q.min(this.minX, e);
        this.maxX = q.max(this.maxX, e);
        this.minY = q.min(this.minY, f);
        this.maxY = q.max(this.maxY, f);
        this.minZ = q.min(this.minZ, b);
        this.maxZ = q.max(this.maxZ, b);
        d !== l && h !== l && a !== l && (this.minX = q.min(this.minX, d), this.maxX = q.max(this.maxX, d), this.minY = q.min(this.minY, h), this.maxY = q.max(this.maxY, h), this.minZ = q.min(this.minZ,
            a), this.maxZ = q.max(this.maxZ, a))
    }
})(ChemDoodle.math, Math);
ChemDoodle.featureDetection = function(f, q, l, t, e) {
    let k = {
        supports_canvas: function() {
            return !!l.createElement("canvas").getContext
        },
        supports_canvas_text: function() {
            return k.supports_canvas() ? "function" === typeof l.createElement("canvas").getContext("2d").fillText : !1
        },
        supports_webgl: function() {
            let b = l.createElement("canvas");
            try {
                if (b.getContext("webgl") || b.getContext("experimental-webgl")) return !0
            } catch (d) {}
            return !1
        },
        supports_xhr2: function() {
            return q.support.cors
        },
        supports_touch: function() {
            let b = (/iPhone|iPad|iPod|Android|BlackBerry|BB10/i.test(navigator.userAgent) ||
                "MacIntel" === navigator.platform && 1 < navigator.maxTouchPoints) && !t.MSStream;
            return "ontouchstart" in t && b
        },
        supports_gesture: function() {
            return "ongesturestart" in t
        }
    };
    return k
}(ChemDoodle.iChemLabs, ChemDoodle.lib.jQuery, document, window);
ChemDoodle.SYMBOLS = "H He Li Be B C N O F Ne Na Mg Al Si P S Cl Ar K Ca Sc Ti V Cr Mn Fe Co Ni Cu Zn Ga Ge As Se Br Kr Rb Sr Y Zr Nb Mo Tc Ru Rh Pd Ag Cd In Sn Sb Te I Xe Cs Ba La Ce Pr Nd Pm Sm Eu Gd Tb Dy Ho Er Tm Yb Lu Hf Ta W Re Os Ir Pt Au Hg Tl Pb Bi Po At Rn Fr Ra Ac Th Pa U Np Pu Am Cm Bk Cf Es Fm Md No Lr Rf Db Sg Bh Hs Mt Ds Rg Cn Nh Fl Mc Lv Ts Og".split(" ");
ChemDoodle.ELEMENT = function(f, q) {
    function l(f, e, k, b, d, h, a, g, n) {
        this.symbol = f;
        this.name = e;
        this.atomicNumber = k;
        this.addH = b;
        this.jmolColor = this.pymolColor = d;
        this.covalentRadius = h;
        this.vdWRadius = a;
        this.valency = g;
        this.mass = n
    }
    f = [];
    f.H = new l("H", "Hydrogen", 1, !1, "#FFFFFF", .31, 1.1, 1, 1);
    f.He = new l("He", "Helium", 2, !1, "#D9FFFF", .28, 1.4, 0, 4);
    f.Li = new l("Li", "Lithium", 3, !1, "#CC80FF", 1.28, 1.82, 1, 7);
    f.Be = new l("Be", "Beryllium", 4, !1, "#C2FF00", .96, 1.53, 2, 9);
    f.B = new l("B", "Boron", 5, !0, "#FFB5B5", .84, 1.92, 3, 11);
    f.C = new l("C",
        "Carbon", 6, !0, "#909090", .76, 1.7, 4, 12);
    f.N = new l("N", "Nitrogen", 7, !0, "#3050F8", .71, 1.55, 3, 14);
    f.O = new l("O", "Oxygen", 8, !0, "#FF0D0D", .66, 1.52, 2, 16);
    f.F = new l("F", "Fluorine", 9, !0, "#90E050", .57, 1.47, 1, 19);
    f.Ne = new l("Ne", "Neon", 10, !1, "#B3E3F5", .58, 1.54, 0, 20);
    f.Na = new l("Na", "Sodium", 11, !1, "#AB5CF2", 1.66, 2.27, 1, 23);
    f.Mg = new l("Mg", "Magnesium", 12, !1, "#8AFF00", 1.41, 1.73, 0, 24);
    f.Al = new l("Al", "Aluminum", 13, !1, "#BFA6A6", 1.21, 1.84, 0, 27);
    f.Si = new l("Si", "Silicon", 14, !0, "#F0C8A0", 1.11, 2.1, 4, 28);
    f.P = new l("P",
        "Phosphorus", 15, !0, "#FF8000", 1.07, 1.8, 3, 31);
    f.S = new l("S", "Sulfur", 16, !0, "#FFFF30", 1.05, 1.8, 2, 32);
    f.Cl = new l("Cl", "Chlorine", 17, !0, "#1FF01F", 1.02, 1.75, 1, 35);
    f.Ar = new l("Ar", "Argon", 18, !1, "#80D1E3", 1.06, 1.88, 0, 40);
    f.K = new l("K", "Potassium", 19, !1, "#8F40D4", 2.03, 2.75, 0, 39);
    f.Ca = new l("Ca", "Calcium", 20, !1, "#3DFF00", 1.76, 2.31, 0, 40);
    f.Sc = new l("Sc", "Scandium", 21, !1, "#E6E6E6", 1.7, 0, 0, 45);
    f.Ti = new l("Ti", "Titanium", 22, !1, "#BFC2C7", 1.6, 0, 1, 48);
    f.V = new l("V", "Vanadium", 23, !1, "#A6A6AB", 1.53, 0, 1, 51);
    f.Cr = new l("Cr",
        "Chromium", 24, !1, "#8A99C7", 1.39, 0, 2, 52);
    f.Mn = new l("Mn", "Manganese", 25, !1, "#9C7AC7", 1.39, 0, 3, 55);
    f.Fe = new l("Fe", "Iron", 26, !1, "#E06633", 1.32, 0, 2, 56);
    f.Co = new l("Co", "Cobalt", 27, !1, "#F090A0", 1.26, 0, 1, 59);
    f.Ni = new l("Ni", "Nickel", 28, !1, "#50D050", 1.24, 1.63, 1, 58);
    f.Cu = new l("Cu", "Copper", 29, !1, "#C88033", 1.32, 1.4, 0, 63);
    f.Zn = new l("Zn", "Zinc", 30, !1, "#7D80B0", 1.22, 1.39, 0, 64);
    f.Ga = new l("Ga", "Gallium", 31, !1, "#C28F8F", 1.22, 1.87, 0, 69);
    f.Ge = new l("Ge", "Germanium", 32, !1, "#668F8F", 1.2, 2.11, 4, 74);
    f.As = new l("As",
        "Arsenic", 33, !0, "#BD80E3", 1.19, 1.85, 3, 75);
    f.Se = new l("Se", "Selenium", 34, !0, "#FFA100", 1.2, 1.9, 2, 80);
    f.Br = new l("Br", "Bromine", 35, !0, "#A62929", 1.2, 1.85, 1, 79);
    f.Kr = new l("Kr", "Krypton", 36, !1, "#5CB8D1", 1.16, 2.02, 0, 84);
    f.Rb = new l("Rb", "Rubidium", 37, !1, "#702EB0", 2.2, 3.03, 0, 85);
    f.Sr = new l("Sr", "Strontium", 38, !1, "#00FF00", 1.95, 2.49, 0, 88);
    f.Y = new l("Y", "Yttrium", 39, !1, "#94FFFF", 1.9, 0, 0, 89);
    f.Zr = new l("Zr", "Zirconium", 40, !1, "#94E0E0", 1.75, 0, 0, 90);
    f.Nb = new l("Nb", "Niobium", 41, !1, "#73C2C9", 1.64, 0, 1, 93);
    f.Mo =
        new l("Mo", "Molybdenum", 42, !1, "#54B5B5", 1.54, 0, 2, 98);
    f.Tc = new l("Tc", "Technetium", 43, !1, "#3B9E9E", 1.47, 0, 3, 0);
    f.Ru = new l("Ru", "Ruthenium", 44, !1, "#248F8F", 1.46, 0, 2, 102);
    f.Rh = new l("Rh", "Rhodium", 45, !1, "#0A7D8C", 1.42, 0, 1, 103);
    f.Pd = new l("Pd", "Palladium", 46, !1, "#006985", 1.39, 1.63, 0, 106);
    f.Ag = new l("Ag", "Silver", 47, !1, "#C0C0C0", 1.45, 1.72, 0, 107);
    f.Cd = new l("Cd", "Cadmium", 48, !1, "#FFD98F", 1.44, 1.58, 0, 114);
    f.In = new l("In", "Indium", 49, !1, "#A67573", 1.42, 1.93, 0, 115);
    f.Sn = new l("Sn", "Tin", 50, !1, "#668080", 1.39,
        2.17, 4, 120);
    f.Sb = new l("Sb", "Antimony", 51, !1, "#9E63B5", 1.39, 2.06, 3, 121);
    f.Te = new l("Te", "Tellurium", 52, !0, "#D47A00", 1.38, 2.06, 2, 130);
    f.I = new l("I", "Iodine", 53, !0, "#940094", 1.39, 1.98, 1, 127);
    f.Xe = new l("Xe", "Xenon", 54, !1, "#429EB0", 1.4, 2.16, 0, 132);
    f.Cs = new l("Cs", "Cesium", 55, !1, "#57178F", 2.44, 3.43, 0, 133);
    f.Ba = new l("Ba", "Barium", 56, !1, "#00C900", 2.15, 2.68, 0, 138);
    f.La = new l("La", "Lanthanum", 57, !1, "#70D4FF", 2.07, 0, 0, 139);
    f.Ce = new l("Ce", "Cerium", 58, !1, "#FFFFC7", 2.04, 0, 0, 140);
    f.Pr = new l("Pr", "Praseodymium",
        59, !1, "#D9FFC7", 2.03, 0, 0, 141);
    f.Nd = new l("Nd", "Neodymium", 60, !1, "#C7FFC7", 2.01, 0, 0, 142);
    f.Pm = new l("Pm", "Promethium", 61, !1, "#A3FFC7", 1.99, 0, 0, 0);
    f.Sm = new l("Sm", "Samarium", 62, !1, "#8FFFC7", 1.98, 0, 0, 152);
    f.Eu = new l("Eu", "Europium", 63, !1, "#61FFC7", 1.98, 0, 0, 153);
    f.Gd = new l("Gd", "Gadolinium", 64, !1, "#45FFC7", 1.96, 0, 0, 158);
    f.Tb = new l("Tb", "Terbium", 65, !1, "#30FFC7", 1.94, 0, 0, 159);
    f.Dy = new l("Dy", "Dysprosium", 66, !1, "#1FFFC7", 1.92, 0, 0, 164);
    f.Ho = new l("Ho", "Holmium", 67, !1, "#00FF9C", 1.92, 0, 0, 165);
    f.Er = new l("Er",
        "Erbium", 68, !1, "#00E675", 1.89, 0, 0, 166);
    f.Tm = new l("Tm", "Thulium", 69, !1, "#00D452", 1.9, 0, 0, 169);
    f.Yb = new l("Yb", "Ytterbium", 70, !1, "#00BF38", 1.87, 0, 0, 174);
    f.Lu = new l("Lu", "Lutetium", 71, !1, "#00AB24", 1.87, 0, 0, 175);
    f.Hf = new l("Hf", "Hafnium", 72, !1, "#4DC2FF", 1.75, 0, 0, 180);
    f.Ta = new l("Ta", "Tantalum", 73, !1, "#4DA6FF", 1.7, 0, 1, 181);
    f.W = new l("W", "Tungsten", 74, !1, "#2194D6", 1.62, 0, 2, 184);
    f.Re = new l("Re", "Rhenium", 75, !1, "#267DAB", 1.51, 0, 3, 187);
    f.Os = new l("Os", "Osmium", 76, !1, "#266696", 1.44, 0, 2, 192);
    f.Ir = new l("Ir",
        "Iridium", 77, !1, "#175487", 1.41, 0, 3, 193);
    f.Pt = new l("Pt", "Platinum", 78, !1, "#D0D0E0", 1.36, 1.75, 0, 195);
    f.Au = new l("Au", "Gold", 79, !1, "#FFD123", 1.36, 1.66, 1, 197);
    f.Hg = new l("Hg", "Mercury", 80, !1, "#B8B8D0", 1.32, 1.55, 0, 202);
    f.Tl = new l("Tl", "Thallium", 81, !1, "#A6544D", 1.45, 1.96, 0, 205);
    f.Pb = new l("Pb", "Lead", 82, !1, "#575961", 1.46, 2.02, 4, 208);
    f.Bi = new l("Bi", "Bismuth", 83, !1, "#9E4FB5", 1.48, 2.07, 3, 209);
    f.Po = new l("Po", "Polonium", 84, !1, "#AB5C00", 1.4, 1.97, 2, 0);
    f.At = new l("At", "Astatine", 85, !0, "#754F45", 1.5, 2.02, 1,
        0);
    f.Rn = new l("Rn", "Radon", 86, !1, "#428296", 1.5, 2.2, 0, 0);
    f.Fr = new l("Fr", "Francium", 87, !1, "#420066", 2.6, 3.48, 0, 0);
    f.Ra = new l("Ra", "Radium", 88, !1, "#007D00", 2.21, 2.83, 0, 0);
    f.Ac = new l("Ac", "Actinium", 89, !1, "#70ABFA", 2.15, 0, 0, 0);
    f.Th = new l("Th", "Thorium", 90, !1, "#00BAFF", 2.06, 0, 0, 232);
    f.Pa = new l("Pa", "Protactinium", 91, !1, "#00A1FF", 2, 0, 0, 231);
    f.U = new l("U", "Uranium", 92, !1, "#008FFF", 1.96, 1.86, 0, 238);
    f.Np = new l("Np", "Neptunium", 93, !1, "#0080FF", 1.9, 0, 0, 0);
    f.Pu = new l("Pu", "Plutonium", 94, !1, "#006BFF", 1.87, 0,
        0, 0);
    f.Am = new l("Am", "Americium", 95, !1, "#545CF2", 1.8, 0, 0, 0);
    f.Cm = new l("Cm", "Curium", 96, !1, "#785CE3", 1.69, 0, 0, 0);
    f.Bk = new l("Bk", "Berkelium", 97, !1, "#8A4FE3", 0, 0, 0, 0);
    f.Cf = new l("Cf", "Californium", 98, !1, "#A136D4", 0, 0, 0, 0);
    f.Es = new l("Es", "Einsteinium", 99, !1, "#B31FD4", 0, 0, 0, 0);
    f.Fm = new l("Fm", "Fermium", 100, !1, "#B31FBA", 0, 0, 0, 0);
    f.Md = new l("Md", "Mendelevium", 101, !1, "#B30DA6", 0, 0, 0, 0);
    f.No = new l("No", "Nobelium", 102, !1, "#BD0D87", 0, 0, 0, 0);
    f.Lr = new l("Lr", "Lawrencium", 103, !1, "#C70066", 0, 0, 0, 0);
    f.Rf = new l("Rf",
        "Rutherfordium", 104, !1, "#CC0059", 0, 0, 0, 0);
    f.Db = new l("Db", "Dubnium", 105, !1, "#D1004F", 0, 0, 0, 0);
    f.Sg = new l("Sg", "Seaborgium", 106, !1, "#D90045", 0, 0, 0, 0);
    f.Bh = new l("Bh", "Bohrium", 107, !1, "#E00038", 0, 0, 0, 0);
    f.Hs = new l("Hs", "Hassium", 108, !1, "#E6002E", 0, 0, 0, 0);
    f.Mt = new l("Mt", "Meitnerium", 109, !1, "#EB0026", 0, 0, 0, 0);
    f.Ds = new l("Ds", "Darmstadtium", 110, !1, "#000000", 0, 0, 0, 0);
    f.Rg = new l("Rg", "Roentgenium", 111, !1, "#000000", 0, 0, 0, 0);
    f.Cn = new l("Cn", "Copernicium", 112, !1, "#000000", 0, 0, 0, 0);
    f.Nh = new l("Nh", "Nihonium",
        113, !1, "#000000", 0, 0, 0, 0);
    f.Fl = new l("Fl", "Flerovium", 114, !1, "#000000", 0, 0, 0, 0);
    f.Mc = new l("Mc", "Moscovium", 115, !1, "#000000", 0, 0, 0, 0);
    f.Lv = new l("Lv", "Livermorium", 116, !1, "#000000", 0, 0, 0, 0);
    f.Ts = new l("Ts", "Tennessine", 117, !1, "#000000", 0, 0, 0, 0);
    f.Og = new l("Og", "Oganesson", 118, !1, "#000000", 0, 0, 0, 0);
    f.H.pymolColor = "#E6E6E6";
    f.C.pymolColor = "#33FF33";
    f.N.pymolColor = "#3333FF";
    f.O.pymolColor = "#FF4D4D";
    f.F.pymolColor = "#B3FFFF";
    f.S.pymolColor = "#E6C640";
    return f
}(ChemDoodle.SYMBOLS);
ChemDoodle.RESIDUE = function(f) {
    function q(f, t, e, k, b, d) {
        this.symbol = f;
        this.name = t;
        this.polar = e;
        this.aminoColor = k;
        this.shapelyColor = b;
        this.acidity = d
    }
    f = [];
    f.Ala = new q("Ala", "Alanine", !1, "#C8C8C8", "#8CFF8C", 0);
    f.Arg = new q("Arg", "Arginine", !0, "#145AFF", "#00007C", 1);
    f.Asn = new q("Asn", "Asparagine", !0, "#00DCDC", "#FF7C70", 0);
    f.Asp = new q("Asp", "Aspartic Acid", !0, "#E60A0A", "#A00042", -1);
    f.Cys = new q("Cys", "Cysteine", !0, "#E6E600", "#FFFF70", 0);
    f.Gln = new q("Gln", "Glutamine", !0, "#00DCDC", "#FF4C4C", 0);
    f.Glu = new q("Glu",
        "Glutamic Acid", !0, "#E60A0A", "#660000", -1);
    f.Gly = new q("Gly", "Glycine", !1, "#EBEBEB", "#FFFFFF", 0);
    f.His = new q("His", "Histidine", !0, "#8282D2", "#7070FF", 1);
    f.Ile = new q("Ile", "Isoleucine", !1, "#0F820F", "#004C00", 0);
    f.Leu = new q("Leu", "Leucine", !1, "#0F820F", "#455E45", 0);
    f.Lys = new q("Lys", "Lysine", !0, "#145AFF", "#4747B8", 1);
    f.Met = new q("Met", "Methionine", !1, "#E6E600", "#B8A042", 0);
    f.Phe = new q("Phe", "Phenylalanine", !1, "#3232AA", "#534C52", 0);
    f.Pro = new q("Pro", "Proline", !1, "#DC9682", "#525252", 0);
    f.Ser = new q("Ser",
        "Serine", !0, "#FA9600", "#FF7042", 0);
    f.Thr = new q("Thr", "Threonine", !0, "#FA9600", "#B84C00", 0);
    f.Trp = new q("Trp", "Tryptophan", !0, "#B45AB4", "#4F4600", 0);
    f.Tyr = new q("Tyr", "Tyrosine", !0, "#3232AA", "#8C704C", 0);
    f.Val = new q("Val", "Valine", !1, "#0F820F", "#FF8CFF", 0);
    f.Asx = new q("Asx", "Asparagine/Aspartic Acid", !0, "#FF69B4", "#FF00FF", 0);
    f.Glx = new q("Glx", "Glutamine/Glutamic Acid", !0, "#FF69B4", "#FF00FF", 0);
    f["*"] = new q("*", "Other", !1, "#BEA06E", "#FF00FF", 0);
    f.A = new q("A", "Adenine", !1, "#BEA06E", "#A0A0FF", 0);
    f.G =
        new q("G", "Guanine", !1, "#BEA06E", "#FF7070", 0);
    f.I = new q("I", "", !1, "#BEA06E", "#80FFFF", 0);
    f.C = new q("C", "Cytosine", !1, "#BEA06E", "#FF8C4B", 0);
    f.T = new q("T", "Thymine", !1, "#BEA06E", "#A0FFA0", 0);
    f.U = new q("U", "Uracil", !1, "#BEA06E", "#FF8080", 0);
    return f
}();
(function(f, q) {
    f.Queue = function() {
        this.queue = []
    };
    f = f.Queue.prototype;
    f.queueSpace = 0;
    f.getSize = function() {
        return this.queue.length - this.queueSpace
    };
    f.isEmpty = function() {
        return 0 === this.queue.length
    };
    f.enqueue = function(f) {
        this.queue.push(f)
    };
    f.dequeue = function() {
        let f;
        this.queue.length && (f = this.queue[this.queueSpace], 2 * ++this.queueSpace >= this.queue.length && (this.queue = this.queue.slice(this.queueSpace), this.queueSpace = 0));
        return f
    };
    f.getOldestElement = function() {
        let f;
        this.queue.length && (f = this.queue[this.queueSpace]);
        return f
    }
})(ChemDoodle.structures);
(function(f, q, l) {
    f.Point = function(f, e) {
        this.x = f ? f : 0;
        this.y = e ? e : 0
    };
    f = f.Point.prototype;
    f.sub = function(f) {
        this.x -= f.x;
        this.y -= f.y
    };
    f.add = function(f) {
        this.x += f.x;
        this.y += f.y
    };
    f.distance = function(f) {
        let e = f.x - this.x;
        f = f.y - this.y;
        return q.sqrt(e * e + f * f)
    };
    f.angleForStupidCanvasArcs = function(f) {
        var e = f.x - this.x;
        f = f.y - this.y;
        for (e = 0 === e ? 0 === f ? 0 : 0 < f ? q.PI / 2 : 3 * q.PI / 2 : 0 === f ? 0 < e ? 0 : q.PI : 0 > e ? q.atan(f / e) + q.PI : 0 > f ? q.atan(f / e) + 2 * q.PI : q.atan(f / e); 0 > e;) e += 2 * q.PI;
        return e %= 2 * q.PI
    };
    f.angle = function(f) {
        var e = f.x - this.x;
        f = this.y - f.y;
        for (e = 0 === e ? 0 === f ? 0 : 0 < f ? q.PI / 2 : 3 * q.PI / 2 : 0 === f ? 0 < e ? 0 : q.PI : 0 > e ? q.atan(f / e) + q.PI : 0 > f ? q.atan(f / e) + 2 * q.PI : q.atan(f / e); 0 > e;) e += 2 * q.PI;
        return e %= 2 * q.PI
    }
})(ChemDoodle.structures, Math);
(function(f, q, l, t) {
    let e = /[ ,]+/,
        k = /\-+/,
        b = ["Helvetica", "Arial", "Dialog"];
    q.Query = function(b) {
        this.type = b;
        this.elements = {
            v: [],
            not: !1
        };
        this.saturation = this.hydrogens = this.connectivityNoH = this.connectivity = this.chirality = this.charge = t;
        this.orders = {
            v: [],
            not: !1
        };
        this.cache = this.ringCount = this.aromatic = this.stereo = t
    };
    q.Query.TYPE_ATOM = 0;
    q.Query.TYPE_BOND = 1;
    l = q.Query.prototype;
    l.parseRange = function(b) {
        let d = [];
        b = b.split(e);
        for (let h = 0, e = b.length; h < e; h++) {
            var a = b[h],
                g = !1,
                n = !1;
            "-" === a.charAt(0) && (g = !0, a =
                a.substring(1)); - 1 != a.indexOf("--") && (n = !0); - 1 != a.indexOf("-") ? (a = a.split(k), g = {
                x: parseInt(a[0]) * (g ? -1 : 1),
                y: parseInt(a[1]) * (n ? -1 : 1)
            }, g.y < g.x && (n = g.y, g.y = g.x, g.x = n), d.push(g)) : d.push({
                x: parseInt(a) * (g ? -1 : 1)
            })
        }
        return d
    };
    l.draw = function(d, h, a) {
        this.cache || (this.cache = this.toString());
        let g = this.cache,
            e = t;
        var v = g.indexOf("("); - 1 != v && (g = this.cache.substring(0, v), e = this.cache.substring(v, this.cache.length));
        d.textAlign = "center";
        d.textBaseline = "middle";
        d.font = f.getFontString(12, b, !0, !1);
        v = d.measureText(g).width;
        d.fillStyle = h.backgroundColor;
        d.fillRect(a.x - v / 2, a.y - 6, v, 12);
        d.fillStyle = "black";
        d.fillText(g, a.x, a.y);
        e && (d.font = f.getFontString(10, b, !1, !0), v = d.measureText(e).width, d.fillStyle = h.backgroundColor, d.fillRect(a.x - v / 2, a.y + 6, v, 11), d.fillStyle = "black", d.fillText(e, a.x, a.y + 11))
    };
    l.outputRange = function(b) {
        let d = !1,
            a = [];
        for (let g = 0, h = b.length; g < h; g++) {
            d && a.push(",");
            d = !0;
            let h = b[g];
            h.y ? (a.push(h.x), a.push("-"), a.push(h.y)) : a.push(h.x)
        }
        return a.join("")
    };
    l.toString = function() {
        let b = [],
            h = [];
        this.type === q.Query.TYPE_ATOM ?
            (this.elements && 0 !== this.elements.v.length ? (this.elements.not && b.push("!"), b.push("["), b.push(this.elements.v.join(",")), b.push("]")) : b.push("[a]"), this.chirality && h.push((this.chirality.not ? "!" : "") + "@\x3d" + this.chirality.v), this.aromatic && h.push((this.aromatic.not ? "!" : "") + "A"), this.charge && h.push((this.charge.not ? "!" : "") + "C\x3d" + this.outputRange(this.charge.v)), this.hydrogens && h.push((this.hydrogens.not ? "!" : "") + "H\x3d" + this.outputRange(this.hydrogens.v)), this.ringCount && h.push((this.ringCount.not ?
                "!" : "") + "R\x3d" + this.outputRange(this.ringCount.v)), this.saturation && h.push((this.saturation.not ? "!" : "") + "S"), this.connectivity && h.push((this.connectivity.not ? "!" : "") + "X\x3d" + this.outputRange(this.connectivity.v)), this.connectivityNoH && h.push((this.connectivityNoH.not ? "!" : "") + "x\x3d" + this.outputRange(this.connectivityNoH.v))) : this.type === q.Query.TYPE_BOND && (this.orders && 0 !== this.orders.v.length ? (this.orders.not && b.push("!"), b.push("["), b.push(this.orders.v.join(",")), b.push("]")) : b.push("[a]"), this.stereo &&
                h.push((this.stereo.not ? "!" : "") + "@\x3d" + this.stereo.v), this.aromatic && h.push((this.aromatic.not ? "!" : "") + "A"), this.ringCount && h.push((this.ringCount.not ? "!" : "") + "R\x3d" + this.outputRange(this.ringCount.v)));
        0 < h.length && (b.push("("), b.push(h.join(",")), b.push(")"));
        return b.join("")
    }
})(ChemDoodle.extensions, ChemDoodle.structures, Math);
(function(f, q, l, t, e, k, b) {
    let d = /\s+/g;
    t.Atom = function(a, b, d, h) {
        this.label = a ? a.trim() : "C";
        this.x = b ? b : 0;
        this.y = d ? d : 0;
        this.z = h ? h : 0
    };
    let h = t.Atom.prototype = new t.Point(0, 0);
    h.charge = 0;
    h.numLonePair = 0;
    h.numRadical = 0;
    h.mass = -1;
    h.implicitH = -1;
    h.coordinationNumber = 0;
    h.bondNumber = 0;
    h.angleOfLeastInterference = 0;
    h.isHidden = !1;
    h.altLabel = b;
    h.isLone = !1;
    h.isHover = !1;
    h.isSelected = !1;
    h.add3D = function(a) {
        this.x += a.x;
        this.y += a.y;
        this.z += a.z
    };
    h.sub3D = function(a) {
        this.x -= a.x;
        this.y -= a.y;
        this.z -= a.z
    };
    h.distance3D = function(a) {
        let b =
            a.x - this.x,
            d = a.y - this.y;
        a = a.z - this.z;
        return e.sqrt(b * b + d * d + a * a)
    };
    h.draw = function(a, g) {
        if (!this.dontDraw) {
            if (this.isLassoed) {
                var h = a.createRadialGradient(this.x - 1, this.y - 1, 0, this.x, this.y, 7);
                h.addColorStop(0, "rgba(212, 99, 0, 0)");
                h.addColorStop(.7, "rgba(212, 99, 0, 0.8)");
                a.fillStyle = h;
                a.beginPath();
                a.arc(this.x, this.y, 5, 0, 2 * e.PI, !1);
                a.fill()
            }
            if (!this.query) {
                this.textBounds = [];
                this.styles && (g = this.styles);
                var v = q.getFontString(g.atoms_font_size_2D, g.atoms_font_families_2D, g.atoms_font_bold_2D, g.atoms_font_italic_2D);
                a.font = v;
                a.fillStyle = this.getElementColor(g.atoms_useJMOLColors, g.atoms_usePYMOLColors, g.atoms_color, 2);
                "H" === this.label && g.atoms_HBlack_2D && (a.fillStyle = "black");
                this.error && (a.fillStyle = g.colorError);
                h = this.isLabelVisible(g);
                if (this.isLone && !h || g.atoms_circles_2D) this.isLone && (a.fillStyle = "#909090"), a.beginPath(), a.arc(this.x, this.y, g.atoms_circleDiameter_2D / 2, 0, 2 * e.PI, !1), a.fill(), 0 < g.atoms_circleBorderWidth_2D && (a.lineWidth = g.atoms_circleBorderWidth_2D, a.strokeStyle = "black", a.stroke());
                else if (h)
                    if (a.textAlign =
                        "center", a.textBaseline = "middle", this.altLabel !== b) a.fillText(this.altLabel, this.x, this.y), h = a.measureText(this.altLabel).width, this.textBounds.push({
                        x: this.x - h / 2,
                        y: this.y - g.atoms_font_size_2D / 2 + 1,
                        w: h,
                        h: g.atoms_font_size_2D - 2
                    });
                    else if (f[this.label]) {
                    a.fillText(this.label, this.x, this.y);
                    var m = a.measureText(this.label).width;
                    this.textBounds.push({
                        x: this.x - m / 2,
                        y: this.y - g.atoms_font_size_2D / 2 + 1,
                        w: m,
                        h: g.atoms_font_size_2D - 2
                    });
                    var k = 0; - 1 !== this.mass && (h = a.font, a.font = q.getFontString(.7 * g.atoms_font_size_2D,
                        g.atoms_font_families_2D, g.atoms_font_bold_2D, g.atoms_font_italic_2D), k = a.measureText(this.mass).width, a.fillText(this.mass, this.x - k - .5, this.y - g.atoms_font_size_2D / 2 + 1), this.textBounds.push({
                        x: this.x - m / 2 - k - .5,
                        y: this.y - 1.7 * g.atoms_font_size_2D / 2 + 1,
                        w: k,
                        h: g.atoms_font_size_2D / 2 - 1
                    }), a.font = h);
                    h = m / 2;
                    var u = this.getImplicitHydrogenCount();
                    if (g.atoms_implicitHydrogens_2D && 0 < u) {
                        var w = 0;
                        var z = a.measureText("H").width;
                        let b = !0;
                        if (1 < u) {
                            let c = m / 2 + z / 2,
                                d = 0,
                                h = q.getFontString(.8 * g.atoms_font_size_2D, g.atoms_font_families_2D,
                                    g.atoms_font_bold_2D, g.atoms_font_italic_2D);
                            a.font = h;
                            let n = a.measureText(u).width;
                            1 === this.bondNumber ? this.angleOfLeastInterference > e.PI / 2 && this.angleOfLeastInterference < 3 * e.PI / 2 && (c = -m / 2 - n - z / 2 - k / 2, b = !1, w = e.PI) : this.angleOfLeastInterference <= e.PI / 4 || (this.angleOfLeastInterference < 3 * e.PI / 4 ? (c = 0, d = .9 * -g.atoms_font_size_2D, 0 !== this.charge && (d -= .3 * g.atoms_font_size_2D), b = !1, w = e.PI / 2) : this.angleOfLeastInterference <= 5 * e.PI / 4 ? (c = -m / 2 - n - z / 2 - k / 2, b = !1, w = e.PI) : this.angleOfLeastInterference < 7 * e.PI / 4 && (c = 0, d =
                                .9 * g.atoms_font_size_2D, b = !1, w = 3 * e.PI / 2));
                            a.font = v;
                            a.fillText("H", this.x + c, this.y + d);
                            a.font = h;
                            a.fillText(u, this.x + c + z / 2 + n / 2, this.y + d + .3 * g.atoms_font_size_2D);
                            this.textBounds.push({
                                x: this.x + c - z / 2,
                                y: this.y + d - g.atoms_font_size_2D / 2 + 1,
                                w: z,
                                h: g.atoms_font_size_2D - 2
                            });
                            this.textBounds.push({
                                x: this.x + c + z / 2,
                                y: this.y + d + .3 * g.atoms_font_size_2D - g.atoms_font_size_2D / 2 + 1,
                                w: n,
                                h: .8 * g.atoms_font_size_2D - 2
                            })
                        } else v = m / 2 + z / 2, u = 0, 1 === this.bondNumber ? this.angleOfLeastInterference > e.PI / 2 && this.angleOfLeastInterference < 3 *
                            e.PI / 2 && (v = -m / 2 - z / 2 - k / 2, b = !1, w = e.PI) : this.angleOfLeastInterference <= e.PI / 4 || (this.angleOfLeastInterference < 3 * e.PI / 4 ? (v = 0, u = .9 * -g.atoms_font_size_2D, b = !1, w = e.PI / 2) : this.angleOfLeastInterference <= 5 * e.PI / 4 ? (v = -m / 2 - z / 2 - k / 2, b = !1, w = e.PI) : this.angleOfLeastInterference < 7 * e.PI / 4 && (v = 0, u = .9 * g.atoms_font_size_2D, b = !1, w = 3 * e.PI / 2)), a.fillText("H", this.x + v, this.y + u), this.textBounds.push({
                                x: this.x + v - z / 2,
                                y: this.y + u - g.atoms_font_size_2D / 2 + 1,
                                w: z,
                                h: g.atoms_font_size_2D - 2
                            });
                        b && (h += z)
                    }
                    0 !== this.charge && (m = this.charge.toFixed(0),
                        m = "1" === m ? "+" : "-1" === m ? "\u2013" : m.startsWith("-") ? m.substring(1) + "\u2013" : m + "+", k = a.measureText(m).width, h += k / 2, a.textAlign = "center", a.textBaseline = "middle", a.font = q.getFontString(e.floor(.8 * g.atoms_font_size_2D), g.atoms_font_families_2D, g.atoms_font_bold_2D, g.atoms_font_italic_2D), a.fillText(m, this.x + h - 1, this.y - g.atoms_font_size_2D / 2 + 1), this.textBounds.push({
                            x: this.x + h - k / 2 - 1,
                            y: this.y - 1.8 * g.atoms_font_size_2D / 2 + 5,
                            w: k,
                            h: g.atoms_font_size_2D / 2 - 1
                        }))
                } else t.CondensedLabel ? this.label.match(d) ? (a.textAlign =
                    "left", this.error && (a.fillStyle = g.colorError), a.fillText(this.label, this.x, this.y), h = a.measureText(this.label).width, this.textBounds.push({
                        x: this.x + 1,
                        y: this.y - g.atoms_font_size_2D / 2 + 1,
                        w: h,
                        h: g.atoms_font_size_2D - 2
                    })) : (this.condensed && this.condensed.text === this.label || (this.condensed = new t.CondensedLabel(this, this.label)), this.condensed.draw(a, g)) : (a.fillText(this.label, this.x, this.y), h = a.measureText(this.label).width, this.textBounds.push({
                    x: this.x - h / 2,
                    y: this.y - g.atoms_font_size_2D / 2 + 1,
                    w: h,
                    h: g.atoms_font_size_2D -
                        2
                }));
                if (0 < this.numLonePair || 0 < this.numRadical) {
                    a.fillStyle = "black";
                    m = this.angles.slice(0);
                    h = this.angleOfLeastInterference;
                    k = this.largestAngle;
                    w !== b && (m.push(w), m.sort(function(a, c) {
                        return a - c
                    }), k = l.angleBetweenLargest(m), h = k.angle % (2 * e.PI), k = k.largest);
                    v = [];
                    for (z = 0; z < this.numLonePair; z++) v.push({
                        t: 2
                    });
                    for (z = 0; z < this.numRadical; z++) v.push({
                        t: 1
                    });
                    if (w === b && e.abs(k - 2 * e.PI / m.length) < e.PI / 60) {
                        m = e.ceil(v.length / m.length);
                        for (let b = 0, c = v.length; b < c; b += m, h += k) this.drawElectrons(a, g, v.slice(b, e.min(v.length,
                            b + m)), h, k, w)
                    } else this.drawElectrons(a, g, v, h, k, w)
                }
            }
        }
    };
    h.drawElectrons = function(a, d, h, f, m, k) {
        k = m / (h.length + (0 === this.bonds.length && k === b ? 0 : 1));
        f = f - m / 2 + k;
        for (m = 0; m < h.length; m++) {
            var g = h[m],
                n = f + m * k;
            let b = this.x + Math.cos(n) * d.atoms_lonePairDistance_2D,
                v = this.y - Math.sin(n) * d.atoms_lonePairDistance_2D;
            2 === g.t ? (n += Math.PI / 2, g = Math.cos(n) * d.atoms_lonePairSpread_2D / 2, n = -Math.sin(n) * d.atoms_lonePairSpread_2D / 2, a.beginPath(), a.arc(b + g, v + n, d.atoms_lonePairDiameter_2D, 0, 2 * e.PI, !1), a.fill(), a.beginPath(), a.arc(b -
                g, v - n, d.atoms_lonePairDiameter_2D, 0, 2 * e.PI, !1), a.fill()) : 1 === g.t && (a.beginPath(), a.arc(b, v, d.atoms_lonePairDiameter_2D, 0, 2 * e.PI, !1), a.fill())
        }
    };
    h.drawDecorations = function(a, b) {
        if (this.isHover || this.isSelected) a.strokeStyle = this.isHover ? b.colorHover : b.colorSelect, a.lineWidth = 1.2, a.beginPath(), a.arc(this.x, this.y, this.isHover ? 7 : 15, 0, 2 * e.PI, !1), a.stroke();
        this.isOverlap && (a.strokeStyle = b.colorError, a.lineWidth = 1.2, a.beginPath(), a.arc(this.x, this.y, 7, 0, 2 * e.PI, !1), a.stroke())
    };
    h.render = function(a, b, d) {
        this.styles &&
            (b = this.styles);
        let g = k.translate(k.identity(), [this.x, this.y, this.z]),
            h = b.atoms_useVDWDiameters_3D ? f[this.label].vdWRadius * b.atoms_vdwMultiplier_3D : b.atoms_sphereDiameter_3D / 2;
        0 === h && (h = 1);
        k.scale(g, [h, h, h]);
        d || (d = b.atoms_color, b.atoms_useJMOLColors ? d = f[this.label].jmolColor : b.atoms_usePYMOLColors && (d = f[this.label].pymolColor), a.material.setDiffuseColor(a, d));
        a.shader.setMatrixUniforms(a, g);
        a.drawElements(a.TRIANGLES, (this.renderAsStar ? a.starBuffer : a.sphereBuffer).vertexIndexBuffer.numItems, a.UNSIGNED_SHORT,
            0)
    };
    h.renderHighlight = function(a, b) {
        if (this.isSelected || this.isHover) {
            this.styles && (b = this.styles);
            let d = k.translate(k.identity(), [this.x, this.y, this.z]),
                g = b.atoms_useVDWDiameters_3D ? f[this.label].vdWRadius * b.atoms_vdwMultiplier_3D : b.atoms_sphereDiameter_3D / 2;
            0 === g && (g = 1);
            g *= 1.3;
            k.scale(d, [g, g, g]);
            a.shader.setMatrixUniforms(a, d);
            a.material.setDiffuseColor(a, this.isHover ? b.colorHover : b.colorSelect);
            a.drawElements(a.TRIANGLES, (this.renderAsStar ? a.starBuffer : a.sphereBuffer).vertexIndexBuffer.numItems,
                a.UNSIGNED_SHORT, 0)
        }
    };
    h.isLabelVisible = function(a) {
        return a.atoms_displayAllCarbonLabels_2D || "C" !== this.label || this.altLabel || !f[this.label] || -1 !== this.mass || -1 !== this.implicitH || 0 !== this.charge || a.atoms_showAttributedCarbons_2D && (0 !== this.numRadical || 0 !== this.numLonePair) || this.isHidden && a.atoms_showHiddenCarbons_2D || a.atoms_displayTerminalCarbonLabels_2D && 1 === this.bondNumber ? !0 : !1
    };
    h.getImplicitHydrogenCount = function() {
        if (!f[this.label] || !f[this.label].addH) return 0;
        if (-1 !== this.implicitH) return this.implicitH;
        if ("H" === this.label) return 0;
        var a = f[this.label].valency;
        let b = a - this.coordinationNumber;
        0 < this.numRadical && (b = e.max(0, b - this.numRadical));
        0 < this.charge ? (a = 4 - a, b = this.charge <= a ? b + this.charge : 4 - this.coordinationNumber - this.charge + a) : b += this.charge;
        return 0 > b ? 0 : e.floor(b)
    };
    h.getBounds = function() {
        let a = new l.Bounds;
        a.expand(this.x, this.y);
        if (this.textBounds)
            for (let b = 0, d = this.textBounds.length; b < d; b++) {
                let d = this.textBounds[b];
                a.expand(d.x, d.y, d.x + d.w, d.y + d.h)
            }
        return a
    };
    h.getBounds3D = function() {
        let a =
            new l.Bounds;
        a.expand3D(this.x, this.y, this.z);
        return a
    };
    h.getElementColor = function(a, b, d) {
        if (!f[this.label]) return "#000";
        a ? d = f[this.label].jmolColor : b && (d = f[this.label].pymolColor);
        return d
    }
})(ChemDoodle.ELEMENT, ChemDoodle.extensions, ChemDoodle.math, ChemDoodle.structures, Math, ChemDoodle.lib.mat4);
(function(f, q, l, t, e, k, b, d) {
    l.Bond = function(b, a, g) {
        this.a1 = b;
        this.a2 = a;
        this.bondOrder = g !== d ? g : 1
    };
    l.Bond.STEREO_NONE = "none";
    l.Bond.STEREO_PROTRUDING = "protruding";
    l.Bond.STEREO_RECESSED = "recessed";
    l.Bond.STEREO_AMBIGUOUS = "ambiguous";
    f = l.Bond.prototype;
    f.stereo = l.Bond.STEREO_NONE;
    f.isHover = !1;
    f.ring = d;
    f.getCenter = function() {
        return new l.Point((this.a1.x + this.a2.x) / 2, (this.a1.y + this.a2.y) / 2)
    };
    f.getLength = function() {
        return this.a1.distance(this.a2)
    };
    f.getLength3D = function() {
        return this.a1.distance3D(this.a2)
    };
    f.contains = function(b) {
        return b === this.a1 || b === this.a2
    };
    f.getNeighbor = function(b) {
        return b === this.a1 ? this.a2 : b === this.a2 ? this.a1 : d
    };
    f.draw = function(b, a) {
        if (this.a1.x !== this.a2.x || this.a1.y !== this.a2.y) {
            this.styles && (a = this.styles);
            var d = this.a1.x,
                h = this.a2.x,
                f = this.a1.y,
                m = this.a2.y,
                k = this.a1.distance(this.a2),
                u = h - d,
                w = m - f;
            if (this.a1.isLassoed && this.a2.isLassoed) {
                let a = b.createLinearGradient(d, f, h, m);
                a.addColorStop(0, "rgba(212, 99, 0, 0)");
                a.addColorStop(.5, "rgba(212, 99, 0, 0.8)");
                a.addColorStop(1,
                    "rgba(212, 99, 0, 0)");
                let g = this.a1.angle(this.a2) + e.PI / 2,
                    c = e.cos(g),
                    n = e.sin(g),
                    k = d - 2.5 * c,
                    v = f + 2.5 * n,
                    u = d + 2.5 * c,
                    x = f - 2.5 * n,
                    w = h + 2.5 * c,
                    l = m - 2.5 * n,
                    t = h - 2.5 * c,
                    q = m + 2.5 * n;
                b.fillStyle = a;
                b.beginPath();
                b.moveTo(k, v);
                b.lineTo(u, x);
                b.lineTo(w, l);
                b.lineTo(t, q);
                b.closePath();
                b.fill()
            }
            if (a.atoms_display && !a.atoms_circles_2D && this.a1.isLabelVisible(a) && this.a1.textBounds) {
                let b = 0;
                for (let a = 0, d = this.a1.textBounds.length; a < d; a++) b = Math.max(b, t.calculateDistanceInterior(this.a1, this.a2, this.a1.textBounds[a]));
                b += a.bonds_atomLabelBuffer_2D;
                let g = b / k;
                d += u * g;
                f += w * g
            }
            if (a.atoms_display && !a.atoms_circles_2D && this.a2.isLabelVisible(a) && this.a2.textBounds) {
                let b = 0;
                for (let a = 0, d = this.a2.textBounds.length; a < d; a++) b = Math.max(b, t.calculateDistanceInterior(this.a2, this.a1, this.a2.textBounds[a]));
                b += a.bonds_atomLabelBuffer_2D;
                let d = b / k;
                h -= u * d;
                m -= w * d
            }
            if (a.bonds_clearOverlaps_2D) {
                let g = d + .15 * u,
                    e = f + .15 * w,
                    c = h - .15 * u,
                    n = m - .15 * w;
                b.strokeStyle = a.backgroundColor;
                b.lineWidth = a.bonds_width_2D + 2 * a.bonds_overlapClearWidth_2D;
                b.lineCap = "round";
                b.beginPath();
                b.moveTo(g,
                    e);
                b.lineTo(c, n);
                b.closePath();
                b.stroke()
            }
            b.strokeStyle = this.error ? a.colorError : a.bonds_color;
            b.fillStyle = this.error ? a.colorError : a.bonds_color;
            b.lineWidth = a.bonds_width_2D;
            b.lineCap = a.bonds_ends_2D;
            if (a.bonds_splitColor) {
                let g = b.createLinearGradient(d, f, h, m),
                    e = this.a1.styles ? this.a1.styles : a,
                    c = this.a2.styles ? this.a2.styles : a,
                    n = this.a1.getElementColor(e.atoms_useJMOLColors, e.atoms_usePYMOLColors, e.atoms_color, 2),
                    k = this.a2.getElementColor(c.atoms_useJMOLColors, c.atoms_usePYMOLColors, c.atoms_color,
                        2);
                g.addColorStop(0, n);
                a.bonds_colorGradient || (g.addColorStop(.5, n), g.addColorStop(.51, k));
                g.addColorStop(1, k);
                b.strokeStyle = g;
                b.fillStyle = g
            }
            if (a.bonds_lewisStyle_2D && 0 === this.bondOrder % 1) this.drawLewisStyle(b, a, d, f, h, m);
            else switch (this.query ? 1 : this.bondOrder) {
                case 0:
                    if (this.stereo === l.Bond.STEREO_PROTRUDING) {
                        let g = a.bonds_wedgeThickness_2D / 2,
                            n = this.a1.angle(this.a2),
                            c = n + e.PI / 2,
                            k = 2 * a.shapes_arrowLength_2D / e.sqrt(3),
                            v = e.cos(n),
                            u = e.sin(n),
                            x = e.cos(c),
                            w = e.sin(c),
                            l = h - v * k * .8,
                            t = m + u * k * .8,
                            q = l + x * g,
                            K = t - w * g,
                            N = l - x * g,
                            P = t + w * g;
                        b.beginPath();
                        b.moveTo(h, m);
                        b.lineTo(q, K);
                        b.lineTo(N, P);
                        b.closePath();
                        b.fill();
                        b.stroke();
                        b.beginPath();
                        b.moveTo(d, f);
                        b.lineTo(l, t);
                        b.stroke()
                    } else {
                        let g = h - d,
                            n = m - f,
                            c = e.sqrt(g * g + n * n),
                            k = e.floor(c / a.bonds_dotSize_2D),
                            v = (c - (k - 1) * a.bonds_dotSize_2D) / 2;
                        1 === k % 2 ? v += a.bonds_dotSize_2D / 4 : (v -= a.bonds_dotSize_2D / 4, k += 2);
                        k /= 2;
                        let u = this.a1.angle(this.a2),
                            x = d + v * Math.cos(u),
                            w = f - v * Math.sin(u);
                        b.beginPath();
                        for (let c = 0; c < k; c++) b.arc(x, w, a.bonds_dotSize_2D / 2, 0, 2 * e.PI, !1), x += 2 * a.bonds_dotSize_2D * Math.cos(u),
                            w -= 2 * a.bonds_dotSize_2D * Math.sin(u);
                        b.fill();
                        break
                    }
                    case .5:
                        b.beginPath();
                        b.moveTo(d, f);
                        b.lineTo(h, m);
                        b.setLineDash([a.bonds_hashSpacing_2D, a.bonds_hashSpacing_2D]);
                        b.stroke();
                        b.setLineDash([]);
                        break;
                    case 1:
                        if (this.query || this.stereo !== l.Bond.STEREO_PROTRUDING && this.stereo !== l.Bond.STEREO_RECESSED)
                            if (this.query || this.stereo !== l.Bond.STEREO_AMBIGUOUS) b.beginPath(), b.moveTo(d, f), b.lineTo(h, m), b.stroke(), this.query && this.query.draw(b, a, this.getCenter());
                            else {
                                let g = h - d,
                                    n = m - f;
                                b.beginPath();
                                b.moveTo(d, f);
                                let c = e.floor(e.sqrt(g * g + n * n) / a.bonds_wavyLength_2D),
                                    k = d,
                                    v = f,
                                    u = this.a1.angle(this.a2) + e.PI / 2,
                                    x = e.cos(u),
                                    w = e.sin(u),
                                    l = g / c,
                                    t = n / c,
                                    q, K;
                                for (let d = 0; d < c; d++) {
                                    k += l;
                                    v += t;
                                    let c = 0 === d % 2 ? 1 : -1;
                                    q = a.bonds_wavyLength_2D * x * c + k - .5 * l;
                                    K = a.bonds_wavyLength_2D * -w * c + v - .5 * t;
                                    b.quadraticCurveTo(q, K, k, v)
                                }
                                b.stroke()
                            }
                        else {
                            let g = a.bonds_width_2D / 2,
                                n = a.bonds_wedgeThickness_2D / 2,
                                c = this.a1.angle(this.a2) + e.PI / 2,
                                k = e.cos(c),
                                v = e.sin(c),
                                u = d - k * g,
                                x = f + v * g,
                                w = d + k * g,
                                t = f - v * g,
                                q = h + k * n,
                                H = m - v * n,
                                K = h - k * n,
                                N = m + v * n;
                            b.beginPath();
                            b.moveTo(u, x);
                            b.lineTo(w,
                                t);
                            b.lineTo(q, H);
                            b.lineTo(K, N);
                            b.closePath();
                            this.stereo === l.Bond.STEREO_PROTRUDING ? b.fill() : (b.save(), b.clip(), b.lineWidth = 2 * n, b.lineCap = "butt", b.beginPath(), b.moveTo(d, f), b.lineTo(h + 5 * (h - d), m + 5 * (m - f)), b.setLineDash([a.bonds_hashWidth_2D, a.bonds_hashSpacing_2D]), b.stroke(), b.setLineDash([]), b.restore())
                        }
                        break;
                    case 1.5:
                    case 2: {
                        let g = this.a1.angle(this.a2),
                            n = g + e.PI / 2,
                            c = e.cos(n),
                            k = e.sin(n),
                            v = this.a1.distance(this.a2),
                            u = a.bonds_useAbsoluteSaturationWidths_2D ? a.bonds_saturationWidthAbs_2D / 2 : v * a.bonds_saturationWidth_2D /
                            2;
                        if (this.stereo === l.Bond.STEREO_AMBIGUOUS) {
                            let a = d - c * u,
                                g = f + k * u,
                                e = d + c * u,
                                n = f - k * u,
                                v = h + c * u,
                                x = m - k * u,
                                p = h - c * u,
                                w = m + k * u;
                            b.beginPath();
                            b.moveTo(a, g);
                            b.lineTo(v, x);
                            b.moveTo(e, n);
                            b.lineTo(p, w);
                            b.stroke()
                        } else if (!a.bonds_symmetrical_2D && (this.ring || "C" === this.a1.label && "C" === this.a2.label)) {
                            b.beginPath();
                            b.moveTo(d, f);
                            b.lineTo(h, m);
                            b.stroke();
                            let n = 0;
                            u *= 2;
                            let x = a.bonds_saturationAngle_2D;
                            x < e.PI / 2 && (n = -(u / e.tan(x)));
                            if (e.abs(n) < v / 2) {
                                let v = d - e.cos(g) * n,
                                    x = h + e.cos(g) * n,
                                    p = f + e.sin(g) * n,
                                    w = m - e.sin(g) * n,
                                    l = v - c * u,
                                    t = p +
                                    k * u,
                                    z = v + c * u,
                                    q = p - k * u,
                                    y = x - c * u,
                                    C = w + k * u,
                                    A = x + c * u,
                                    B = w - k * u,
                                    D = !this.ring || this.ring.center.angle(this.a1) > this.ring.center.angle(this.a2) && !(this.ring.center.angle(this.a1) - this.ring.center.angle(this.a2) > e.PI) || this.ring.center.angle(this.a1) - this.ring.center.angle(this.a2) < -e.PI;
                                b.beginPath();
                                D ? (b.moveTo(l, t), b.lineTo(y, C)) : (b.moveTo(z, q), b.lineTo(A, B));
                                2 !== this.bondOrder && b.setLineDash([a.bonds_hashSpacing_2D, a.bonds_hashSpacing_2D]);
                                b.stroke();
                                b.setLineDash([])
                            }
                        } else {
                            let g = d - c * u,
                                e = f + k * u,
                                n = d + c * u,
                                v = f - k *
                                u,
                                x = h + c * u,
                                p = m - k * u,
                                w = h - c * u,
                                l = m + k * u;
                            b.beginPath();
                            b.moveTo(g, e);
                            b.lineTo(w, l);
                            b.stroke();
                            b.beginPath();
                            b.moveTo(n, v);
                            b.lineTo(x, p);
                            2 !== this.bondOrder && b.setLineDash([a.bonds_hashWidth_2D, a.bonds_hashSpacing_2D]);
                            b.stroke();
                            b.setLineDash([])
                        }
                        break
                    }
                    case 3: {
                        let g = a.bonds_useAbsoluteSaturationWidths_2D ? a.bonds_saturationWidthAbs_2D : this.a1.distance(this.a2) * a.bonds_saturationWidth_2D,
                            n = this.a1.angle(this.a2) + e.PI / 2,
                            c = e.cos(n),
                            k = e.sin(n),
                            v = d - c * g,
                            u = f + k * g,
                            x = d + c * g,
                            w = f - k * g,
                            l = h + c * g,
                            t = m - k * g,
                            q = h - c * g,
                            K = m + k * g;
                        b.beginPath();
                        b.moveTo(v, u);
                        b.lineTo(q, K);
                        b.moveTo(x, w);
                        b.lineTo(l, t);
                        b.moveTo(d, f);
                        b.lineTo(h, m);
                        b.stroke()
                    }
            }
        }
    };
    f.drawDecorations = function(b, a) {
        if (this.isHover || this.isSelected) {
            let d = 2 * e.PI,
                h = (this.a1.angleForStupidCanvasArcs(this.a2) + e.PI / 2) % d;
            b.strokeStyle = this.isHover ? a.colorHover : a.colorSelect;
            b.lineWidth = 1.2;
            b.beginPath();
            a = (h + e.PI) % d;
            a %= 2 * e.PI;
            b.arc(this.a1.x, this.a1.y, 7, h, a, !1);
            b.stroke();
            b.beginPath();
            h += e.PI;
            a = (h + e.PI) % d;
            b.arc(this.a2.x, this.a2.y, 7, h, a, !1);
            b.stroke()
        }
    };
    f.drawLewisStyle = function(b, a,
        d, n, f, m) {
        var g = this.a1.angle(this.a2);
        let h = g + e.PI / 2;
        f -= d;
        m -= n;
        f = e.sqrt(f * f + m * m) / (this.bondOrder + 1);
        m = f * e.cos(g);
        g = -f * e.sin(g);
        d += m;
        n += g;
        for (f = 0; f < this.bondOrder; f++) {
            var k = a.atoms_lonePairSpread_2D / 2;
            let f = d - e.cos(h) * k,
                v = n + e.sin(h) * k,
                c = d + e.cos(h) * k;
            k = n - e.sin(h) * k;
            b.beginPath();
            b.arc(f - a.atoms_lonePairDiameter_2D / 2, v - a.atoms_lonePairDiameter_2D / 2, a.atoms_lonePairDiameter_2D, 0, 2 * e.PI, !1);
            b.fill();
            b.beginPath();
            b.arc(c - a.atoms_lonePairDiameter_2D / 2, k - a.atoms_lonePairDiameter_2D / 2, a.atoms_lonePairDiameter_2D,
                0, 2 * e.PI, !1);
            b.fill();
            d += m;
            n += g
        }
    };
    f.render = function(d, a, g) {
        this.styles && (a = this.styles);
        var h = this.a1.distance3D(this.a2);
        if (0 !== h) {
            var f = a.bonds_cylinderDiameter_3D / 2,
                m = a.bonds_color,
                x = k.translate(k.identity(), [this.a1.x, this.a1.y, this.a1.z]),
                u, w = [this.a2.x - this.a1.x, this.a2.y - this.a1.y, this.a2.z - this.a1.z],
                l = [0, 1, 0],
                t = 0;
            this.a1.x === this.a2.x && this.a1.z === this.a2.z ? (l = [0, 0, 1], this.a2.y < this.a1.y && (t = e.PI)) : (t = q.vec3AngleFrom(l, w), l = b.cross(l, w, []));
            if (a.bonds_splitColor) {
                m = this.a1.styles ? this.a1.styles :
                    a;
                var c = this.a2.styles ? this.a2.styles : a;
                m = this.a1.getElementColor(m.atoms_useJMOLColors, m.atoms_usePYMOLColors, m.atoms_color);
                c = this.a2.getElementColor(c.atoms_useJMOLColors, c.atoms_usePYMOLColors, c.atoms_color);
                m != c && (u = k.translate(k.identity(), [this.a2.x, this.a2.y, this.a2.z]))
            }
            var p = [0];
            if (g) {
                if (a.bonds_showBondOrders_3D && 1 < this.bondOrder) {
                    p = [a.bonds_cylinderDiameter_3D];
                    var A = [0, 0, 1];
                    f = k.inverse(d.rotationMatrix, []);
                    k.multiplyVec3(f, A);
                    A = b.cross(w, A, []);
                    b.normalize(A)
                }
                w = 1;
                var B = a.bonds_pillSpacing_3D;
                f = a.bonds_pillHeight_3D;
                0 == this.bondOrder && (a.bonds_renderAsLines_3D ? f = B : (f = a.bonds_pillDiameter_3D, f < a.bonds_cylinderDiameter_3D && (f /= 2), w = f / 2, h /= w, B /= w / 2));
                g = f + B;
                let n = e.floor(h / g);
                h = (B + a.bonds_pillDiameter_3D + (h - g * n)) / 2;
                B = n;
                u && (B = e.floor(n / 2));
                for (let v = 0, z = p.length; v < z; v++) {
                    let z = k.set(x, []);
                    0 !== p[v] && k.translate(z, b.scale(A, p[v], []));
                    0 !== t && k.rotate(z, t, l);
                    1 != w && k.scale(z, [w, w, w]);
                    m && d.material.setDiffuseColor(d, m);
                    k.translate(z, [0, h, 0]);
                    for (var C = 0; C < B; C++) a.bonds_renderAsLines_3D ? 0 == this.bondOrder ?
                        (d.shader.setMatrixUniforms(d, z), d.drawArrays(d.POINTS, 0, 1)) : (k.scale(z, [1, f, 1]), d.shader.setMatrixUniforms(d, z), d.drawArrays(d.LINES, 0, d.lineBuffer.vertexPositionBuffer.numItems), k.scale(z, [1, 1 / f, 1])) : (d.shader.setMatrixUniforms(d, z), 0 == this.bondOrder ? d.drawElements(d.TRIANGLES, d.sphereBuffer.vertexIndexBuffer.numItems, d.UNSIGNED_SHORT, 0) : d.drawElements(d.TRIANGLES, d.pillBuffer.vertexIndexBuffer.numItems, d.UNSIGNED_SHORT, 0)), k.translate(z, [0, g, 0]);
                    if (u) {
                        let m;
                        a.bonds_renderAsLines_3D ? (C = f, C /= 2, m =
                            0) : (C = 2 / 3, m = (1 - C) / 2);
                        0 != n % 2 && (k.scale(z, [1, C, 1]), d.shader.setMatrixUniforms(d, z), a.bonds_renderAsLines_3D ? 0 == this.bondOrder ? d.drawArrays(d.POINTS, 0, 1) : d.drawArrays(d.LINES, 0, d.lineBuffer.vertexPositionBuffer.numItems) : 0 == this.bondOrder ? d.drawElements(d.TRIANGLES, d.sphereBuffer.vertexIndexBuffer.numItems, d.UNSIGNED_SHORT, 0) : d.drawElements(d.TRIANGLES, d.pillBuffer.vertexIndexBuffer.numItems, d.UNSIGNED_SHORT, 0), k.translate(z, [0, g * (1 + m), 0]), k.scale(z, [1, 1 / C, 1]));
                        k.set(u, z);
                        0 !== p[v] && k.translate(z, b.scale(A,
                            p[v], []));
                        k.rotate(z, t + e.PI, l);
                        1 != w && k.scale(z, [w, w, w]);
                        c && d.material.setDiffuseColor(d, c);
                        k.translate(z, [0, h, 0]);
                        for (let b = 0; b < B; b++) a.bonds_renderAsLines_3D ? 0 == this.bondOrder ? (d.shader.setMatrixUniforms(d, z), d.drawArrays(d.POINTS, 0, 1)) : (k.scale(z, [1, f, 1]), d.shader.setMatrixUniforms(d, z), d.drawArrays(d.LINES, 0, d.lineBuffer.vertexPositionBuffer.numItems), k.scale(z, [1, 1 / f, 1])) : (d.shader.setMatrixUniforms(d, z), 0 == this.bondOrder ? d.drawElements(d.TRIANGLES, d.sphereBuffer.vertexIndexBuffer.numItems, d.UNSIGNED_SHORT,
                            0) : d.drawElements(d.TRIANGLES, d.pillBuffer.vertexIndexBuffer.numItems, d.UNSIGNED_SHORT, 0)), k.translate(z, [0, g, 0]);
                        0 != n % 2 && (k.scale(z, [1, C, 1]), d.shader.setMatrixUniforms(d, z), a.bonds_renderAsLines_3D ? 0 == this.bondOrder ? d.drawArrays(d.POINTS, 0, 1) : d.drawArrays(d.LINES, 0, d.lineBuffer.vertexPositionBuffer.numItems) : 0 == this.bondOrder ? d.drawElements(d.TRIANGLES, d.sphereBuffer.vertexIndexBuffer.numItems, d.UNSIGNED_SHORT, 0) : d.drawElements(d.TRIANGLES, d.pillBuffer.vertexIndexBuffer.numItems, d.UNSIGNED_SHORT,
                            0), k.translate(z, [0, g * (1 + m), 0]), k.scale(z, [1, 1 / C, 1]))
                    }
                }
            } else {
                if (a.bonds_showBondOrders_3D) {
                    switch (this.bondOrder) {
                        case 1.5:
                            p = [-a.bonds_cylinderDiameter_3D];
                            break;
                        case 2:
                            p = [-a.bonds_cylinderDiameter_3D, a.bonds_cylinderDiameter_3D];
                            break;
                        case 3:
                            p = [-1.2 * a.bonds_cylinderDiameter_3D, 0, 1.2 * a.bonds_cylinderDiameter_3D]
                    }
                    1 < this.bondOrder && (A = [0, 0, 1], g = k.inverse(d.rotationMatrix, []), k.multiplyVec3(g, A), A = b.cross(w, A, []), b.normalize(A))
                } else switch (this.bondOrder) {
                    case 0:
                        f *= .25;
                        break;
                    case .5:
                    case 1.5:
                        f *= .5
                }
                u &&
                    (h /= 2);
                h = [f, h, f];
                for (let g = 0, n = p.length; g < n; g++) w = k.set(x, []), 0 !== p[g] && k.translate(w, b.scale(A, p[g], [])), 0 !== t && k.rotate(w, t, l), k.scale(w, h), m && d.material.setDiffuseColor(d, m), d.shader.setMatrixUniforms(d, w), a.bonds_renderAsLines_3D ? d.drawArrays(d.LINES, 0, d.lineBuffer.vertexPositionBuffer.numItems) : d.drawArrays(d.TRIANGLE_STRIP, 0, d.cylinderBuffer.vertexPositionBuffer.numItems), u && (k.set(u, w), 0 !== p[g] && k.translate(w, b.scale(A, p[g], [])), k.rotate(w, t + e.PI, l), k.scale(w, h), c && d.material.setDiffuseColor(d,
                    c), d.shader.setMatrixUniforms(d, w), a.bonds_renderAsLines_3D ? d.drawArrays(d.LINES, 0, d.lineBuffer.vertexPositionBuffer.numItems) : d.drawArrays(d.TRIANGLE_STRIP, 0, d.cylinderBuffer.vertexPositionBuffer.numItems))
            }
        }
    };
    f.renderHighlight = function(d, a) {
        if (this.isSelected || this.isHover) {
            this.styles && (a = this.styles);
            this.styles && (a = this.styles);
            let n = this.a1.distance3D(this.a2);
            if (0 !== n) {
                var g = a.bonds_cylinderDiameter_3D / 1.2,
                    h = k.translate(k.identity(), [this.a1.x, this.a1.y, this.a1.z]),
                    f = [this.a2.x - this.a1.x, this.a2.y -
                        this.a1.y, this.a2.z - this.a1.z
                    ],
                    m = [0, 1, 0],
                    x = 0;
                this.a1.x === this.a2.x && this.a1.z === this.a2.z ? (f = [0, 0, 1], this.a2.y < this.a1.y && (x = e.PI)) : (x = q.vec3AngleFrom(m, f), f = b.cross(m, f, []));
                g = [g, n, g];
                0 !== x && k.rotate(h, x, f);
                k.scale(h, g);
                d.shader.setMatrixUniforms(d, h);
                d.material.setDiffuseColor(d, this.isHover ? a.colorHover : a.colorSelect);
                d.drawArrays(d.TRIANGLE_STRIP, 0, d.cylinderBuffer.vertexPositionBuffer.numItems)
            }
        }
    };
    f.renderPicker = function(d, a) {
        this.styles && (a = this.styles);
        var g = this.a1.distance3D(this.a2);
        if (0 !==
            g) {
            var h = a.bonds_cylinderDiameter_3D / 2,
                f = k.translate(k.identity(), [this.a1.x, this.a1.y, this.a1.z]),
                m = [this.a2.x - this.a1.x, this.a2.y - this.a1.y, this.a2.z - this.a1.z],
                x = [0, 1, 0],
                u = 0;
            this.a1.x === this.a2.x && this.a1.z === this.a2.z ? (x = [0, 0, 1], this.a2.y < this.a1.y && (u = e.PI)) : (u = q.vec3AngleFrom(x, m), x = b.cross(x, m, []));
            var w = [0];
            if (a.bonds_showBondOrders_3D)
                if (a.bonds_renderAsLines_3D) {
                    switch (this.bondOrder) {
                        case 1.5:
                        case 2:
                            w = [-a.bonds_cylinderDiameter_3D, a.bonds_cylinderDiameter_3D];
                            break;
                        case 3:
                            w = [-1.2 * a.bonds_cylinderDiameter_3D,
                                0, 1.2 * a.bonds_cylinderDiameter_3D
                            ]
                    }
                    if (1 < this.bondOrder) {
                        var l = [0, 0, 1];
                        let a = k.inverse(d.rotationMatrix, []);
                        k.multiplyVec3(a, l);
                        l = b.cross(m, l, []);
                        b.normalize(l)
                    }
                } else switch (this.bondOrder) {
                    case 1.5:
                    case 2:
                        h *= 3;
                        break;
                    case 3:
                        h *= 3.4
                } else switch (this.bondOrder) {
                    case 0:
                        h *= .25;
                        break;
                    case .5:
                    case 1.5:
                        h *= .5
                }
            g = [h, g, h];
            for (let e = 0, c = w.length; e < c; e++) h = k.set(f, []), 0 !== w[e] && k.translate(h, b.scale(l, w[e], [])), 0 !== u && k.rotate(h, u, x), k.scale(h, g), d.shader.setMatrixUniforms(d, h), a.bonds_renderAsLines_3D ? d.drawArrays(d.LINES,
                0, d.lineBuffer.vertexPositionBuffer.numItems) : d.drawArrays(d.TRIANGLE_STRIP, 0, d.cylinderBuffer.vertexPositionBuffer.numItems)
        }
    }
})(ChemDoodle.ELEMENT, ChemDoodle.extensions, ChemDoodle.structures, ChemDoodle.math, Math, ChemDoodle.lib.mat4, ChemDoodle.lib.vec3);
(function(f, q, l) {
    f.Ring = function() {
        this.atoms = [];
        this.bonds = []
    };
    let t = f.Ring.prototype;
    t.center = l;
    t.setupBonds = function() {
        for (let e = 0, f = this.bonds.length; e < f; e++) this.bonds[e].ring = this;
        this.center = this.getCenter()
    };
    t.getCenter = function() {
        let e = Infinity,
            k = Infinity,
            b = -Infinity,
            d = -Infinity;
        for (let h = 0, a = this.atoms.length; h < a; h++) e = q.min(this.atoms[h].x, e), k = q.min(this.atoms[h].y, k), b = q.max(this.atoms[h].x, b), d = q.max(this.atoms[h].y, d);
        return new f.Point((b + e) / 2, (d + k) / 2)
    }
})(ChemDoodle.structures, Math);
(function(f, q, l, t, e, k) {
    l.Molecule = function() {
        this.atoms = [];
        this.bonds = [];
        this.rings = []
    };
    let b = l.Molecule.prototype;
    b.findRings = !0;
    b.draw = function(b, h) {
        this.styles && (h = this.styles);
        if (h.atoms_display && !h.atoms_circles_2D)
            for (let a = 0, d = this.atoms.length; a < d; a++) this.atoms[a].draw(b, h);
        if (h.bonds_display)
            for (let a = 0, d = this.bonds.length; a < d; a++) this.bonds[a].draw(b, h);
        if (h.atoms_display)
            for (let a = 0, d = this.atoms.length; a < d; a++) {
                let d = this.atoms[a];
                h.atoms_circles_2D && d.draw(b, h);
                d.query && d.query.draw(b,
                    h, d)
            }
    };
    b.render = function(b, h) {
        this.styles && (h = this.styles);
        var a = 0 < this.atoms.length && this.atoms[0].hetatm !== k;
        if (a) {
            if (h.macro_displayBonds) {
                0 < this.bonds.length && (h.bonds_renderAsLines_3D && !this.residueSpecs || this.residueSpecs && this.residueSpecs.bonds_renderAsLines_3D ? (b.lineWidth(this.residueSpecs ? this.residueSpecs.bonds_width_2D : h.bonds_width_2D), b.lineBuffer.bindBuffers(b)) : b.cylinderBuffer.bindBuffers(b), b.material.setTempColors(b, h.bonds_materialAmbientColor_3D, k, h.bonds_materialSpecularColor_3D,
                    h.bonds_materialShininess_3D));
                for (let a = 0, g = this.bonds.length; a < g; a++) {
                    var d = this.bonds[a];
                    !d.a1.hetatm && (-1 === h.macro_atomToLigandDistance || d.a1.closestDistance !== k && h.macro_atomToLigandDistance >= d.a1.closestDistance && h.macro_atomToLigandDistance >= d.a2.closestDistance) && d.render(b, this.residueSpecs ? this.residueSpecs : h)
                }
            }
            if (h.macro_displayAtoms) {
                0 < this.atoms.length && (b.sphereBuffer.bindBuffers(b), b.material.setTempColors(b, h.atoms_materialAmbientColor_3D, k, h.atoms_materialSpecularColor_3D, h.atoms_materialShininess_3D));
                for (let a = 0, g = this.atoms.length; a < g; a++) d = this.atoms[a], !d.hetatm && (-1 === h.macro_atomToLigandDistance || d.closestDistance !== k && h.macro_atomToLigandDistance >= d.closestDistance) && d.render(b, this.residueSpecs ? this.residueSpecs : h)
            }
        }
        if (h.bonds_display) {
            d = [];
            var e = [];
            0 < this.bonds.length && (h.bonds_renderAsLines_3D ? (b.lineWidth(h.bonds_width_2D), b.lineBuffer.bindBuffers(b)) : b.cylinderBuffer.bindBuffers(b), b.material.setTempColors(b, h.bonds_materialAmbientColor_3D, k, h.bonds_materialSpecularColor_3D, h.bonds_materialShininess_3D));
            for (let g = 0, f = this.bonds.length; g < f; g++) {
                let f = this.bonds[g];
                if (!a || f.a1.hetatm) h.bonds_showBondOrders_3D ? 0 == f.bondOrder ? e.push(f) : .5 == f.bondOrder ? d.push(f) : (1.5 == f.bondOrder && d.push(f), f.render(b, h)) : f.render(b, h)
            }
            if (0 < d.length) {
                h.bonds_renderAsLines_3D || b.pillBuffer.bindBuffers(b);
                for (let a = 0, g = d.length; a < g; a++) d[a].render(b, h, !0)
            }
            if (0 < e.length) {
                h.bonds_renderAsLines_3D || b.sphereBuffer.bindBuffers(b);
                for (let a = 0, d = e.length; a < d; a++) e[a].render(b, h, !0)
            }
        }
        if (h.atoms_display) {
            for (let a = 0, b = this.atoms.length; a <
                b; a++) d = this.atoms[a], d.bondNumber = 0, d.renderAsStar = !1;
            for (let a = 0, b = this.bonds.length; a < b; a++) d = this.bonds[a], d.a1.bondNumber++, d.a2.bondNumber++;
            0 < this.atoms.length && (b.sphereBuffer.bindBuffers(b), b.material.setTempColors(b, h.atoms_materialAmbientColor_3D, k, h.atoms_materialSpecularColor_3D, h.atoms_materialShininess_3D));
            d = [];
            for (let g = 0, f = this.atoms.length; g < f; g++)
                if (e = this.atoms[g], !a || e.hetatm && (h.macro_showWater || !e.isWater)) h.atoms_nonBondedAsStars_3D && 0 === e.bondNumber ? (e.renderAsStar = !0, d.push(e)) :
                    e.render(b, h);
            if (0 < d.length) {
                b.starBuffer.bindBuffers(b);
                for (let a = 0, g = d.length; a < g; a++) d[a].render(b, h)
            }
        }
        if (this.chains) {
            b.shader.setMatrixUniforms(b);
            if (h.proteins_displayRibbon) {
                b.material.setTempColors(b, h.proteins_materialAmbientColor_3D, k, h.proteins_materialSpecularColor_3D, h.proteins_materialShininess_3D);
                a = h.proteins_ribbonCartoonize ? this.cartoons : this.ribbons;
                for (let g = 0, f = a.length; g < f; g++)
                    if (d = a[g], "none" !== h.proteins_residueColor) {
                        d.front.bindBuffers(b);
                        e = "rainbow" === h.proteins_residueColor;
                        for (let a = 0, g = d.front.segments.length; a < g; a++) e && b.material.setDiffuseColor(b, q.rainbowAt(a, g, h.macro_rainbowColors)), d.front.segments[a].render(b, h);
                        d.back.bindBuffers(b);
                        for (let a = 0, g = d.back.segments.length; a < g; a++) e && b.material.setDiffuseColor(b, q.rainbowAt(a, g, h.macro_rainbowColors)), d.back.segments[a].render(b, h)
                    } else d.front.render(b, h), d.back.render(b, h)
            }
            if (h.proteins_displayPipePlank)
                for (let a = 0, d = this.pipePlanks.length; a < d; a++) this.pipePlanks[a].render(b, h);
            if (h.proteins_displayBackbone) {
                if (!this.alphaCarbonTrace) {
                    this.alphaCarbonTrace = {
                        nodes: [],
                        edges: []
                    };
                    for (let b = 0, g = this.chains.length; b < g; b++)
                        if (a = this.chains[b], !(2 < a.length && t[a[2].name] && "#BEA06E" === t[a[2].name].aminoColor) && 0 < a.length)
                            for (let b = 0, g = a.length - 2; b < g; b++) d = a[b].cp1, d.chainColor = a.chainColor, this.alphaCarbonTrace.nodes.push(d), d = new l.Bond(a[b].cp1, a[b + 1].cp1), d.residueName = a[b].name, d.chainColor = a.chainColor, this.alphaCarbonTrace.edges.push(d), b === a.length - 3 && (d = a[b + 1].cp1, d.chainColor = a.chainColor, this.alphaCarbonTrace.nodes.push(d))
                }
                if (0 < this.alphaCarbonTrace.nodes.length) {
                    a =
                        new l.Styles;
                    a.atoms_display = !0;
                    a.bonds_display = !0;
                    a.atoms_sphereDiameter_3D = h.proteins_backboneThickness;
                    a.bonds_cylinderDiameter_3D = h.proteins_backboneThickness;
                    a.bonds_splitColor = !1;
                    a.atoms_color = h.proteins_backboneColor;
                    a.bonds_color = h.proteins_backboneColor;
                    a.atoms_useVDWDiameters_3D = !1;
                    b.material.setTempColors(b, h.proteins_materialAmbientColor_3D, k, h.proteins_materialSpecularColor_3D, h.proteins_materialShininess_3D);
                    b.material.setDiffuseColor(b, h.proteins_backboneColor);
                    for (let g = 0, e = this.alphaCarbonTrace.nodes.length; g <
                        e; g++) d = this.alphaCarbonTrace.nodes[g], h.macro_colorByChain && (a.atoms_color = d.chainColor), b.sphereBuffer.bindBuffers(b), d.render(b, a);
                    for (let g = 0, n = this.alphaCarbonTrace.edges.length; g < n; g++) {
                        d = this.alphaCarbonTrace.edges[g];
                        var f;
                        e = t[d.residueName] ? t[d.residueName] : t["*"];
                        h.macro_colorByChain ? f = d.chainColor : "shapely" === h.proteins_residueColor ? f = e.shapelyColor : "amino" === h.proteins_residueColor ? f = e.aminoColor : "polarity" === h.proteins_residueColor ? f = e.polar ? "#C10000" : "#FFFFFF" : "acidity" === h.proteins_residueColor ?
                            f = 1 === e.acidity ? "#0000FF" : -1 === e.acidity ? "#FF0000" : e.polar ? "#FFFFFF" : "#773300" : "rainbow" === h.proteins_residueColor && (f = q.rainbowAt(g, n, h.macro_rainbowColors));
                        f && (a.bonds_color = f);
                        b.cylinderBuffer.bindBuffers(b);
                        d.render(b, a)
                    }
                }
            }
            if (h.nucleics_display) {
                b.material.setTempColors(b, h.nucleics_materialAmbientColor_3D, k, h.nucleics_materialSpecularColor_3D, h.nucleics_materialShininess_3D);
                for (let a = 0, d = this.tubes.length; a < d; a++) b.shader.setMatrixUniforms(b), this.tubes[a].render(b, h)
            }
        }
        if (h.atoms_display) {
            f = !1;
            for (let b = 0, d = this.atoms.length; b < d; b++)
                if (a = this.atoms[b], a.isHover || a.isSelected) {
                    f = !0;
                    break
                } if (!f)
                for (let b = 0, d = this.bonds.length; b < d; b++)
                    if (a = this.bonds[b], a.isHover || a.isSelected) {
                        f = !0;
                        break
                    } if (f) {
                b.sphereBuffer.bindBuffers(b);
                b.blendFunc(b.SRC_ALPHA, b.ONE);
                b.material.setTempColors(b, h.atoms_materialAmbientColor_3D, k, "#000000", 0);
                b.enable(b.BLEND);
                b.depthMask(!1);
                b.material.setAlpha(b, .4);
                b.sphereBuffer.bindBuffers(b);
                for (let a = 0, d = this.atoms.length; a < d; a++) f = this.atoms[a], (f.isHover || f.isSelected) &&
                    f.renderHighlight(b, h);
                b.cylinderBuffer.bindBuffers(b);
                for (let a = 0, d = this.bonds.length; a < d; a++) f = this.bonds[a], (f.isHover || f.isSelected) && f.renderHighlight(b, h);
                b.depthMask(!0);
                b.disable(b.BLEND);
                b.blendFuncSeparate(b.SRC_ALPHA, b.ONE_MINUS_SRC_ALPHA, b.ONE, b.ONE_MINUS_SRC_ALPHA)
            }
        }
    };
    b.renderPickFrame = function(b, h, a, g, e) {
        this.styles && (h = this.styles);
        var d = 0 < this.atoms.length && this.atoms[0].hetatm !== k;
        if (e && h.bonds_display) {
            0 < this.bonds.length && (h.bonds_renderAsLines_3D ? (b.lineWidth(h.bonds_width_2D),
                b.lineBuffer.bindBuffers(b)) : b.cylinderBuffer.bindBuffers(b));
            for (let g = 0, f = this.bonds.length; g < f; g++)
                if (e = this.bonds[g], !d || e.a1.hetatm) b.material.setDiffuseColor(b, q.idx2color(a.length)), e.renderPicker(b, h), a.push(e)
        }
        if (g && h.atoms_display) {
            for (let a = 0, b = this.atoms.length; a < b; a++) g = this.atoms[a], g.bondNumber = 0, g.renderAsStar = !1;
            for (let a = 0, b = this.bonds.length; a < b; a++) g = this.bonds[a], g.a1.bondNumber++, g.a2.bondNumber++;
            0 < this.atoms.length && b.sphereBuffer.bindBuffers(b);
            g = [];
            for (let f = 0, n = this.atoms.length; f <
                n; f++)
                if (e = this.atoms[f], !d || e.hetatm && (h.macro_showWater || !e.isWater)) h.atoms_nonBondedAsStars_3D && 0 === e.bondNumber ? (e.renderAsStar = !0, g.push(e)) : (b.material.setDiffuseColor(b, q.idx2color(a.length)), e.render(b, h, !0), a.push(e));
            if (0 < g.length) {
                b.starBuffer.bindBuffers(b);
                for (let e = 0, f = g.length; e < f; e++) d = g[e], b.material.setDiffuseColor(b, q.idx2color(a.length)), d.render(b, h, !0), a.push(d)
            }
        }
    };
    b.getCenter3D = function() {
        if (1 === this.atoms.length) return new l.Atom("C", this.atoms[0].x, this.atoms[0].y, this.atoms[0].z);
        let b = Infinity,
            h = Infinity,
            a = Infinity,
            g = -Infinity,
            f = -Infinity,
            k = -Infinity;
        if (this.chains)
            for (let d = 0, n = this.chains.length; d < n; d++) {
                let n = this.chains[d];
                for (let d = 0, m = n.length; d < m; d++) {
                    let m = n[d];
                    b = e.min(m.cp1.x, m.cp2.x, b);
                    h = e.min(m.cp1.y, m.cp2.y, h);
                    a = e.min(m.cp1.z, m.cp2.z, a);
                    g = e.max(m.cp1.x, m.cp2.x, g);
                    f = e.max(m.cp1.y, m.cp2.y, f);
                    k = e.max(m.cp1.z, m.cp2.z, k)
                }
            }
        for (let d = 0, n = this.atoms.length; d < n; d++) b = e.min(this.atoms[d].x, b), h = e.min(this.atoms[d].y, h), a = e.min(this.atoms[d].z, a), g = e.max(this.atoms[d].x,
            g), f = e.max(this.atoms[d].y, f), k = e.max(this.atoms[d].z, k);
        return new l.Atom("C", (g + b) / 2, (f + h) / 2, (k + a) / 2)
    };
    b.getCenter = function() {
        if (1 === this.atoms.length) return new l.Point(this.atoms[0].x, this.atoms[0].y);
        let b = Infinity,
            h = Infinity,
            a = -Infinity,
            g = -Infinity;
        for (let d = 0, f = this.atoms.length; d < f; d++) b = e.min(this.atoms[d].x, b), h = e.min(this.atoms[d].y, h), a = e.max(this.atoms[d].x, a), g = e.max(this.atoms[d].y, g);
        return new l.Point((a + b) / 2, (g + h) / 2)
    };
    b.getDimension = function() {
        if (1 === this.atoms.length) return new l.Point(0,
            0);
        let b = Infinity,
            h = Infinity,
            a = -Infinity,
            g = -Infinity;
        if (this.chains) {
            for (let d = 0, f = this.chains.length; d < f; d++) {
                let f = this.chains[d];
                for (let d = 0, n = f.length; d < n; d++) {
                    let n = f[d];
                    b = e.min(n.cp1.x, n.cp2.x, b);
                    h = e.min(n.cp1.y, n.cp2.y, h);
                    a = e.max(n.cp1.x, n.cp2.x, a);
                    g = e.max(n.cp1.y, n.cp2.y, g)
                }
            }
            b -= 30;
            h -= 30;
            a += 30;
            g += 30
        }
        for (let d = 0, f = this.atoms.length; d < f; d++) b = e.min(this.atoms[d].x, b), h = e.min(this.atoms[d].y, h), a = e.max(this.atoms[d].x, a), g = e.max(this.atoms[d].y, g);
        return new l.Point(a - b, g - h)
    };
    b.check = function(b) {
        if (b &&
            this.doChecks) {
            if (this.findRings)
                if (this.bonds.length - this.atoms.length !== this.fjNumCache) {
                    this.rings = (new f.informatics.SSSRFinder(this)).rings;
                    for (let a = 0, b = this.bonds.length; a < b; a++) this.bonds[a].ring = k;
                    for (let a = 0, b = this.rings.length; a < b; a++) this.rings[a].setupBonds()
                } else
                    for (let a = 0, b = this.rings.length; a < b; a++) {
                        var d = this.rings[a];
                        d.center = d.getCenter()
                    }
            for (let a = 0, b = this.atoms.length; a < b; a++)
                if (this.atoms[a].isLone = !1, "C" === this.atoms[a].label) {
                    d = 0;
                    for (let b = 0, g = this.bonds.length; b < g; b++) this.bonds[b].a1 !==
                        this.atoms[a] && this.bonds[b].a2 !== this.atoms[a] || d++;
                    0 === d && (this.atoms[a].isLone = !0)
                } d = !1;
            for (let a = 0, b = this.atoms.length; a < b; a++) 0 !== this.atoms[a].z && (d = !0);
            d && (this.sortAtomsByZ(), this.sortBondsByZ());
            this.setupMetaData();
            this.atomNumCache = this.atoms.length;
            this.bondNumCache = this.bonds.length;
            this.fjNumCache = this.bonds.length - this.atoms.length
        }
        this.doChecks = !b
    };
    b.getAngles = function(b) {
        let d = [];
        for (let a = 0, g = this.bonds.length; a < g; a++) this.bonds[a].contains(b) && d.push(b.angle(this.bonds[a].getNeighbor(b)));
        d.sort(function(a, b) {
            return a - b
        });
        return d
    };
    b.getCoordinationNumber = function(b) {
        let d = 0;
        for (let a = 0, g = b.length; a < g; a++) d += b[a].bondOrder;
        return d
    };
    b.getBonds = function(b) {
        let d = [];
        for (let a = 0, g = this.bonds.length; a < g; a++) this.bonds[a].contains(b) && d.push(this.bonds[a]);
        return d
    };
    b.sortAtomsByZ = function() {
        for (let b = 1, e = this.atoms.length; b < e; b++) {
            let a = b;
            for (; 0 < a && this.atoms[a].z < this.atoms[a - 1].z;) {
                let b = this.atoms[a];
                this.atoms[a] = this.atoms[a - 1];
                this.atoms[a - 1] = b;
                a--
            }
        }
    };
    b.sortBondsByZ = function() {
        for (let b =
                1, e = this.bonds.length; b < e; b++) {
            let a = b;
            for (; 0 < a && this.bonds[a].a1.z + this.bonds[a].a2.z < this.bonds[a - 1].a1.z + this.bonds[a - 1].a2.z;) {
                let b = this.bonds[a];
                this.bonds[a] = this.bonds[a - 1];
                this.bonds[a - 1] = b;
                a--
            }
        }
    };
    b.setupMetaData = function() {
        let b = this.getCenter();
        for (let d = 0, a = this.atoms.length; d < a; d++) {
            let a = this.atoms[d];
            a.bonds = this.getBonds(a);
            a.angles = this.getAngles(a);
            a.isHidden = 2 === a.bonds.length && e.abs(e.abs(a.angles[1] - a.angles[0]) - e.PI) < e.PI / 30 && a.bonds[0].bondOrder === a.bonds[1].bondOrder;
            let h =
                q.angleBetweenLargest(a.angles);
            a.angleOfLeastInterference = h.angle % (2 * e.PI);
            a.largestAngle = h.largest;
            a.coordinationNumber = this.getCoordinationNumber(a.bonds);
            a.bondNumber = a.bonds.length;
            a.molCenter = b
        }
        for (let d = 0, a = this.bonds.length; d < a; d++) this.bonds[d].molCenter = b
    };
    b.scaleToAverageBondLength = function(b) {
        let d = this.getAverageBondLength();
        if (0 !== d) {
            b /= d;
            for (let a = 0, d = this.atoms.length; a < d; a++) this.atoms[a].x *= b, this.atoms[a].y *= b
        }
    };
    b.getAverageBondLength = function() {
        if (0 === this.bonds.length) return 0;
        let b = 0;
        for (let d = 0, a = this.bonds.length; d < a; d++) b += this.bonds[d].getLength();
        return b /= this.bonds.length
    };
    b.getBounds = function() {
        let b = new q.Bounds;
        for (let d = 0, a = this.atoms.length; d < a; d++) b.expand(this.atoms[d].getBounds());
        if (this.chains) {
            for (let d = 0, a = this.chains.length; d < a; d++) {
                let a = this.chains[d];
                for (let d = 0, g = a.length; d < g; d++) {
                    let g = a[d];
                    b.expand(g.cp1.x, g.cp1.y);
                    b.expand(g.cp2.x, g.cp2.y)
                }
            }
            b.minX -= 30;
            b.minY -= 30;
            b.maxX += 30;
            b.maxY += 30
        }
        return b
    };
    b.getBounds3D = function() {
        let b = new q.Bounds;
        for (let d =
                0, a = this.atoms.length; d < a; d++) b.expand(this.atoms[d].getBounds3D());
        if (this.chains)
            for (let d = 0, a = this.chains.length; d < a; d++) {
                let a = this.chains[d];
                for (let d = 0, g = a.length; d < g; d++) {
                    let g = a[d];
                    b.expand3D(g.cp1.x, g.cp1.y, g.cp1.z);
                    b.expand3D(g.cp2.x, g.cp2.y, g.cp2.z)
                }
            }
        return b
    };
    b.getAtomGroup = function(b) {
        let d = !1;
        for (let a = 0, b = this.atoms.length; a < b; a++) this.atoms[a].visited = !1;
        for (let g = 0, e = this.bonds.length; g < e; g++) {
            var a = this.bonds[g];
            !d && a.contains(b) && a.ring !== k && (d = !0)
        }
        if (!d) return k;
        a = [b];
        b.visited = !0;
        let g = new l.Queue;
        for (g.enqueue(b); !g.isEmpty();) {
            b = g.dequeue();
            for (let h = 0, f = this.bonds.length; h < f; h++) {
                var e = this.bonds[h];
                e.contains(b) && d === (e.ring !== k) && (e = e.getNeighbor(b), e.visited || (e.visited = !0, a.push(e), g.enqueue(e)))
            }
        }
        return a
    };
    b.getBondGroup = function(b) {
        let d = b.ring !== k;
        var a = !1;
        for (let d = 0, e = this.bonds.length; d < e; d++) {
            var g = this.bonds[d];
            g === b && (a = !0);
            g.visited = !1
        }
        if (!a) return k;
        a = [b];
        b.visited = !0;
        g = new l.Queue;
        for (g.enqueue(b); !g.isEmpty();) {
            b = g.dequeue();
            for (let e = 0, h = this.bonds.length; e <
                h; e++) {
                let h = this.bonds[e];
                h.visited || h.a1 !== b.a1 && h.a2 !== b.a1 && h.a1 !== b.a2 && h.a2 !== b.a2 || h.ring !== k !== d || (h.visited = !0, a.push(h), g.enqueue(h))
            }
        }
        return a
    }
})(ChemDoodle, ChemDoodle.math, ChemDoodle.structures, ChemDoodle.RESIDUE, Math);
(function(f, q, l, t, e) {
    let k, b = -1;
    f.Residue = function(b) {
        this.resSeq = b
    };
    e = f.Residue.prototype;
    e.setup = function(b, e) {
        this.horizontalResolution = e;
        let a = [b.x - this.cp1.x, b.y - this.cp1.y, b.z - this.cp1.z];
        var d = t.cross(a, [this.cp2.x - this.cp1.x, this.cp2.y - this.cp1.y, this.cp2.z - this.cp1.z], []);
        this.D = t.cross(d, a, []);
        t.normalize(d);
        t.normalize(this.D);
        this.guidePointsSmall = [];
        this.guidePointsLarge = [];
        b = [(b.x + this.cp1.x) / 2, (b.y + this.cp1.y) / 2, (b.z + this.cp1.z) / 2];
        this.helix && (t.scale(d, 1.5), t.add(b, d));
        this.guidePointsSmall[0] =
            new f.Atom("", b[0] - this.D[0] / 2, b[1] - this.D[1] / 2, b[2] - this.D[2] / 2);
        for (d = 1; d < e; d++) this.guidePointsSmall[d] = new f.Atom("", this.guidePointsSmall[0].x + this.D[0] * d / e, this.guidePointsSmall[0].y + this.D[1] * d / e, this.guidePointsSmall[0].z + this.D[2] * d / e);
        t.scale(this.D, 4);
        this.guidePointsLarge[0] = new f.Atom("", b[0] - this.D[0] / 2, b[1] - this.D[1] / 2, b[2] - this.D[2] / 2);
        for (d = 1; d < e; d++) this.guidePointsLarge[d] = new f.Atom("", this.guidePointsLarge[0].x + this.D[0] * d / e, this.guidePointsLarge[0].y + this.D[1] * d / e, this.guidePointsLarge[0].z +
            this.D[2] * d / e)
    };
    e.getGuidePointSet = function(b) {
        if (0 === b) return this.helix || this.sheet ? this.guidePointsLarge : this.guidePointsSmall;
        if (1 === b) return this.guidePointsSmall;
        if (2 === b) return this.guidePointsLarge
    };
    e.computeLineSegments = function(b, e, a, g, f) {
        this.setVerticalResolution(f);
        this.split = a.helix !== this.helix || a.sheet !== this.sheet;
        this.lineSegments = this.innerCompute(0, b, e, a, !1, f);
        g && (this.lineSegmentsCartoon = this.innerCompute(this.helix || this.sheet ? 2 : 1, b, e, a, !0, f))
    };
    e.innerCompute = function(b, e, a,
        g, n, v) {
        let d = [];
        var h = this.getGuidePointSet(b);
        e = e.getGuidePointSet(b);
        a = a.getGuidePointSet(b);
        b = g.getGuidePointSet(b);
        for (let n = 0, m = h.length; n < m; n++) {
            g = l.multiply([e[n].x, e[n].y, e[n].z, 1, a[n].x, a[n].y, a[n].z, 1, h[n].x, h[n].y, h[n].z, 1, b[n].x, b[n].y, b[n].z, 1], k, []);
            let m = [];
            for (let a = 0; a < v; a++) {
                for (let a = 3; 0 < a; a--)
                    for (let b = 0; 4 > b; b++) g[4 * a + b] += g[4 * (a - 1) + b];
                m[a] = new f.Atom("", g[12] / g[15], g[13] / g[15], g[14] / g[15])
            }
            d[n] = m
        }
        if (n && this.arrow)
            for (let f = 0, m = v; f < m; f++) {
                n = 1.5 - 1.3 * f / v;
                h = q.floor(this.horizontalResolution /
                    2);
                e = d[h];
                for (let m = 0, k = d.length; m < k; m++) m !== h && (a = e[f], b = d[m][f], g = [b.x - a.x, b.y - a.y, b.z - a.z], t.scale(g, n), b.x = a.x + g[0], b.y = a.y + g[1], b.z = a.z + g[2])
            }
        return d
    };
    e.setVerticalResolution = function(d) {
        if (d !== b) {
            {
                let e = d * d,
                    a = d * d * d;
                k = l.multiply([-1 / 6, .5, -.5, 1 / 6, .5, -1, .5, 0, -.5, 0, .5, 0, 1 / 6, 2 / 3, 1 / 6, 0], [6 / a, 0, 0, 0, 6 / a, 2 / e, 0, 0, 1 / a, 1 / e, 1 / d, 0, 0, 0, 0, 1], []);
                b = d
            }
        }
    }
})(ChemDoodle.structures, Math, ChemDoodle.lib.mat4, ChemDoodle.lib.vec3);
(function(f, q, l, t, e, k) {
    q.Spectrum = function() {
        this.data = [];
        this.metadata = [];
        this.dataDisplay = [];
        this.memory = {
            offsetTop: 0,
            offsetLeft: 0,
            offsetBottom: 0,
            flipXAxis: !1,
            scale: 1,
            width: 0,
            height: 0
        }
    };
    t = q.Spectrum.prototype;
    t.title = k;
    t.xUnit = k;
    t.yUnit = k;
    t.continuous = !0;
    t.integrationSensitivity = .01;
    t.draw = function(b, d, h, a) {
        this.styles && (d = this.styles);
        let g = 5,
            n = 0,
            k = 0;
        b.fillStyle = d.text_color;
        b.textAlign = "center";
        b.textBaseline = "alphabetic";
        b.font = f.getFontString(d.text_font_size, d.text_font_families);
        this.xUnit &&
            (k += d.text_font_size, b.fillText(this.xUnit, h / 2, a - 2));
        this.yUnit && d.plots_showYAxis && (n += d.text_font_size, b.save(), b.translate(d.text_font_size, a / 2), b.rotate(-e.PI / 2), b.fillText(this.yUnit, 0, 0), b.restore());
        this.title && (g += d.text_font_size, b.fillText(this.title, h / 2, d.text_font_size));
        b.lineCap = "square";
        k += 5 + d.text_font_size;
        d.plots_showYAxis && (n += 5 + b.measureText("1000").width);
        d.plots_showGrid && (b.strokeStyle = d.plots_gridColor, b.lineWidth = d.plots_gridLineWidth, b.strokeRect(n, g, h - n, a - k - g));
        b.textAlign =
            "center";
        b.textBaseline = "top";
        for (var m = this.maxX - this.minX, l = m / 100, u = .001; u < l || 25 < m / u;) u *= 10;
        m = 0;
        l = d.plots_flipXAxis ? h : 0;
        for (var w = e.round(this.minX / u) * u; w <= this.maxX; w += u / 2) {
            var t = this.getTransformedX(w, d, h, n);
            if (t > n)
                if (b.strokeStyle = "black", b.lineWidth = 1, 0 === m % 2) {
                    b.beginPath();
                    b.moveTo(t, a - k);
                    b.lineTo(t, a - k + 2);
                    b.stroke();
                    let e = w.toFixed(5);
                    for (;
                        "0" === e.charAt(e.length - 1);) e = e.substring(0, e.length - 1);
                    "." === e.charAt(e.length - 1) && (e = e.substring(0, e.length - 1));
                    let c = b.measureText(e).width;
                    d.plots_flipXAxis &&
                        (c *= -1);
                    let h = t - c / 2;
                    if (d.plots_flipXAxis ? h < l : h > l) b.fillText(e, t, a - k + 2), l = t + c / 2;
                    d.plots_showGrid && (b.strokeStyle = d.plots_gridColor, b.lineWidth = d.plots_gridLineWidth, b.beginPath(), b.moveTo(t, a - k), b.lineTo(t, g), b.stroke())
                } else b.beginPath(), b.moveTo(t, a - k), b.lineTo(t, a - k + 2), b.stroke();
            m++
        }
        if (d.plots_showYAxis || d.plots_showGrid)
            for (u = 1 / d.scale, b.textAlign = "right", b.textBaseline = "middle", m = 0; 10 >= m; m++)
                if (w = u / 10 * m, l = g + (a - k - g) * (1 - w * d.scale), d.plots_showGrid && (b.strokeStyle = d.plots_gridColor, b.lineWidth =
                        d.plots_gridLineWidth, b.beginPath(), b.moveTo(n, l), b.lineTo(h, l), b.stroke()), d.plots_showYAxis) {
                    b.strokeStyle = "black";
                    b.lineWidth = 1;
                    b.beginPath();
                    b.moveTo(n, l);
                    b.lineTo(n - 3, l);
                    b.stroke();
                    t = 100 * w;
                    w = e.max(0, 3 - e.floor(t).toString().length);
                    t = t.toFixed(w);
                    if (0 < w)
                        for (;
                            "0" === t.charAt(t.length - 1);) t = t.substring(0, t.length - 1);
                    "." === t.charAt(t.length - 1) && (t = t.substring(0, t.length - 1));
                    b.fillText(t, n - 3, l)
                } b.strokeStyle = "black";
        b.lineWidth = 1;
        b.beginPath();
        b.moveTo(h, a - k);
        b.lineTo(n, a - k);
        d.plots_showYAxis && b.lineTo(n,
            g);
        b.stroke();
        if (0 < this.dataDisplay.length) {
            b.textAlign = "left";
            b.textBaseline = "top";
            u = 0;
            for (let a = 0, c = this.dataDisplay.length; a < c; a++)
                if (this.dataDisplay[a].value) b.fillText([this.dataDisplay[a].display, ": ", this.dataDisplay[a].value].join(""), n + 10, g + 10 + u * (d.text_font_size + 5)), u++;
                else if (this.dataDisplay[a].tag)
                for (let c = 0, e = this.metadata.length; c < e; c++)
                    if (this.metadata[c].startsWith(this.dataDisplay[a].tag)) {
                        m = this.metadata[c];
                        this.dataDisplay[a].display && (m = this.metadata[c].indexOf("\x3d"), m = [this.dataDisplay[a].display,
                            ": ", -1 < m ? this.metadata[c].substring(m + 2) : this.metadata[c]
                        ].join(""));
                        b.fillText(m, n + 10, g + 10 + u * (d.text_font_size + 5));
                        u++;
                        break
                    }
        }
        this.drawPlot(b, d, h, a, g, n, k);
        this.memory.offsetTop = g;
        this.memory.offsetLeft = n;
        this.memory.offsetBottom = k;
        this.memory.flipXAxis = d.plots_flipXAxis;
        this.memory.scale = d.scale;
        this.memory.width = h;
        this.memory.height = a
    };
    t.drawPlot = function(b, d, h, a, g, f, v) {
        this.styles && (d = this.styles);
        b.strokeStyle = d.plots_color;
        b.lineWidth = d.plots_width;
        let n = [];
        b.save();
        b.rect(f, g, h - f, a - v - g);
        b.clip();
        b.beginPath();
        if (this.continuous) {
            var l = !1,
                u = 0,
                t = !1;
            for (let m = 0, w = this.data.length; m < w; m++) {
                let c = this.getTransformedX(this.data[m].x, d, h, f),
                    p;
                m < w && !l && this.data[m + 1] && (p = this.getTransformedX(this.data[m + 1].x, d, h, f));
                if (c >= f && c < h || p !== k && p >= f && p < h) {
                    let h = this.getTransformedY(this.data[m].y, d, a, v, g);
                    d.plots_showIntegration && e.abs(this.data[m].y) > this.integrationSensitivity && n.push(new q.Point(this.data[m].x, this.data[m].y));
                    l || (b.moveTo(c, h), l = !0);
                    b.lineTo(c, h);
                    u++;
                    0 === u % 1E3 && (b.stroke(), b.beginPath(),
                        b.moveTo(c, h));
                    if (t) break
                } else l && (t = !0)
            }
        } else
            for (let e = 0, n = this.data.length; e < n; e++) l = this.getTransformedX(this.data[e].x, d, h, f), l >= f && l < h && (b.moveTo(l, a - v), b.lineTo(l, this.getTransformedY(this.data[e].y, d, a, v, g)));
        b.stroke();
        if (d.plots_showIntegration && 1 < n.length) {
            b.strokeStyle = d.plots_integrationColor;
            b.lineWidth = d.plots_integrationLineWidth;
            b.beginPath();
            l = n[1].x > n[0].x;
            if (this.flipXAxis && !l || !this.flipXAxis && l) {
                for (l = n.length - 2; 0 <= l; l--) n[l].y += n[l + 1].y;
                l = n[0].y
            } else {
                for (let a = 1, b = n.length; a <
                    b; a++) n[a].y += n[a - 1].y;
                l = n[n.length - 1].y
            }
            for (let e = 0, k = n.length; e < k; e++) u = this.getTransformedX(n[e].x, d, h, f), t = this.getTransformedY(n[e].y / d.scale / l, d, a, v, g), 0 === e ? b.moveTo(u, t) : b.lineTo(u, t);
            b.stroke()
        }
        b.restore()
    };
    t.getTransformedY = function(b, d, e, a, g) {
        return g + (e - a - g) * (1 - b * d.scale)
    };
    t.getInverseTransformedY = function(b) {
        return (1 - (b - this.memory.offsetTop) / (this.memory.height - this.memory.offsetBottom - this.memory.offsetTop)) / this.memory.scale * 100
    };
    t.getTransformedX = function(b, d, e, a) {
        b = a + (b - this.minX) /
            (this.maxX - this.minX) * (e - a);
        d.plots_flipXAxis && (b = e + a - b);
        return b
    };
    t.getInverseTransformedX = function(b) {
        this.memory.flipXAxis && (b = this.memory.width + this.memory.offsetLeft - b);
        return (b - this.memory.offsetLeft) * (this.maxX - this.minX) / (this.memory.width - this.memory.offsetLeft) + this.minX
    };
    t.setup = function() {
        let b = Number.MAX_VALUE,
            d = Number.MIN_VALUE,
            h = Number.MIN_VALUE;
        for (let a = 0, g = this.data.length; a < g; a++) b = e.min(b, this.data[a].x), d = e.max(d, this.data[a].x), h = e.max(h, this.data[a].y);
        this.continuous ? (this.minX =
            b, this.maxX = d) : (this.minX = b - 1, this.maxX = d + 1);
        for (let a = 0, b = this.data.length; a < b; a++) this.data[a].y /= h
    };
    t.zoom = function(b, d, h, a) {
        b = this.getInverseTransformedX(b);
        d = this.getInverseTransformedX(d);
        this.minX = e.min(b, d);
        this.maxX = e.max(b, d);
        if (a) {
            a = Number.MIN_VALUE;
            for (let b = 0, d = this.data.length; b < d; b++) l.isBetween(this.data[b].x, this.minX, this.maxX) && (a = e.max(a, this.data[b].y));
            return 1 / a
        }
    };
    t.translate = function(b, d) {
        b = b / (d - this.memory.offsetLeft) * (this.maxX - this.minX) * (this.memory.flipXAxis ? 1 : -1);
        this.minX +=
            b;
        this.maxX += b
    };
    t.alertMetadata = function() {
        alert(this.metadata.join("\n"))
    };
    t.getInternalCoordinates = function(b, d) {
        return new ChemDoodle.structures.Point(this.getInverseTransformedX(b), this.getInverseTransformedY(d))
    };
    t.getClosestPlotInternalCoordinates = function(b) {
        var d = this.getInverseTransformedX(b - 1);
        b = this.getInverseTransformedX(b + 1);
        if (d > b) {
            var e = d;
            d = b;
            b = e
        }
        e = -1;
        let a = -Infinity,
            g = !1;
        for (let h = 0, f = this.data.length; h < f; h++) {
            let f = this.data[h];
            if (l.isBetween(f.x, d, b)) f.y > a && (g = !0, a = f.y, e = h);
            else if (g) break
        }
        if (-1 ===
            e) return k;
        d = this.data[e];
        return new ChemDoodle.structures.Point(d.x, 100 * d.y)
    };
    t.getClosestPeakInternalCoordinates = function(b) {
        var d = this.getInverseTransformedX(b);
        b = 0;
        var h = Infinity;
        for (let g = 0, f = this.data.length; g < f; g++) {
            var a = e.abs(this.data[g].x - d);
            if (a <= h) h = a, b = g;
            else break
        }
        h = d = b;
        a = this.data[b].y;
        var g = this.data[b].y;
        for (let a = b + 1, d = this.data.length; a < d; a++)
            if (this.data[a].y + .05 > g) g = this.data[a].y, h = a;
            else break;
        for (g = b - 1; 0 <= g; g--)
            if (this.data[g].y + .05 > a) a = this.data[g].y, d = g;
            else break;
        b = this.data[d -
            b > h - b ? h : d];
        return new ChemDoodle.structures.Point(b.x, 100 * b.y)
    }
})(ChemDoodle.extensions, ChemDoodle.structures, ChemDoodle.math, ChemDoodle.lib.jQuery, Math);
(function(f, q, l, t) {
    q._Shape = function() {};
    q = q._Shape.prototype;
    q.drawDecorations = function(e, f) {
        if (this.isHover) {
            let b = this.getPoints();
            for (let d = 0, h = b.length; d < h; d++) {
                let a = b[d];
                this.drawAnchor(e, f, a, a === this.hoverPoint)
            }
        }
    };
    q.getBounds = function() {
        let e = new f.Bounds,
            k = this.getPoints();
        for (let b = 0, d = k.length; b < d; b++) {
            let d = k[b];
            e.expand(d.x, d.y)
        }
        return e
    };
    q.drawAnchor = function(e, f, b, d) {
        e.save();
        e.translate(b.x, b.y);
        e.rotate(l.PI / 4);
        e.scale(1 / f.scale, 1 / f.scale);
        e.beginPath();
        e.moveTo(-4, -4);
        e.lineTo(4,
            -4);
        e.lineTo(4, 4);
        e.lineTo(-4, 4);
        e.closePath();
        e.fillStyle = d ? f.colorHover : "white";
        e.fill();
        e.beginPath();
        e.moveTo(-4, -2);
        e.lineTo(-4, -4);
        e.lineTo(-2, -4);
        e.moveTo(2, -4);
        e.lineTo(4, -4);
        e.lineTo(4, -2);
        e.moveTo(4, 2);
        e.lineTo(4, 4);
        e.lineTo(2, 4);
        e.moveTo(-2, 4);
        e.lineTo(-4, 4);
        e.lineTo(-4, 2);
        e.moveTo(-4, -2);
        e.strokeStyle = "rgba(0,0,0,.2)";
        e.lineWidth = 5;
        e.stroke();
        e.strokeStyle = "blue";
        e.lineWidth = 1;
        e.stroke();
        e.restore()
    }
})(ChemDoodle.math, ChemDoodle.structures.d2, Math);
(function(f, q, l, t, e, k) {
    t.AtomMapping = function(b, d) {
        this.o1 = b;
        this.o2 = d;
        this.label = "0";
        this.error = !1
    };
    q = t.AtomMapping.prototype = new t._Shape;
    q.drawDecorations = function(b, d) {
        if (this.isHover || this.isSelected) b.strokeStyle = this.isHover ? d.colorHover : d.colorSelect, b.lineWidth = 1, b.beginPath(), b.moveTo(this.o1.x, this.o1.y), b.lineTo(this.o2.x, this.o2.y), b.setLineDash([2]), b.stroke(), b.setLineDash([])
    };
    q.draw = function(b, d) {
        if (this.o1 && this.o2) {
            this.x1 = this.o1.x + 14 * e.cos(this.o1.angleOfLeastInterference);
            this.y1 =
                this.o1.y - 14 * e.sin(this.o1.angleOfLeastInterference);
            this.x2 = this.o2.x + 14 * e.cos(this.o2.angleOfLeastInterference);
            this.y2 = this.o2.y - 14 * e.sin(this.o2.angleOfLeastInterference);
            b.font = f.getFontString(d.text_font_size, d.text_font_families, d.text_font_bold, d.text_font_italic);
            let h = this.label,
                a = b.measureText(h).width;
            this.isLassoed && (b.fillStyle = d.colorHover, b.fillRect(this.x1 - a / 2 - 3, this.y1 - d.text_font_size / 2 - 3, a + 6, d.text_font_size + 6), b.fillRect(this.x2 - a / 2 - 3, this.y2 - d.text_font_size / 2 - 3, a + 6, d.text_font_size +
                6));
            let g = this.error ? d.colorError : d.shapes_color;
            if (this.isHover || this.isSelected) g = this.isHover ? d.colorHover : d.colorSelect;
            b.fillStyle = g;
            b.fillRect(this.x1 - a / 2 - 1, this.y1 - d.text_font_size / 2 - 1, a + 2, d.text_font_size + 2);
            b.fillRect(this.x2 - a / 2 - 1, this.y2 - d.text_font_size / 2 - 1, a + 2, d.text_font_size + 2);
            b.textAlign = "center";
            b.textBaseline = "middle";
            b.fillStyle = d.backgroundColor;
            b.fillText(h, this.x1, this.y1);
            b.fillText(h, this.x2, this.y2)
        }
    };
    q.getPoints = function() {
        return [new l.Point(this.x1, this.y1), new l.Point(this.x2,
            this.y2)]
    };
    q.isOver = function(b, d) {
        return this.x1 ? b.distance({
            x: this.x1,
            y: this.y1
        }) < d || b.distance({
            x: this.x2,
            y: this.y2
        }) < d : !1
    }
})(ChemDoodle.extensions, ChemDoodle.math, ChemDoodle.structures, ChemDoodle.structures.d2, Math);
(function(f, q, l, t, e, k) {
    t.Bracket = function(b, d) {
        this.p1 = b ? b : new l.Point;
        this.p2 = d ? d : new l.Point
    };
    t = t.Bracket.prototype = new t._Shape;
    t.charge = 0;
    t.mult = 0;
    t.repeat = 0;
    t.draw = function(b, d) {
        let h = e.min(this.p1.x, this.p2.x),
            a = e.max(this.p1.x, this.p2.x),
            g = e.min(this.p1.y, this.p2.y),
            n = e.max(this.p1.y, this.p2.y),
            k = n - g;
        var m = k / 10;
        b.beginPath();
        b.moveTo(h + m, g);
        b.lineTo(h, g);
        b.lineTo(h, n);
        b.lineTo(h + m, n);
        b.moveTo(a - m, n);
        b.lineTo(a, n);
        b.lineTo(a, g);
        b.lineTo(a - m, g);
        this.isLassoed && (m = b.createLinearGradient(this.p1.x,
            this.p1.y, this.p2.x, this.p2.y), m.addColorStop(0, "rgba(212, 99, 0, 0)"), m.addColorStop(.5, "rgba(212, 99, 0, 0.8)"), m.addColorStop(1, "rgba(212, 99, 0, 0)"), b.lineWidth = d.shapes_lineWidth + 5, b.strokeStyle = m, b.lineJoin = "miter", b.lineCap = "square", b.stroke());
        b.strokeStyle = d.shapes_color;
        b.lineWidth = d.shapes_lineWidth;
        b.lineJoin = "miter";
        b.lineCap = "butt";
        b.stroke();
        0 !== this.charge && (b.fillStyle = d.text_color, b.textAlign = "left", b.textBaseline = "alphabetic", b.font = f.getFontString(d.text_font_size, d.text_font_families),
            m = this.charge.toFixed(0), m = "1" === m ? "+" : "-1" === m ? "\u2013" : m.startsWith("-") ? m.substring(1) + "\u2013" : m + "+", b.fillText(m, a + 5, g + 5));
        0 !== this.mult && (b.fillStyle = d.text_color, b.textAlign = "right", b.textBaseline = "middle", b.font = f.getFontString(d.text_font_size, d.text_font_families), b.fillText(this.mult.toFixed(0), h - 5, g + k / 2));
        0 !== this.repeat && (b.fillStyle = d.text_color, b.textAlign = "left", b.textBaseline = "top", b.font = f.getFontString(d.text_font_size, d.text_font_families), d = this.repeat.toFixed(0), b.fillText(d,
            a + 5, n - 5))
    };
    t.getPoints = function() {
        return [this.p1, this.p2]
    };
    t.isOver = function(b, d) {
        return q.isBetween(b.x, this.p1.x, this.p2.x) && q.isBetween(b.y, this.p1.y, this.p2.y)
    }
})(ChemDoodle.extensions, ChemDoodle.math, ChemDoodle.structures, ChemDoodle.structures.d2, Math);
(function(f, q, l, t, e, k, b) {
    e.RepeatUnit = function(b, a) {
        this.b1 = b;
        this.b2 = a;
        this.n1 = 1;
        this.n2 = 4;
        this.contents = [];
        this.ps = []
    };
    q = e.RepeatUnit.prototype = new e._Shape;
    q.drawDecorations = function(b, a) {
        if (this.isHover)
            for (let d = 0, e = this.contents.length; d < e; d++) {
                a = this.contents[d];
                let g = b.createRadialGradient(a.x - 1, a.y - 1, 0, a.x, a.y, 7);
                g.addColorStop(0, "rgba(212, 99, 0, 0)");
                g.addColorStop(.7, "rgba(212, 99, 0, 0.8)");
                b.fillStyle = g;
                b.beginPath();
                b.arc(a.x, a.y, 5, 0, 2 * k.PI, !1);
                b.fill()
            }
    };
    let d = function(b, a, d, e, f) {
        a = [];
        var g = 0 < f.length ? -1 === f.indexOf(d.a1) ? d.a2 : d.a1 : d.a1.distance(e.getCenter()) < d.a2.distance(e.getCenter()) ? d.a1 : d.a2;
        e = g.angle(d.getNeighbor(g));
        var h = e + k.PI / 2;
        d = d.getLength() / (1 < f.length ? 4 : 2);
        f = g.x + d * k.cos(e);
        g = g.y - d * k.sin(e);
        var n = 10 * k.cos(h),
            v = 10 * k.sin(h);
        h = f + n;
        d = g - v;
        f -= n;
        g += v;
        v = -4 * k.cos(e);
        var l = -4 * k.sin(e);
        e = h + v;
        n = d - l;
        v = f + v;
        l = g - l;
        b.beginPath();
        b.moveTo(e, n);
        b.lineTo(h, d);
        b.lineTo(f, g);
        b.lineTo(v, l);
        b.stroke();
        a.push(new t.Point(h, d));
        a.push(new t.Point(f, g));
        return a
    };
    q.draw = function(b, a) {
        if (this.b1 &&
            this.b2) {
            var g = this.error ? a.colorError : a.shapes_color;
            if (this.isHover || this.isSelected) g = this.isHover ? a.colorHover : a.colorSelect;
            b.strokeStyle = g;
            b.fillStyle = b.strokeStyle;
            b.lineWidth = a.shapes_lineWidth;
            b.lineJoin = "miter";
            b.lineCap = "butt";
            g = d(b, a, this.b1, this.b2, this.contents);
            let e = d(b, a, this.b2, this.b1, this.contents);
            this.ps = g.concat(e);
            this.b1.getCenter().x > this.b2.getCenter().x ? this.textPos = this.ps[0].x > this.ps[1].x + 5 ? this.ps[0] : this.ps[1] : this.textPos = this.ps[2].x > this.ps[3].x + 5 ? this.ps[2] : this.ps[3];
            !this.error && 0 < this.contents.length && (b.font = f.getFontString(a.text_font_size, a.text_font_families, a.text_font_bold, a.text_font_italic), b.fillStyle = this.isHover ? a.colorHover : a.text_color, b.textAlign = "left", b.textBaseline = "bottom", b.fillText(this.n1 + "-" + this.n2, this.textPos.x + 2, this.textPos.y + 2))
        }
    };
    q.getPoints = function() {
        return this.ps
    };
    q.isOver = function(b, a) {
        return !1
    };
    q.setContents = function(d) {
        this.contents = [];
        let a = d.getMoleculeByAtom(this.b1.a1);
        d = d.getMoleculeByAtom(this.b2.a1);
        if (a && a === d) {
            var g =
                d = 0;
            for (let b = 0, f = a.rings.length; b < f; b++) {
                var e = a.rings[b];
                for (let a = 0, b = e.bonds.length; a < b; a++) {
                    var h = e.bonds[a];
                    h === this.b1 ? d++ : h === this.b2 && g++
                }
            }
            d = 1 === d && 1 === g && this.b1.ring === this.b2.ring;
            this.contents.flippable = d;
            if (this.b1.ring === b && this.b2.ring === b || d)
                for (let b = 0, f = a.atoms.length; b < f; b++) {
                    h = e = g = !1;
                    for (let b = 0, d = a.bonds.length; b < d; b++) a.bonds[b].visited = !1;
                    let f = new t.Queue,
                        n = a.atoms[b];
                    for (f.enqueue(n); !(f.isEmpty() || g && e);) {
                        let b = f.dequeue();
                        d && (!this.flip && b === this.b1.a1 || this.flip && b ===
                            this.b1.a2) && (h = !0);
                        for (let d = 0, c = a.bonds.length; d < c; d++) {
                            let c = a.bonds[d];
                            if (c.a1 === b || c.a2 === b) c === this.b1 ? g = !0 : c === this.b2 ? e = !0 : c.visited || (c.visited = !0, f.enqueue(c.getNeighbor(b)))
                        }
                    }
                    g && e && (!d || h) && this.contents.push(n)
                }
        }
    }
})(ChemDoodle.extensions, ChemDoodle.math, ChemDoodle.lib.jsBezier, ChemDoodle.structures, ChemDoodle.structures.d2, Math);
(function(f, q, l, t, e, k) {
    t.Line = function(b, e) {
        this.p1 = b ? b : new l.Point;
        this.p2 = e ? e : new l.Point
    };
    t.Line.ARROW_SYNTHETIC = "synthetic";
    t.Line.ARROW_RETROSYNTHETIC = "retrosynthetic";
    t.Line.ARROW_RESONANCE = "resonance";
    t.Line.ARROW_EQUILIBRIUM = "equilibrium";
    let b = t.Line.prototype = new t._Shape;
    b.arrowType = k;
    b.topText = k;
    b.bottomText = k;
    b.draw = function(b, h) {
        if (this.isLassoed) {
            var a = b.createLinearGradient(this.p1.x, this.p1.y, this.p2.x, this.p2.y);
            a.addColorStop(0, "rgba(212, 99, 0, 0)");
            a.addColorStop(.5, "rgba(212, 99, 0, 0.8)");
            a.addColorStop(1, "rgba(212, 99, 0, 0)");
            var d = this.p1.angle(this.p2) + e.PI / 2,
                n = e.cos(d),
                k = e.sin(d);
            d = this.p1.x - 2.5 * n;
            var m = this.p1.y + 2.5 * k,
                l = this.p1.x + 2.5 * n,
                u = this.p1.y - 2.5 * k,
                w = this.p2.x + 2.5 * n,
                q = this.p2.y - 2.5 * k;
            n = this.p2.x - 2.5 * n;
            k = this.p2.y + 2.5 * k;
            b.fillStyle = a;
            b.beginPath();
            b.moveTo(d, m);
            b.lineTo(l, u);
            b.lineTo(w, q);
            b.lineTo(n, k);
            b.closePath();
            b.fill()
        }
        b.strokeStyle = h.shapes_color;
        b.fillStyle = h.shapes_color;
        b.lineWidth = h.shapes_lineWidth;
        b.lineJoin = "miter";
        b.lineCap = "butt";
        if (this.p1.x !== this.p2.x ||
            this.p1.y !== this.p2.y) {
            if (this.arrowType === t.Line.ARROW_RETROSYNTHETIC) {
                d = 2 * e.sqrt(2);
                a = h.shapes_arrowLength_2D / d;
                l = this.p1.angle(this.p2);
                u = l + e.PI / 2;
                d = h.shapes_arrowLength_2D / d;
                m = e.cos(l);
                l = e.sin(l);
                let g = e.cos(u),
                    f = e.sin(u);
                u = this.p1.x - g * a;
                w = this.p1.y + f * a;
                q = this.p1.x + g * a;
                n = this.p1.y - f * a;
                k = this.p2.x + g * a - m * d;
                var y = this.p2.y - f * a + l * d,
                    c = this.p2.x - g * a - m * d,
                    p = this.p2.y + f * a + l * d,
                    A = this.p2.x + g * a * 2 - m * d * 2;
                let v = this.p2.y - f * a * 2 + l * d * 2;
                m = this.p2.x - g * a * 2 - m * d * 2;
                a = this.p2.y + f * a * 2 + l * d * 2;
                b.beginPath();
                b.moveTo(q, n);
                b.lineTo(k, y);
                b.moveTo(A, v);
                b.lineTo(this.p2.x, this.p2.y);
                b.lineTo(m, a);
                b.moveTo(c, p);
                b.lineTo(u, w)
            } else this.arrowType === t.Line.ARROW_EQUILIBRIUM ? (a = 2 * e.sqrt(2), y = h.shapes_arrowLength_2D / a / 2, m = this.p1.angle(this.p2), u = m + e.PI / 2, a = 2 * h.shapes_arrowLength_2D / e.sqrt(3), d = e.cos(m), m = e.sin(m), l = e.cos(u), u = e.sin(u), w = this.p1.x - l * y, q = this.p1.y + u * y, c = this.p1.x + l * y, p = this.p1.y - u * y, n = this.p2.x + l * y, k = this.p2.y - u * y, A = this.p2.x - l * y, y = this.p2.y + u * y, b.beginPath(), b.moveTo(c, p), b.lineTo(n, k), b.moveTo(A, y), b.lineTo(w,
                q), b.stroke(), y = n - d * a * .8, c = k + m * a * .8, p = n + l * h.shapes_arrowLength_2D / 3 - d * a, A = k - u * h.shapes_arrowLength_2D / 3 + m * a, b.beginPath(), b.moveTo(n, k), b.lineTo(p, A), b.lineTo(y, c), b.closePath(), b.fill(), b.stroke(), y = w + d * a * .8, c = q - m * a * .8, p = w - l * h.shapes_arrowLength_2D / 3 + d * a, A = q + u * h.shapes_arrowLength_2D / 3 - m * a, b.beginPath(), b.moveTo(w, q), b.lineTo(p, A), b.lineTo(y, c), b.closePath(), b.fill()) : this.arrowType === t.Line.ARROW_SYNTHETIC ? (m = this.p1.angle(this.p2), l = m + e.PI / 2, a = 2 * h.shapes_arrowLength_2D / e.sqrt(3), d = e.cos(m), m = e.sin(m),
                n = e.cos(l), k = e.sin(l), b.beginPath(), b.moveTo(this.p1.x, this.p1.y), b.lineTo(this.p2.x - d * a / 2, this.p2.y + m * a / 2), b.stroke(), l = this.p2.x - d * a * .8, u = this.p2.y + m * a * .8, w = this.p2.x + n * h.shapes_arrowLength_2D / 3 - d * a, q = this.p2.y - k * h.shapes_arrowLength_2D / 3 + m * a, d = this.p2.x - n * h.shapes_arrowLength_2D / 3 - d * a, a = this.p2.y + k * h.shapes_arrowLength_2D / 3 + m * a, b.beginPath(), b.moveTo(this.p2.x, this.p2.y), b.lineTo(d, a), b.lineTo(l, u), b.lineTo(w, q), b.closePath(), b.fill()) : this.arrowType === t.Line.ARROW_RESONANCE ? (m = this.p1.angle(this.p2),
                u = m + e.PI / 2, a = 2 * h.shapes_arrowLength_2D / e.sqrt(3), d = e.cos(m), m = e.sin(m), l = e.cos(u), u = e.sin(u), b.beginPath(), b.moveTo(this.p1.x + d * a / 2, this.p1.y - m * a / 2), b.lineTo(this.p2.x - d * a / 2, this.p2.y + m * a / 2), b.stroke(), w = this.p2.x - d * a * .8, q = this.p2.y + m * a * .8, n = this.p2.x + l * h.shapes_arrowLength_2D / 3 - d * a, k = this.p2.y - u * h.shapes_arrowLength_2D / 3 + m * a, y = this.p2.x - l * h.shapes_arrowLength_2D / 3 - d * a, c = this.p2.y + u * h.shapes_arrowLength_2D / 3 + m * a, b.beginPath(), b.moveTo(this.p2.x, this.p2.y), b.lineTo(y, c), b.lineTo(w, q), b.lineTo(n, k),
                b.closePath(), b.fill(), b.stroke(), w = this.p1.x + d * a * .8, q = this.p1.y - m * a * .8, n = this.p1.x - l * h.shapes_arrowLength_2D / 3 + d * a, k = this.p1.y + u * h.shapes_arrowLength_2D / 3 - m * a, y = this.p1.x + l * h.shapes_arrowLength_2D / 3 + d * a, c = this.p1.y - u * h.shapes_arrowLength_2D / 3 - m * a, b.beginPath(), b.moveTo(this.p1.x, this.p1.y), b.lineTo(y, c), b.lineTo(w, q), b.lineTo(n, k), b.closePath(), b.fill()) : (b.beginPath(), b.moveTo(this.p1.x, this.p1.y), b.lineTo(this.p2.x, this.p2.y));
            b.stroke();
            if (this.topText || this.bottomText) b.font = f.getFontString(h.text_font_size,
                h.text_font_families, h.text_font_bold, h.text_font_italic), b.fillStyle = h.text_color;
            this.topText && (b.textAlign = "center", b.textBaseline = "bottom", b.fillText(this.topText, (this.p1.x + this.p2.x) / 2, this.p1.y - 5));
            this.bottomText && (b.textAlign = "center", b.textBaseline = "top", b.fillText(this.bottomText, (this.p1.x + this.p2.x) / 2, this.p1.y + 5))
        }
    };
    b.getPoints = function() {
        return [this.p1, this.p2]
    };
    b.isOver = function(b, e) {
        b = q.distanceFromPointToLineInclusive(b, this.p1, this.p2);
        return -1 !== b && b < e
    }
})(ChemDoodle.extensions,
    ChemDoodle.math, ChemDoodle.structures, ChemDoodle.structures.d2, Math);
(function(f, q, l, t, e, k) {
    let b = function(a) {
            let b = [];
            if (a instanceof l.Atom)
                if (0 === a.bondNumber) b.push(e.PI);
                else {
                    if (a.angles) {
                        if (1 === a.angles.length) b.push(a.angles[0] + e.PI);
                        else {
                            for (let d = 1, g = a.angles.length; d < g; d++) b.push(a.angles[d - 1] + (a.angles[d] - a.angles[d - 1]) / 2);
                            var d = a.angles[a.angles.length - 1];
                            b.push(d + (a.angles[0] + 2 * e.PI - d) / 2)
                        }
                        a.largestAngle > e.PI && (b = [a.angleOfLeastInterference]);
                        if (a.bonds)
                            for (let g = 0, e = a.bonds.length; g < e; g++)
                                if (d = a.bonds[g], 2 === d.bondOrder && (d = d.getNeighbor(a), "O" === d.label)) {
                                    b = [d.angle(a)];
                                    break
                                }
                    }
                }
            else a = a.a1.angle(a.a2), b.push(a + e.PI / 2), b.push(a + 3 * e.PI / 2);
            for (let a = 0, d = b.length; a < d; a++) {
                for (; b[a] > 2 * e.PI;) b[a] -= 2 * e.PI;
                for (; 0 > b[a];) b[a] += 2 * e.PI
            }
            return b
        },
        d = function(a, b) {
            let d = 3;
            if (a instanceof l.Atom) {
                if (a.isLabelVisible(b) && (d = 8), 0 !== a.charge || 0 !== a.numRadical || 0 !== a.numLonePair) d = 13
            } else a instanceof l.Point ? d = 0 : 1 < a.bondOrder && (d = 5);
            return d
        },
        h = function(a, b, h, f, k, t, u, w, q, y) {
            var c = t.angle(k),
                g = u.angle(w),
                n = e.cos(c);
            c = e.sin(c);
            var m = d(h, b);
            k.x -= n * m;
            k.y += c * m;
            m = g + e.PI / 2;
            h =
                2 * b.shapes_arrowLength_2D / e.sqrt(3);
            n = e.cos(g);
            c = e.sin(g);
            let v = e.cos(m),
                x = e.sin(m);
            w.x -= 5 * n;
            w.y += 5 * c;
            g = new l.Point(w.x, w.y);
            m = d(f, b) / 3;
            g.x -= n * m;
            g.y += c * m;
            w.x -= n * (.8 * h + m);
            w.y += c * (.8 * h + m);
            f = g.x - n * h * .8;
            m = g.y + c * h * .8;
            let z = new l.Point(g.x + v * b.shapes_arrowLength_2D / 3 - n * h, g.y - x * b.shapes_arrowLength_2D / 3 + c * h);
            b = new l.Point(g.x - v * b.shapes_arrowLength_2D / 3 - n * h, g.y + x * b.shapes_arrowLength_2D / 3 + c * h);
            c = n = !0;
            1 === q && (z.distance(t) > b.distance(t) ? c = !1 : n = !1);
            a.beginPath();
            a.moveTo(g.x, g.y);
            c && a.lineTo(b.x, b.y);
            a.lineTo(f,
                m);
            n && a.lineTo(z.x, z.y);
            a.closePath();
            a.fill();
            a.stroke();
            a.beginPath();
            a.moveTo(k.x, k.y);
            a.bezierCurveTo(t.x, t.y, u.x, u.y, w.x, w.y);
            a.stroke();
            y.push([k, t, u, w])
        };
    t.Pusher = function(a, b, d) {
        this.o1 = a;
        this.o2 = b;
        this.numElectron = d ? d : 1
    };
    t = t.Pusher.prototype = new t._Shape;
    t.drawDecorations = function(a, b) {
        if (this.isHover) {
            var d = this.o1 instanceof l.Atom ? new l.Point(this.o1.x, this.o1.y) : this.o1.getCenter(),
                g = this.o2 instanceof l.Atom ? new l.Point(this.o2.x, this.o2.y) : this.o2.getCenter();
            d = [d, g];
            for (let e = 0, h =
                    d.length; e < h; e++) g = d[e], this.drawAnchor(a, b, g, g === this.hoverPoint)
        }
    };
    t.draw = function(a, d) {
        if (this.o1 && this.o2) {
            a.strokeStyle = d.shapes_color;
            a.fillStyle = d.shapes_color;
            a.lineWidth = d.shapes_lineWidth;
            a.lineJoin = "miter";
            a.lineCap = "butt";
            let n = this.o1 instanceof l.Atom ? new l.Point(this.o1.x, this.o1.y) : this.o1.getCenter(),
                v = this.o2 instanceof l.Atom ? new l.Point(this.o2.x, this.o2.y) : this.o2.getCenter();
            var g = b(this.o1),
                k = b(this.o2);
            let c, p;
            var m = Infinity;
            for (let a = 0, b = g.length; a < b; a++)
                for (let b = 0, d = k.length; b <
                    d; b++) {
                    var t = new l.Point(n.x + 35 * e.cos(g[a]), n.y - 35 * e.sin(g[a])),
                        u = new l.Point(v.x + 35 * e.cos(k[b]), v.y - 35 * e.sin(k[b])),
                        w = t.distance(u);
                    w < m && (m = w, c = t, p = u)
                }
            this.caches = []; - 1 === this.numElectron ? (t = n.distance(v) / 2, k = n.angle(v), g = k + e.PI / 2, u = e.cos(k), w = e.sin(k), k = new l.Point(n.x + (t - 1) * u, n.y - (t - 1) * w), m = new l.Point(k.x + 35 * e.cos(g + e.PI / 6), k.y - 35 * e.sin(g + e.PI / 6)), t = new l.Point(n.x + (t + 1) * u, n.y - (t + 1) * w), g = new l.Point(t.x + 35 * e.cos(g - e.PI / 6), t.y - 35 * e.sin(g - e.PI / 6)), h(a, d, this.o1, k, n, c, m, k, 1, this.caches), h(a, d, this.o2,
                t, v, p, g, t, 1, this.caches)) : (f.intersectLines(n.x, n.y, c.x, c.y, v.x, v.y, p.x, p.y) && (g = c, c = p, p = g), g = c.angle(n), k = p.angle(v), m = e.max(g, k) - e.min(g, k), .001 > e.abs(m - e.PI) && this.o1.molCenter === this.o2.molCenter && (g += e.PI / 2, k -= e.PI / 2, c.x = n.x + 35 * e.cos(g + e.PI), c.y = n.y - 35 * e.sin(g + e.PI), p.x = v.x + 35 * e.cos(k + e.PI), p.y = v.y - 35 * e.sin(k + e.PI)), h(a, d, this.o1, this.o2, n, c, p, v, this.numElectron, this.caches))
        }
    };
    t.getPoints = function() {
        return []
    };
    t.isOver = function(a, b) {
        for (let d = 0, g = this.caches.length; d < g; d++)
            if (q.distanceFromCurve(a,
                    this.caches[d]).distance < b) return !0;
        return !1
    }
})(ChemDoodle.math, ChemDoodle.lib.jsBezier, ChemDoodle.structures, ChemDoodle.structures.d2, Math);
(function(f, q, l, t, e) {
    let k = new q.Bond;
    l.VAP = function(b, d) {
        this.asterisk = new q.Atom("O", b, d);
        this.substituent;
        this.bondType = 1;
        this.attachments = []
    };
    f = l.VAP.prototype = new l._Shape;
    f.drawDecorations = function(b, d) {
        if (this.isHover || this.isSelected) {
            b.strokeStyle = this.isHover ? d.colorHover : d.colorSelect;
            b.lineWidth = 1.2;
            if (this.hoverBond) {
                let e = 2 * t.PI,
                    a = (this.asterisk.angleForStupidCanvasArcs(this.hoverBond) + t.PI / 2) % e;
                b.strokeStyle = this.isHover ? d.colorHover : d.colorSelect;
                b.beginPath();
                d = (a + t.PI) % e;
                d %= 2 * t.PI;
                b.arc(this.asterisk.x, this.asterisk.y, 7, a, d, !1);
                b.stroke();
                b.beginPath();
                a += t.PI;
                d = (a + t.PI) % e;
                b.arc(this.hoverBond.x, this.hoverBond.y, 7, a, d, !1)
            } else b.beginPath(), b.arc(this.asterisk.x, this.asterisk.y, 7, 0, 2 * t.PI, !1);
            b.stroke()
        }
    };
    f.draw = function(b, d) {
        b.strokeStyle = this.error ? d.colorError : d.shapes_color;
        b.lineWidth = 1;
        var e = t.sqrt(3) / 2;
        b.beginPath();
        b.moveTo(this.asterisk.x, this.asterisk.y - 4);
        b.lineTo(this.asterisk.x, this.asterisk.y + 4);
        b.moveTo(this.asterisk.x - 4 * e, this.asterisk.y - 2);
        b.lineTo(this.asterisk.x +
            4 * e, this.asterisk.y + 2);
        b.moveTo(this.asterisk.x - 4 * e, this.asterisk.y + 2);
        b.lineTo(this.asterisk.x + 4 * e, this.asterisk.y - 2);
        b.stroke();
        this.asterisk.textBounds = [];
        this.asterisk.textBounds.push({
            x: this.asterisk.x - 4,
            y: this.asterisk.y - 4,
            w: 8,
            h: 8
        });
        e = d.bonds_color;
        this.error && (d.bonds_color = d.colorError);
        k.a1 = this.asterisk;
        this.substituent && (k.a2 = this.substituent, k.bondOrder = this.bondType, k.draw(b, d));
        k.bondOrder = 0;
        this.error || (d.bonds_color = d.shapes_color);
        for (let a = 0, g = this.attachments.length; a < g; a++) k.a2 =
            this.attachments[a], k.draw(b, d);
        d.bonds_color = e
    };
    f.getPoints = function() {
        return [this.asterisk]
    };
    f.isOver = function(b, d) {
        return !1
    }
})(ChemDoodle.math, ChemDoodle.structures, ChemDoodle.structures.d2, Math);
(function(f, q, l) {
    f._Mesh = function() {};
    f = f._Mesh.prototype;
    f.storeData = function(f, e, k) {
        this.positionData = f;
        this.normalData = e;
        this.indexData = k
    };
    f.setupBuffers = function(f) {
        this.vertexPositionBuffer = f.createBuffer();
        f.bindBuffer(f.ARRAY_BUFFER, this.vertexPositionBuffer);
        f.bufferData(f.ARRAY_BUFFER, new Float32Array(this.positionData), f.STATIC_DRAW);
        this.vertexPositionBuffer.itemSize = 3;
        this.vertexPositionBuffer.numItems = this.positionData.length / 3;
        this.vertexNormalBuffer = f.createBuffer();
        f.bindBuffer(f.ARRAY_BUFFER,
            this.vertexNormalBuffer);
        f.bufferData(f.ARRAY_BUFFER, new Float32Array(this.normalData), f.STATIC_DRAW);
        this.vertexNormalBuffer.itemSize = 3;
        this.vertexNormalBuffer.numItems = this.normalData.length / 3;
        this.indexData && (this.vertexIndexBuffer = f.createBuffer(), f.bindBuffer(f.ELEMENT_ARRAY_BUFFER, this.vertexIndexBuffer), f.bufferData(f.ELEMENT_ARRAY_BUFFER, new Uint16Array(this.indexData), f.STATIC_DRAW), this.vertexIndexBuffer.itemSize = 1, this.vertexIndexBuffer.numItems = this.indexData.length);
        if (this.partitions)
            for (let e =
                    0, k = this.partitions.length; e < k; e++) {
                let b = this.partitions[e],
                    d = this.generateBuffers(f, b.positionData, b.normalData, b.indexData);
                b.vertexPositionBuffer = d[0];
                b.vertexNormalBuffer = d[1];
                b.vertexIndexBuffer = d[2]
            }
    };
    f.generateBuffers = function(f, e, k, b) {
        let d = f.createBuffer();
        f.bindBuffer(f.ARRAY_BUFFER, d);
        f.bufferData(f.ARRAY_BUFFER, new Float32Array(e), f.STATIC_DRAW);
        d.itemSize = 3;
        d.numItems = e.length / 3;
        e = f.createBuffer();
        f.bindBuffer(f.ARRAY_BUFFER, e);
        f.bufferData(f.ARRAY_BUFFER, new Float32Array(k), f.STATIC_DRAW);
        e.itemSize = 3;
        e.numItems = k.length / 3;
        let h;
        b && (h = f.createBuffer(), f.bindBuffer(f.ELEMENT_ARRAY_BUFFER, h), f.bufferData(f.ELEMENT_ARRAY_BUFFER, new Uint16Array(b), f.STATIC_DRAW), h.itemSize = 1, h.numItems = b.length);
        return [d, e, h]
    };
    f.bindBuffers = function(f) {
        this.vertexPositionBuffer || this.setupBuffers(f);
        f.bindBuffer(f.ARRAY_BUFFER, this.vertexPositionBuffer);
        f.vertexAttribPointer(f.shader.vertexPositionAttribute, this.vertexPositionBuffer.itemSize, f.FLOAT, !1, 0, 0);
        f.bindBuffer(f.ARRAY_BUFFER, this.vertexNormalBuffer);
        f.vertexAttribPointer(f.shader.vertexNormalAttribute, this.vertexNormalBuffer.itemSize, f.FLOAT, !1, 0, 0);
        this.vertexIndexBuffer && f.bindBuffer(f.ELEMENT_ARRAY_BUFFER, this.vertexIndexBuffer)
    }
})(ChemDoodle.structures.d3, Math);
(function(f, q) {
    f._Measurement = function() {};
    f = f._Measurement.prototype = new f._Mesh;
    f.render = function(f, t) {
        f.shader.setMatrixUniforms(f);
        t.measurement_update_3D && (this.text = this.vertexPositionBuffer = q);
        this.vertexPositionBuffer || this.calculateData(t);
        this.bindBuffers(f);
        f.material.setDiffuseColor(f, t.shapes_color);
        f.lineWidth(t.shapes_lineWidth);
        f.drawElements(f.LINES, this.vertexIndexBuffer.numItems, f.UNSIGNED_SHORT, 0)
    };
    f.renderText = function(f, t) {
        f.shader.setMatrixUniforms(f);
        this.text || (this.text =
            this.getText(t));
        t = {
            position: [],
            texCoord: [],
            translation: []
        };
        f.textImage.pushVertexData(this.text.value, this.text.pos, 1, t);
        f.textMesh.storeData(f, t.position, t.texCoord, t.translation);
        f.textImage.useTexture(f);
        f.textMesh.render(f)
    }
})(ChemDoodle.structures.d3);
(function(f, q, l, t, e, k, b, d) {
    l.Angle = function(b, a, d) {
        this.a1 = b;
        this.a2 = a;
        this.a3 = d
    };
    f = l.Angle.prototype = new l._Measurement;
    f.calculateData = function(d) {
        let a = [],
            g = [],
            h = [];
        var f = this.a2.distance3D(this.a1),
            k = this.a2.distance3D(this.a3);
        this.distUse = e.min(f, k) / 2;
        this.vec1 = b.normalize([this.a1.x - this.a2.x, this.a1.y - this.a2.y, this.a1.z - this.a2.z]);
        this.vec2 = b.normalize([this.a3.x - this.a2.x, this.a3.y - this.a2.y, this.a3.z - this.a2.z]);
        this.angle = q.vec3AngleFrom(this.vec1, this.vec2);
        f = b.normalize(b.cross(this.vec1,
            this.vec2, []));
        f = b.normalize(b.cross(f, this.vec1, []));
        d = d.measurement_angleBands_3D;
        for (k = 0; k <= d; ++k) {
            var l = this.angle * k / d,
                u = b.scale(this.vec1, e.cos(l), []);
            l = b.scale(f, e.sin(l), []);
            u = b.scale(b.normalize(b.add(u, l, [])), this.distUse);
            a.push(this.a2.x + u[0], this.a2.y + u[1], this.a2.z + u[2]);
            g.push(0, 0, 0);
            k < d && h.push(k, k + 1)
        }
        this.storeData(a, g, h)
    };
    f.getText = function(d) {
        d = b.scale(b.normalize(b.add(this.vec1, this.vec2, [])), this.distUse + .3);
        return {
            pos: [this.a2.x + d[0], this.a2.y + d[1], this.a2.z + d[2]],
            value: [t.angleBounds(this.angle,
                !0).toFixed(2), " \u00b0"].join("")
        }
    }
})(ChemDoodle.ELEMENT, ChemDoodle.extensions, ChemDoodle.structures.d3, ChemDoodle.math, Math, ChemDoodle.lib.mat4, ChemDoodle.lib.vec3);
(function(f, q, l) {
    f.Arrow = function(f, e) {
        let k = [],
            b = [];
        for (var d = 0; d <= e; d++) {
            var h = 2 * d * q.PI / e,
                a = q.sin(h);
            h = q.cos(h);
            b.push(0, 0, -1, 0, 0, -1, h, a, 0, h, a, 0, 0, 0, -1, 0, 0, -1, h, a, 1, h, a, 1);
            k.push(0, 0, 0, f * h, f * a, 0, f * h, f * a, 0, f * h, f * a, 2, f * h, f * a, 2, f * h * 2, f * a * 2, 2, f * h * 2, f * a * 2, 2, 0, 0, 3)
        }
        f = [];
        for (d = 0; d < e; d++) {
            a = 8 * d;
            for (let b = 0, d = 7; b < d; b++) {
                h = b + a;
                let g = h + d + 2;
                f.push(h, g, h + 1, g, h, g - 1)
            }
        }
        this.storeData(k, b, f)
    };
    f.Arrow.prototype = new f._Mesh
})(ChemDoodle.structures.d3, Math);
(function(f, q, l) {
    f.Box = function(f, e, k) {
        f /= 2;
        k /= 2;
        let b = [],
            d = [];
        b.push(f, e, -k);
        b.push(f, e, -k);
        b.push(-f, e, -k);
        b.push(f, e, k);
        b.push(-f, e, k);
        b.push(-f, e, k);
        for (var h = 6; h--; d.push(0, 1, 0));
        b.push(-f, e, k);
        b.push(-f, e, k);
        b.push(-f, 0, k);
        b.push(f, e, k);
        b.push(f, 0, k);
        b.push(f, 0, k);
        for (h = 6; h--; d.push(0, 0, 1));
        b.push(f, e, k);
        b.push(f, e, k);
        b.push(f, 0, k);
        b.push(f, e, -k);
        b.push(f, 0, -k);
        b.push(f, 0, -k);
        for (h = 6; h--; d.push(1, 0, 0));
        b.push(f, e, -k);
        b.push(f, e, -k);
        b.push(f, 0, -k);
        b.push(-f, e, -k);
        b.push(-f, 0, -k);
        b.push(-f, 0,
            -k);
        for (h = 6; h--; d.push(0, 0, -1));
        b.push(-f, e, -k);
        b.push(-f, e, -k);
        b.push(-f, 0, -k);
        b.push(-f, e, k);
        b.push(-f, 0, k);
        b.push(-f, 0, k);
        for (e = 6; e--; d.push(-1, 0, 0));
        b.push(-f, 0, k);
        b.push(-f, 0, k);
        b.push(-f, 0, -k);
        b.push(f, 0, k);
        b.push(f, 0, -k);
        b.push(f, 0, -k);
        for (f = 6; f--; d.push(0, -1, 0));
        this.storeData(b, d)
    };
    f.Box.prototype = new f._Mesh
})(ChemDoodle.structures.d3, Math);
(function(f, q, l, t, e, k) {
    q.Camera = function() {
        this.fieldOfView = 45;
        this.aspect = 1;
        this.near = .1;
        this.far = 1E4;
        this.zoom = 1;
        this.viewMatrix = t.identity([]);
        this.projectionMatrix = t.identity([])
    };
    f = q.Camera.prototype;
    f.perspectiveProjectionMatrix = function() {
        let b = e.tan(this.fieldOfView / 360 * e.PI) * this.near * this.zoom,
            d = this.aspect * b;
        return t.frustum(-d, d, -b, b, this.near, this.far, this.projectionMatrix)
    };
    f.orthogonalProjectionMatrix = function() {
        let b = e.tan(this.fieldOfView / 360 * e.PI) * ((this.far - this.near) / 2 + this.near) *
            this.zoom,
            d = this.aspect * b;
        return t.ortho(-d, d, -b, b, this.near, this.far, this.projectionMatrix)
    };
    f.updateProjectionMatrix = function(b) {
        return b ? this.perspectiveProjectionMatrix() : this.orthogonalProjectionMatrix()
    };
    f.focalLength = function() {
        return (this.far - this.near) / 2 + this.near
    };
    f.zoomOut = function() {
        this.zoom = e.min(1.25 * this.zoom, 200)
    };
    f.zoomIn = function() {
        this.zoom = e.max(this.zoom / 1.25, .0025)
    }
})(ChemDoodle.math, ChemDoodle.structures.d3, ChemDoodle.lib.vec3, ChemDoodle.lib.mat4, Math);
(function(f, q, l, t) {
    f.LineArrow = function() {
        this.storeData([0, 0, -3, .1, 0, -2.8, 0, 0, -3, -.1, 0, -2.8, 0, 0, -3, 0, 0, 3, 0, 0, 3, .1, 0, 2.8, 0, 0, 3, -.1, 0, 2.8], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
    };
    f.LineArrow.prototype = new f._Mesh;
    f.Compass = function(e, b) {
        this.textImage = new f.TextImage;
        this.textImage.init(e);
        this.textImage.updateFont(e, b.text_font_size, b.text_font_families, b.text_font_bold, b.text_font_italic, b.text_font_stroke_3D);
        this.textMesh = new f.TextMesh;
        this.textMesh.init(e);
        var d = 3 / (b.compass_size_3D /
                e.canvas.clientHeight),
            h = q.tan(b.projectionPerspectiveVerticalFieldOfView_3D / 360 * q.PI);
        let a = d / h,
            g = q.max(a - d, .1);
        var k = e.canvas.clientWidth / e.canvas.clientHeight;
        let v;
        if (b.projectionPerspective_3D) {
            var m = g;
            v = l.frustum
        } else m = a, v = l.ortho;
        let t = m / e.canvas.clientHeight * 2 * h;
        h *= m;
        m = -h;
        let u = k * m;
        k *= h;
        if (0 === b.compass_type_3D) {
            let a = (-(e.canvas.clientWidth - b.compass_size_3D) / 2 + this.textImage.charHeight) * t;
            b = (-(e.canvas.clientHeight - b.compass_size_3D) / 2 + this.textImage.charHeight) * t;
            u -= a;
            k -= a;
            m -= b;
            h -= b
        }
        this.projectionMatrix =
            v(u, k, m, h, g, a + d);
        this.translationMatrix = l.translate(l.identity([]), [0, 0, -a]);
        d = {
            position: [],
            texCoord: [],
            translation: []
        };
        this.textImage.pushVertexData("X", [3.5, 0, 0], 0, d);
        this.textImage.pushVertexData("Y", [0, 3.5, 0], 0, d);
        this.textImage.pushVertexData("Z", [0, 0, 3.5], 0, d);
        this.textMesh.storeData(e, d.position, d.texCoord, d.translation)
    };
    let e = f.Compass.prototype;
    e.renderArrow = function(e, b, d, h) {
        e.material.setDiffuseColor(e, d);
        e.shader.setModelViewMatrix(e, h);
        1 === b ? e.drawArrays(e.LINES, 0, e.lineArrowBuffer.vertexPositionBuffer.numItems) :
            e.drawElements(e.TRIANGLES, e.arrowBuffer.vertexIndexBuffer.numItems, e.UNSIGNED_SHORT, 0)
    };
    e.render = function(e, b) {
        e.shader.setProjectionMatrix(e, this.projectionMatrix);
        1 === b.compass_type_3D ? e.lineArrowBuffer.bindBuffers(e) : e.arrowBuffer.bindBuffers(e);
        e.material.setTempColors(e, b.bonds_materialAmbientColor_3D, t, b.bonds_materialSpecularColor_3D, b.bonds_materialShininess_3D);
        let d = l.multiply(this.translationMatrix, e.rotationMatrix, []),
            h = q.PI / 2;
        this.renderArrow(e, b.compass_type_3D, b.compass_axisXColor_3D,
            l.rotateY(d, h, []));
        this.renderArrow(e, b.compass_type_3D, b.compass_axisYColor_3D, l.rotateX(d, -h, []));
        this.renderArrow(e, b.compass_type_3D, b.compass_axisZColor_3D, d)
    };
    e.renderAxis = function(e) {
        e.shader.setProjectionMatrix(e, this.projectionMatrix);
        let b = l.multiply(this.translationMatrix, e.rotationMatrix, []);
        e.shader.setModelViewMatrix(e, b);
        this.textImage.useTexture(e);
        this.textMesh.render(e)
    }
})(ChemDoodle.structures.d3, Math, ChemDoodle.lib.mat4);
(function(f, q, l) {
    f.Cylinder = function(f, e, k, b) {
        let d = [],
            h = [];
        if (b) {
            for (b = 0; b <= k; b++) {
                var a = b % k * 2 * q.PI / k,
                    g = q.cos(a);
                a = q.sin(a);
                h.push(0, -1, 0);
                d.push(0, 0, 0);
                h.push(0, -1, 0);
                d.push(f * g, 0, f * a)
            }
            for (b = 0; b <= k; b++) a = b % k * 2 * q.PI / k, g = q.cos(a), a = q.sin(a), h.push(g, 0, a), d.push(f * g, 0, f * a), h.push(g, 0, a), d.push(f * g, e, f * a);
            for (b = 0; b <= k; b++) a = b % k * 2 * q.PI / k, g = q.cos(a), a = q.sin(a), h.push(0, 1, 0), d.push(f * g, e, f * a), h.push(0, 1, 0), d.push(0, e, 0)
        } else {
            for (b = 0; b < k; b++) a = 2 * b * q.PI / k, g = q.cos(a), a = q.sin(a), h.push(g, 0, a), d.push(f * g, 0,
                f * a), h.push(g, 0, a), d.push(f * g, e, f * a);
            h.push(1, 0, 0);
            d.push(f, 0, 0);
            h.push(1, 0, 0);
            d.push(f, e, 0)
        }
        this.storeData(d, h)
    };
    f.Cylinder.prototype = new f._Mesh
})(ChemDoodle.structures.d3, Math);
(function(f, q, l, t, e) {
    q.Distance = function(e, b, d, h) {
        this.a1 = e;
        this.a2 = b;
        this.node = d;
        this.offset = h ? h : 0
    };
    q = q.Distance.prototype = new q._Measurement;
    q.calculateData = function(e) {
        let b = [this.a1.x, this.a1.y, this.a1.z, this.a2.x, this.a2.y, this.a2.z];
        this.node && (this.move = this.offset + l.max(e.atoms_useVDWDiameters_3D ? f[this.a1.label].vdWRadius * e.atoms_vdwMultiplier_3D : e.atoms_sphereDiameter_3D / 2, e.atoms_useVDWDiameters_3D ? f[this.a2.label].vdWRadius * e.atoms_vdwMultiplier_3D : e.atoms_sphereDiameter_3D / 2), this.displacement = [(this.a1.x + this.a2.x) / 2 - this.node.x, (this.a1.y + this.a2.y) / 2 - this.node.y, (this.a1.z + this.a2.z) / 2 - this.node.z], t.normalize(this.displacement), e = t.scale(this.displacement, this.move, []), b[0] += e[0], b[1] += e[1], b[2] += e[2], b[3] += e[0], b[4] += e[1], b[5] += e[2]);
        this.storeData(b, [0, 0, 0, 0, 0, 0], [0, 1])
    };
    q.getText = function(e) {
        e = this.a1.distance3D(this.a2);
        let b = [(this.a1.x + this.a2.x) / 2, (this.a1.y + this.a2.y) / 2, (this.a1.z + this.a2.z) / 2];
        if (this.node) {
            let d = t.scale(this.displacement, this.move + .1, []);
            b[0] += d[0];
            b[1] +=
                d[1];
            b[2] += d[2]
        }
        return {
            pos: b,
            value: [e.toFixed(2), " \u212b"].join("")
        }
    }
})(ChemDoodle.ELEMENT, ChemDoodle.structures.d3, Math, ChemDoodle.lib.vec3);
(function(f, q, l, t) {
    q.Fog = function(e, f, b, d) {
        this.fogScene(e, f, b, d)
    };
    q.Fog.prototype.fogScene = function(e, k, b, d) {
        this.colorRGB = f.getRGB(e, 1);
        this.fogStart = k;
        this.fogEnd = b;
        this.density = d
    }
})(ChemDoodle.math, ChemDoodle.structures.d3, ChemDoodle.lib.vec3);
(function(f, q, l) {
    q.Label = function(f) {};
    q = q.Label.prototype;
    q.updateVerticesBuffer = function(t, e, k) {
        for (let n = 0, v = e.length; n < v; n++) {
            var b = e[n];
            let m = b.labelMesh;
            var d = b.atoms;
            let v = {
                position: [],
                texCoord: [],
                translation: []
            };
            var h = 0 < d.length && d[0].hetatm != l;
            for (let b = 0, e = d.length; b < e; b++) {
                var a = d[b],
                    g = a.label;
                let e = .05;
                k.atoms_useVDWDiameters_3D ? (g = f[g].vdWRadius * k.atoms_vdwMultiplier_3D, 0 === g && (g = 1), e += g) : k.atoms_sphereDiameter_3D && (e += k.atoms_sphereDiameter_3D / 2 * 1.5);
                if (h)
                    if (!a.hetatm) {
                        if (!k.macro_displayAtoms) continue
                    } else if (a.isWater &&
                    !k.macro_showWaters) continue;
                t.textImage.pushVertexData(a.altLabel ? a.altLabel : a.label, [a.x, a.y, a.z], e, v)
            }
            if ((b = b.chains) && (k.proteins_displayRibbon || k.proteins_displayBackbone))
                for (let g = 0, e = b.length; g < e; g++) {
                    d = b[g];
                    for (let b = 0, g = d.length; b < g; b++) h = d[b], h.name && (a = h.cp1, t.textImage.pushVertexData(h.name, [a.x, a.y, a.z], 2, v))
                }
            m.storeData(t, v.position, v.texCoord, v.translation, v.zDepth)
        }
    };
    q.render = function(f, e, k) {
        f.shader.setMatrixUniforms(f);
        f.textImage.useTexture(f);
        for (let b = 0, d = k.length; b < d; b++) k[b].labelMesh &&
            k[b].labelMesh.render(f)
    }
})(ChemDoodle.ELEMENT, ChemDoodle.structures.d3);
(function(f, q, l) {
    f.Sphere = function(f, e, k) {
        let b = [],
            d = [];
        for (var h = 0; h <= e; h++) {
            var a = h * q.PI / e,
                g = q.sin(a);
            a = q.cos(a);
            for (var n = 0; n <= k; n++) {
                var v = 2 * n * q.PI / k,
                    m = q.sin(v);
                v = q.cos(v) * g;
                let e = a;
                m *= g;
                d.push(v, e, m);
                b.push(f * v, f * e, f * m)
            }
        }
        f = [];
        k += 1;
        for (h = 0; h < e; h++)
            for (g = 0; g < k; g++) a = h * k + g % k, n = a + k, f.push(a, a + 1, n), g < k - 1 && f.push(n, a + 1, n + 1);
        this.storeData(b, d, f)
    };
    f.Sphere.prototype = new f._Mesh
})(ChemDoodle.structures.d3, Math);
(function(f, q, l, t, e) {
    function k(b, e, a, g) {
        this.entire = b;
        this.name = e;
        this.indexes = a;
        this.pi = g
    }
    let b = k.prototype;
    b.getColor = function(b) {
        return b.macro_colorByChain ? this.entire.chainColor : this.name ? this.getResidueColor(f[this.name] ? this.name : "*", b) : this.helix ? this.entire.front ? b.proteins_ribbonCartoonHelixPrimaryColor : b.proteins_ribbonCartoonHelixSecondaryColor : this.sheet ? b.proteins_ribbonCartoonSheetColor : this.entire.front ? b.proteins_primaryColor : b.proteins_secondaryColor
    };
    b.getResidueColor = function(b,
        e) {
        b = f[b];
        if ("shapely" === e.proteins_residueColor) return b.shapelyColor;
        if ("amino" === e.proteins_residueColor) return b.aminoColor;
        if ("polarity" === e.proteins_residueColor) {
            if (b.polar) return "#C10000"
        } else if ("acidity" === e.proteins_residueColor) {
            if (1 === b.acidity) return "#0000FF";
            if (-1 === b.acidity) return "#FF0000";
            if (!b.polar) return "#773300"
        }
        return "#FFFFFF"
    };
    b.render = function(b, e, a) {
        if (this.entire.partitions && this.pi !== this.entire.partitions.lastRender) {
            var d = this.entire.partitions[this.pi];
            b.bindBuffer(b.ARRAY_BUFFER,
                d.vertexPositionBuffer);
            b.vertexAttribPointer(b.shader.vertexPositionAttribute, d.vertexPositionBuffer.itemSize, b.FLOAT, !1, 0, 0);
            b.bindBuffer(b.ARRAY_BUFFER, d.vertexNormalBuffer);
            b.vertexAttribPointer(b.shader.vertexNormalAttribute, d.vertexNormalBuffer.itemSize, b.FLOAT, !1, 0, 0);
            b.bindBuffer(b.ELEMENT_ARRAY_BUFFER, d.vertexIndexBuffer);
            this.entire.partitions.lastRender = this.pi
        }
        this.vertexIndexBuffer || (this.vertexIndexBuffer = b.createBuffer(), b.bindBuffer(b.ELEMENT_ARRAY_BUFFER, this.vertexIndexBuffer), b.bufferData(b.ELEMENT_ARRAY_BUFFER,
            new Uint16Array(this.indexes), b.STATIC_DRAW), this.vertexIndexBuffer.itemSize = 1, this.vertexIndexBuffer.numItems = this.indexes.length);
        b.bindBuffer(b.ELEMENT_ARRAY_BUFFER, this.vertexIndexBuffer);
        a || "rainbow" === e.proteins_residueColor || b.material.setDiffuseColor(b, this.getColor(e));
        b.drawElements(b.TRIANGLES, this.vertexIndexBuffer.numItems, b.UNSIGNED_SHORT, 0)
    };
    q.Ribbon = function(b, f, a) {
        let d = b[0].lineSegments.length,
            h = b[0].lineSegments[0].length;
        this.partitions = [];
        this.partitions.lastRender = 0;
        this.front =
            0 < f;
        for (let g = 0, e = b.length; g < e; g++) {
            if (!v || 65E3 < v.positionData.length) {
                0 < this.partitions.length && g--;
                var v = {
                    count: 0,
                    positionData: [],
                    normalData: []
                };
                this.partitions.push(v)
            }
            var m = b[g];
            v.count++;
            for (var x = 0; x < d; x++) {
                var u = a ? m.lineSegmentsCartoon[x] : m.lineSegments[x],
                    w = 0 === x,
                    q = !1;
                for (var y = 0; y < h; y++) {
                    var c = u[y],
                        p = g,
                        A = y + 1;
                    g === b.length - 1 && y === h - 1 ? A-- : y === h - 1 && (p++, A = 0);
                    A = a ? b[p].lineSegmentsCartoon[x][A] : b[p].lineSegments[x][A];
                    p = !1;
                    var B = x + 1;
                    x === d - 1 && (B -= 2, p = !0);
                    B = a ? m.lineSegmentsCartoon[B][y] : m.lineSegments[B][y];
                    A = [A.x - c.x, A.y - c.y, A.z - c.z];
                    B = [B.x - c.x, B.y - c.y, B.z - c.z];
                    let e = t.cross(A, B, []);
                    0 === y && (t.normalize(A), t.scale(A, -1), v.normalData.push(A[0], A[1], A[2]), v.positionData.push(c.x, c.y, c.z));
                    w || q ? (t.normalize(B), t.scale(B, -1), v.normalData.push(B[0], B[1], B[2]), v.positionData.push(c.x, c.y, c.z), w && y === h - 1 && (w = !1, y = -1)) : (t.normalize(e), (p && !this.front || !p && this.front) && t.scale(e, -1), v.normalData.push(e[0], e[1], e[2]), t.scale(e, l.abs(f)), v.positionData.push(c.x + e[0], c.y + e[1], c.z + e[2]), x === d - 1 && y === h - 1 && (q = !0, y = -1));
                    if (-1 === y || y === h - 1) t.normalize(A), v.normalData.push(A[0], A[1], A[2]), v.positionData.push(c.x, c.y, c.z)
                }
            }
        }
        d += 2;
        h += 2;
        this.segments = [];
        this.partitionSegments = [];
        for (let g = 0, n = this.partitions.length; g < n; g++) {
            f = this.partitions[g];
            v = [];
            m = e;
            for (let n = 0, l = f.count - 1; n < l; n++) {
                m = n;
                for (x = 0; x < g; x++) m += this.partitions[x].count - 1;
                m = b[m];
                u = n * d * h;
                x = [];
                for (let a = 0, b = d - 1; a < b; a++)
                    for (w = u + a * h, q = 0; q < h - 1; q++) y = 1, n === l && (y = 0), y = [w + q, w + h + q, w + h + q + y, w + q, w + q + y, w + h + q + y], q !== h - 1 && (this.front ? x.push(y[0], y[1], y[2], y[3], y[5],
                        y[4]) : x.push(y[0], y[2], y[1], y[3], y[4], y[5])), q !== h - 2 || n === f.count - 2 && g === this.partitions.length - 1 || (c = d * h - q, y[2] += c, y[4] += c, y[5] += c), this.front ? v.push(y[0], y[1], y[2], y[3], y[5], y[4]) : v.push(y[0], y[2], y[1], y[3], y[4], y[5]);
                a && m.split && (v = new k(this, e, v, g), v.helix = m.helix, v.sheet = m.sheet, this.partitionSegments.push(v), v = []);
                this.segments.push(new k(this, m.name, x, g))
            }
            f = new k(this, e, v, g);
            f.helix = m.helix;
            f.sheet = m.sheet;
            this.partitionSegments.push(f)
        }
        this.storeData(this.partitions[0].positionData, this.partitions[0].normalData);
        1 === this.partitions.length && (this.partitions = e)
    };
    (q.Ribbon.prototype = new q._Mesh).render = function(b, f) {
        this.bindBuffers(b);
        let a = f.macro_colorByChain ? this.chainColor : e;
        a || (a = this.front ? f.proteins_primaryColor : f.proteins_secondaryColor);
        b.material.setDiffuseColor(b, a);
        for (let a = 0, d = this.partitionSegments.length; a < d; a++) this.partitionSegments[a].render(b, f, !f.proteins_ribbonCartoonize)
    }
})(ChemDoodle.RESIDUE, ChemDoodle.structures.d3, Math, ChemDoodle.lib.vec3);
(function(f, q, l, t, e) {
    q.Light = function(e, b, d) {
        this.camera = new q.Camera;
        this.lightScene(e, b, d)
    };
    e = q.Light.prototype;
    e.lightScene = function(e, b, d) {
        this.diffuseRGB = f.getRGB(e, 1);
        this.specularRGB = f.getRGB(b, 1);
        this.direction = d;
        this.updateView()
    };
    e.updateView = function() {
        var e = l.normalize(this.direction, []);
        let b = l.scale(e, (this.camera.near - this.camera.far) / 2 - this.camera.near, []);
        e = l.equal(e, [0, 1, 0]) ? [0, 0, 1] : [0, 1, 0];
        t.lookAt(b, [0, 0, 0], e, this.camera.viewMatrix);
        this.camera.orthogonalProjectionMatrix()
    }
})(ChemDoodle.math,
    ChemDoodle.structures.d3, ChemDoodle.lib.vec3, ChemDoodle.lib.mat4);
(function(f, q) {
    f.Line = function() {
        this.storeData([0, 0, 0, 0, 1, 0], [0, 0, 0, 0, 0, 0])
    };
    f.Line.prototype = new f._Mesh
})(ChemDoodle.structures.d3);
(function(f, q, l) {
    q.Material = function() {};
    q = q.Material.prototype;
    q.setTempColors = function(l, e, k, b, d) {
        e && l.shader.setMaterialAmbientColor(l, f.getRGB(e, 1));
        k && l.shader.setMaterialDiffuseColor(l, f.getRGB(k, 1));
        b && l.shader.setMaterialSpecularColor(l, f.getRGB(b, 1));
        l.shader.setMaterialShininess(l, d);
        l.shader.setMaterialAlpha(l, 1)
    };
    q.setDiffuseColor = function(l, e) {
        l.shader.setMaterialDiffuseColor(l, f.getRGB(e, 1))
    };
    q.setAlpha = function(f, e) {
        f.shader.setMaterialAlpha(f, e)
    }
})(ChemDoodle.math, ChemDoodle.structures.d3);
(function(f, q, l, t) {
    f.Picker = function() {};
    f = f.Picker.prototype;
    f.init = function(e) {
        this.framebuffer = e.createFramebuffer();
        let f = e.createTexture(),
            b = e.createRenderbuffer();
        e.bindTexture(e.TEXTURE_2D, f);
        e.texParameteri(e.TEXTURE_2D, e.TEXTURE_MAG_FILTER, e.NEAREST);
        e.texParameteri(e.TEXTURE_2D, e.TEXTURE_MIN_FILTER, e.NEAREST);
        e.texParameteri(e.TEXTURE_2D, e.TEXTURE_WRAP_S, e.CLAMP_TO_EDGE);
        e.texParameteri(e.TEXTURE_2D, e.TEXTURE_WRAP_T, e.CLAMP_TO_EDGE);
        e.bindRenderbuffer(e.RENDERBUFFER, b);
        e.bindFramebuffer(e.FRAMEBUFFER,
            this.framebuffer);
        e.framebufferTexture2D(e.FRAMEBUFFER, e.COLOR_ATTACHMENT0, e.TEXTURE_2D, f, 0);
        e.framebufferRenderbuffer(e.FRAMEBUFFER, e.DEPTH_ATTACHMENT, e.RENDERBUFFER, b);
        e.bindTexture(e.TEXTURE_2D, null);
        e.bindRenderbuffer(e.RENDERBUFFER, null);
        e.bindFramebuffer(e.FRAMEBUFFER, null)
    };
    f.setDimension = function(e, f, b) {
        e.bindFramebuffer(e.FRAMEBUFFER, this.framebuffer);
        var d = e.getFramebufferAttachmentParameter(e.FRAMEBUFFER, e.DEPTH_ATTACHMENT, e.FRAMEBUFFER_ATTACHMENT_OBJECT_NAME);
        e.isRenderbuffer(d) && (e.bindRenderbuffer(e.RENDERBUFFER,
            d), e.renderbufferStorage(e.RENDERBUFFER, e.DEPTH_COMPONENT16, f, b), e.bindRenderbuffer(e.RENDERBUFFER, null));
        d = e.getFramebufferAttachmentParameter(e.FRAMEBUFFER, e.COLOR_ATTACHMENT0, e.FRAMEBUFFER_ATTACHMENT_OBJECT_NAME);
        e.isTexture(d) && (e.bindTexture(e.TEXTURE_2D, d), e.texImage2D(e.TEXTURE_2D, 0, e.RGBA, f, b, 0, e.RGBA, e.UNSIGNED_BYTE, null), e.bindTexture(e.TEXTURE_2D, null));
        e.bindFramebuffer(e.FRAMEBUFFER, null)
    }
})(ChemDoodle.structures.d3, ChemDoodle.math, document);
(function(f, q, l) {
    f.Pill = function(f, e, k, b) {
        var d = 1,
            h = 2 * f;
        e -= h;
        0 > e ? (d = 0, e += h) : e < h && (d = e / h, e = h);
        h = [];
        let a = [];
        for (var g = 0; g <= k; g++) {
            var n = g * q.PI / k,
                v = q.sin(n);
            n = q.cos(n) * d;
            for (let d = 0; d <= b; d++) {
                var m = 2 * d * q.PI / b,
                    l = q.sin(m);
                m = q.cos(m) * v;
                let u = n;
                l *= v;
                a.push(m, u, l);
                h.push(f * m, f * u + (g < k / 2 ? e : 0), f * l)
            }
        }
        f = [];
        b += 1;
        for (e = 0; e < k; e++)
            for (d = 0; d < b; d++) g = e * b + d % b, v = g + b, f.push(g, g + 1, v), d < b - 1 && f.push(v, g + 1, v + 1);
        this.storeData(h, a, f)
    };
    f.Pill.prototype = new f._Mesh
})(ChemDoodle.structures.d3, Math);
(function(f, q, l, t, e, k, b, d, h) {
    function a(a, b, d) {
        let g = new l.Residue(-1);
        g.cp1 = g.cp2 = new l.Atom("", a, b, d);
        return g
    }

    function g(a, b) {
        this.a1 = a;
        this.a2 = b
    }

    function n(a, b, d) {
        this.a1 = a;
        this.a2 = b;
        this.vx = d
    }
    g.prototype.render = function(a, d) {
        var g = this.a1;
        let h = this.a2;
        var n = 1.001 * g.distance3D(h);
        d = d.proteins_cylinderHelixDiameter / 2;
        n = [d, n, d];
        d = k.translate(k.identity(), [g.x, g.y, g.z]);
        var m = [0, 1, 0];
        let v = 0;
        g.x === h.x && g.z === h.z ? (m = [0, 0, 1], h.y < g.y && (v = e.PI)) : (g = [h.x - g.x, h.y - g.y, h.z - g.z], v = f.vec3AngleFrom(m, g), m =
            b.cross(m, g, []));
        0 !== v && k.rotate(d, v, m);
        k.scale(d, n);
        a.shader.setMatrixUniforms(a, d);
        a.drawArrays(a.TRIANGLE_STRIP, 0, a.cylinderClosedBuffer.vertexPositionBuffer.numItems)
    };
    n.prototype.render = function(a, d) {
        this.styles && (d = this.styles);
        let g = 1.001 * this.a1.distance3D(this.a2);
        var e = [this.a2.x - this.a1.x, this.a2.y - this.a1.y, this.a2.z - this.a1.z];
        let f = b.cross(e, this.vx, []),
            h = b.cross(f, e, []);
        b.normalize(h);
        b.normalize(e);
        b.normalize(f);
        e = [h[0], h[1], h[2], 0, e[0], e[1], e[2], 0, f[0], f[1], f[2], 0, this.a1.x, this.a1.y,
            this.a1.z, 1
        ];
        k.scale(e, [d.proteins_plankSheetWidth, g, d.proteins_tubeThickness]);
        a.shader.setMatrixUniforms(a, e);
        a.drawArrays(a.TRIANGLE_STRIP, 0, a.boxBuffer.vertexPositionBuffer.numItems)
    };
    t.PipePlank = function(d, f) {
        this.tubes = [];
        this.helixCylinders = [];
        this.sheetPlanks = [];
        this.chainColor = d.chainColor;
        var h = [],
            k = [],
            m = [],
            v = [];
        if (1 < d.length) {
            var q = d[0],
                c = d[1];
            c.helix ? m.push(q) : c.sheet ? v.push(q) : k.push(q)
        }
        for (let f = 1, u = d.length - 1; f <= u; f++)
            if (q = d[f], q.helix) {
                if (m.push(q), q.arrow) {
                    var p = b.create();
                    c = b.create();
                    if (1 === m.length) p = [q.guidePointsSmall[0].x, q.guidePointsSmall[0].y, q.guidePointsSmall[0].z], c = q.guidePointsSmall[q.guidePointsSmall.length - 1], c = [c.x, c.y, c.z];
                    else if (2 === m.length) p = [m[0].cp1.x, m[0].cp1.y, m[0].cp1.z], c = [m[1].cp1.x, m[1].cp1.y, m[1].cp1.z];
                    else {
                        3 === m.length && m.unshift(d[e.max(f - 3, 0)]);
                        var A = [],
                            B = [];
                        for (let a = 1, c = m.length - 1; a < c; a++) {
                            var C = [m[a].cp1.x, m[a].cp1.y, m[a].cp1.z],
                                D = [m[a - 1].cp1.x, m[a - 1].cp1.y, m[a - 1].cp1.z],
                                F = [m[a + 1].cp1.x, m[a + 1].cp1.y, m[a + 1].cp1.z];
                            b.subtract(D, C);
                            b.subtract(F,
                                C);
                            var L = b.scale(D, b.length(F), []);
                            D = b.scale(F, b.length(D), []);
                            L = b.normalize(b.add(L, D, []));
                            A.push(C);
                            B.push(L)
                        }
                        m = [];
                        for (let a = 0, c = A.length - 1; a < c; a++) {
                            D = A[a];
                            F = B[a];
                            C = A[a + 1];
                            L = B[a + 1];
                            var H = b.normalize(b.cross(F, L, [])),
                                K = b.subtract(C, D, []);
                            let c = b.dot(K, H);
                            H = b.scale(H, c, []);
                            H = b.length(H);
                            K = b.length(K);
                            K = -(H * H - K * K) / (2 * b.dot(b.subtract(D, C, []), L));
                            D = b.add(D, b.scale(F, K, []), []);
                            C = b.add(C, b.scale(L, K, []), []);
                            m.push([D, C])
                        }
                        A = m[0][0];
                        B = m[0][1];
                        B = b.subtract(A, B, []);
                        b.add(A, B, p);
                        A = m[m.length - 1][1];
                        B = m[m.length -
                            1][0];
                        B = b.subtract(A, B, []);
                        b.add(A, B, c)
                    }
                    m = new l.Atom("", p[0], p[1], p[2]);
                    A = new l.Atom("", c[0], c[1], c[2]);
                    this.helixCylinders.push(new g(m, A));
                    m = [];
                    A = b.subtract(p, c, []);
                    b.normalize(A);
                    b.scale(A, .5);
                    0 < k.length && (B = b.add(p, A, []), C = k[k.length - 1].cp1, C = b.subtract([C.x, C.y, C.z], B, []), b.normalize(C), b.scale(C, .5), b.add(B, C), C = new l.Residue(-1), C.cp1 = C.cp2 = new l.Atom("", B[0], B[1], B[2]), k.push(C), C = a(p[0], p[1], p[2]), k.push(C), h.push(k));
                    k = [];
                    f < u && (p = a(c[0], c[1], c[2]), k.push(p), p = d[f + 1], p.sheet ? (k.push(q), k.push(q),
                        h.push(k), k = [], v.push(q)) : (b.scale(A, -1), q = b.add(c, A, []), c = p.cp1, c = b.subtract([c.x, c.y, c.z], q, []), b.normalize(c), b.scale(c, .5), b.add(q, c), q = a(q[0], q[1], q[2]), k.push(q)))
                }
            } else if (q.sheet) {
            if (v.push(q), q.arrow) {
                p = [0, 0, 0];
                A = [0, 0, 0];
                c = v.length;
                for (B = 0; B < c; B++) L = v[B].guidePointsLarge, C = L[0], L = L[L.length - 1], b.add(p, [C.x, C.y, C.z]), b.add(A, [L.x, L.y, L.z]);
                b.scale(p, 1 / c);
                b.scale(A, 1 / c);
                p = b.subtract(p, A);
                c = v[c - 1].guidePointsSmall[0];
                this.sheetPlanks.push(new n(v[0].guidePointsSmall[0], c, p));
                v = [];
                f < u && (d[f +
                    1].sheet ? v.push(q) : (q = a(c.x, c.y, c.z), k.push(q)))
            }
        } else k.push(q), f < u && d[f + 1].sheet && (c = q.guidePointsSmall[0], c = a(c.x, c.y, c.z), k.push(c), h.push(k), k = [], v.push(q));
        1 < k.length && (2 == k.length && k.push(k[k.length - 1]), h.push(k));
        k = [];
        for (let a = 0, b = h.length; a < b; a++) {
            v = h[a];
            q = [];
            for (let a = 0, b = v.length - 1; a <= b; a++) q.push(v[a].cp1);
            k.push(q)
        }
        for (let a = 0, b = k.length; a < b; a++) h = new t.CatmullTube(k[a], f.proteins_tubeThickness, f.proteins_tubeResolution_3D, f.proteins_horizontalResolution), h.chainColor = d.chainColor, this.tubes.push(h)
    };
    (t.PipePlank.prototype = new t._Mesh).render = function(a, b) {
        a.material.setTempColors(a, b.proteins_materialAmbientColor_3D, h, b.proteins_materialSpecularColor_3D, b.proteins_materialShininess_3D);
        a.material.setDiffuseColor(a, b.macro_colorByChain ? this.chainColor : b.proteins_tubeColor);
        for (let d = 0, g = this.tubes.length; d < g; d++) a.shader.setMatrixUniforms(a), this.tubes[d].render(a, b);
        b.macro_colorByChain || a.material.setDiffuseColor(a, b.proteins_ribbonCartoonHelixSecondaryColor);
        a.cylinderClosedBuffer.bindBuffers(a);
        for (let d = 0, g = this.helixCylinders.length; d < g; d++) this.helixCylinders[d].render(a, b);
        b.macro_colorByChain || a.material.setDiffuseColor(a, b.proteins_ribbonCartoonSheetColor);
        a.boxBuffer.bindBuffers(a);
        for (let d = 0, g = this.sheetPlanks.length; d < g; d++) this.sheetPlanks[d].render(a, b)
    }
})(ChemDoodle.extensions, ChemDoodle.RESIDUE, ChemDoodle.structures, ChemDoodle.structures.d3, Math, ChemDoodle.lib.mat4, ChemDoodle.lib.vec3, ChemDoodle.math);
(function(f, q) {
    f.Quad = function() {
        this.storeData([-1, 1, 0, -1, -1, 0, 1, 1, 0, 1, -1, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
    };
    f.Quad.prototype = new f._Mesh
})(ChemDoodle.structures.d3);
(function(f, q, l, t) {
    q.Shape = function(e, k) {
        var b = e.length;
        let d = [],
            h = [],
            a = new f.Point;
        for (let f = 0, m = b; f < m; f++) {
            var g = f + 1;
            f === m - 1 && (g = 0);
            let b = e[f];
            var n = e[g];
            g = l.cross([0, 0, 1], [n.x - b.x, n.y - b.y, 0]);
            for (let a = 0; 2 > a; a++) d.push(b.x, b.y, k / 2), d.push(b.x, b.y, -k / 2), d.push(n.x, n.y, k / 2), d.push(n.x, n.y, -k / 2);
            for (n = 0; 4 > n; n++) h.push(g[0], g[1], g[2]);
            h.push(0, 0, 1);
            h.push(0, 0, -1);
            h.push(0, 0, 1);
            h.push(0, 0, -1);
            a.add(b)
        }
        a.x /= b;
        a.y /= b;
        h.push(0, 0, 1);
        d.push(a.x, a.y, k / 2);
        h.push(0, 0, -1);
        d.push(a.x, a.y, -k / 2);
        e = [];
        k = 8 * b;
        for (let a =
                0, d = b; a < d; a++) b = 8 * a, e.push(b), e.push(b + 3), e.push(b + 1), e.push(b), e.push(b + 2), e.push(b + 3), e.push(b + 4), e.push(k), e.push(b + 6), e.push(b + 5), e.push(b + 7), e.push(k + 1);
        this.storeData(d, h, e)
    };
    q.Shape.prototype = new q._Mesh
})(ChemDoodle.structures, ChemDoodle.structures.d3, ChemDoodle.lib.vec3);
(function(f, q, l, t) {
    f.Star = function() {
        let e = [.8944, .4472, 0, .2764, .4472, .8506, .2764, .4472, -.8506, -.7236, .4472, .5257, -.7236, .4472, -.5257, -.3416, .4472, 0, -.1056, .4472, .3249, -.1056, .4472, -.3249, .2764, .4472, .2008, .2764, .4472, -.2008, -.8944, -.4472, 0, -.2764, -.4472, .8506, -.2764, -.4472, -.8506, .7236, -.4472, .5257, .7236, -.4472, -.5257, .3416, -.4472, 0, .1056, -.4472, .3249, .1056, -.4472, -.3249, -.2764, -.4472, .2008, -.2764, -.4472, -.2008, -.5527, .1058, 0, -.1708, .1058, .5527, -.1708, .1058, -.5527, .4471, .1058, .3249, .4471, .1058, -.3249,
                .5527, -.1058, 0, .1708, -.1058, .5527, .1708, -.1058, -.5527, -.4471, -.1058, .3249, -.4471, -.1058, -.3249, 0, 1, 0, 0, -1, 0
            ],
            f = [0, 9, 8, 2, 7, 9, 4, 5, 7, 3, 6, 5, 1, 8, 6, 0, 8, 23, 30, 6, 8, 3, 21, 6, 11, 26, 21, 13, 23, 26, 2, 9, 24, 30, 8, 9, 1, 23, 8, 13, 25, 23, 14, 24, 25, 4, 7, 22, 30, 9, 7, 0, 24, 9, 14, 27, 24, 12, 22, 27, 3, 5, 20, 30, 7, 5, 2, 22, 7, 12, 29, 22, 10, 20, 29, 1, 6, 21, 30, 5, 6, 4, 20, 5, 10, 28, 20, 11, 21, 28, 10, 19, 18, 12, 17, 19, 14, 15, 17, 13, 16, 15, 11, 18, 16, 31, 19, 17, 14, 17, 27, 2, 27, 22, 4, 22, 29, 10, 29, 19, 31, 18, 19, 12, 19, 29, 4, 29, 20, 3, 20, 28, 11, 28, 18, 31, 16, 18, 10, 18, 28, 3, 28, 21, 1, 21, 26,
                13, 26, 16, 31, 15, 16, 11, 16, 26, 1, 26, 23, 0, 23, 25, 14, 25, 15, 31, 17, 15, 13, 15, 25, 0, 25, 24, 2, 24, 27, 12, 27, 17
            ],
            b = [],
            d = [],
            h = [];
        for (let k = 0, m = f.length; k < m; k += 3) {
            var a = 3 * f[k],
                g = 3 * f[k + 1],
                n = 3 * f[k + 2];
            a = [e[a], e[a + 1], e[a + 2]];
            g = [e[g], e[g + 1], e[g + 2]];
            n = [e[n], e[n + 1], e[n + 2]];
            let m = l.cross([n[0] - g[0], n[1] - g[1], n[2] - g[2]], [a[0] - g[0], a[1] - g[1], a[2] - g[2]], []);
            l.normalize(m);
            b.push(a[0], a[1], a[2], g[0], g[1], g[2], n[0], n[1], n[2]);
            d.push(m[0], m[1], m[2], m[0], m[1], m[2], m[0], m[1], m[2]);
            h.push(k, k + 1, k + 2)
        }
        this.storeData(b, d, h)
    };
    f.Star.prototype =
        new f._Mesh
})(ChemDoodle.structures.d3, Math, ChemDoodle.lib.vec3);
(function(f, q, l, t, e) {
    let k = 1;
    t.devicePixelRatio && (k = t.devicePixelRatio);
    f.TextImage = function() {
        this.ctx = l.createElement("canvas").getContext("2d");
        this.data = [];
        this.text = "";
        this.charHeight = 0
    };
    f = f.TextImage.prototype;
    f.init = function(b) {
        this.textureImage = b.createTexture();
        b.bindTexture(b.TEXTURE_2D, this.textureImage);
        b.pixelStorei(b.UNPACK_FLIP_Y_WEBGL, !1);
        b.texParameteri(b.TEXTURE_2D, b.TEXTURE_WRAP_S, b.CLAMP_TO_EDGE);
        b.texParameteri(b.TEXTURE_2D, b.TEXTURE_WRAP_T, b.CLAMP_TO_EDGE);
        b.texParameteri(b.TEXTURE_2D,
            b.TEXTURE_MIN_FILTER, b.NEAREST);
        b.texParameteri(b.TEXTURE_2D, b.TEXTURE_MAG_FILTER, b.NEAREST);
        b.bindTexture(b.TEXTURE_2D, null);
        this.updateFont(b, 12, ["Sans-serif"], !1, !1, !1)
    };
    f.charData = function(b) {
        b = this.text.indexOf(b);
        return 0 <= b ? this.data[b] : null
    };
    f.updateFont = function(b, d, e, a, g, f) {
        let h = this.ctx,
            n = this.ctx.canvas,
            l = [],
            u = "";
        d *= k;
        e = q.getFontString(d, e, a, g);
        h.font = e;
        h.save();
        a = 0;
        d *= 1.5;
        for (let b = 32, c = 127; b < c; b++) {
            g = String.fromCharCode(b);
            var w = h.measureText(g).width;
            l.push({
                text: g,
                width: w,
                height: d
            });
            a += 2 * w
        }
        g = ["\u00b0", "\u212b", "\u00ae"];
        for (let b = 0, c = g.length; b < c; b++) {
            w = g[b];
            var t = h.measureText(w).width;
            l.push({
                text: w,
                width: t,
                height: d
            });
            a += 2 * t
        }
        g = Math.ceil(Math.sqrt(a * d) / d);
        a = Math.ceil(a / (g - 1));
        n.width = a;
        n.height = g * d;
        h.font = e;
        h.textAlign = "left";
        h.textBaseline = "middle";
        h.strokeStyle = "#000";
        h.lineWidth = 1.4;
        h.fillStyle = "#fff";
        g = e = 0;
        for (let b = 0, c = l.length; b < c; b++) {
            w = l[b];
            t = 2 * w.width;
            let c = w.height,
                d = w.text;
            g + t > a && (e++, g = 0);
            let k = e * c;
            f && h.strokeText(d, g, k + c / 2);
            h.fillText(d, g, k + c / 2);
            w.x = g;
            w.y = k;
            u +=
                d;
            g += t
        }
        this.text = u;
        this.data = l;
        this.charHeight = d;
        b.bindTexture(b.TEXTURE_2D, this.textureImage);
        b.texImage2D(b.TEXTURE_2D, 0, b.RGBA, b.RGBA, b.UNSIGNED_BYTE, n);
        b.bindTexture(b.TEXTURE_2D, null)
    };
    f.pushVertexData = function(b, d, e, a) {
        let g = b.toString().split(""),
            f = this.getHeight(),
            h = this.getWidth();
        b = -this.textWidth(b) / 2 / k;
        let m = -this.charHeight / 2 / k;
        for (let n = 0, v = g.length; n < v; n++) {
            var l = this.charData(g[n]);
            let v = l.width,
                u = l.x / h,
                c = u + 1.8 * l.width / h,
                p = l.y / f;
            l = p + l.height / f;
            let w = b + 1.8 * v / k,
                t = this.charHeight / 2 / k;
            a.position.push(d[0], d[1], d[2], d[0], d[1], d[2], d[0], d[1], d[2], d[0], d[1], d[2], d[0], d[1], d[2], d[0], d[1], d[2]);
            a.texCoord.push(u, p, c, l, c, p, u, p, u, l, c, l);
            a.translation.push(b, t, e, w, m, e, w, t, e, b, t, e, b, m, e, w, m, e);
            b = w + (v - 1.8 * v) / k
        }
    };
    f.getCanvas = function() {
        return this.ctx.canvas
    };
    f.getHeight = function() {
        return this.getCanvas().height
    };
    f.getWidth = function() {
        return this.getCanvas().width
    };
    f.textWidth = function(b) {
        return this.ctx.measureText(b).width
    };
    f.test = function() {
        l.body.appendChild(this.getCanvas())
    };
    f.useTexture =
        function(b) {
            b.bindTexture(b.TEXTURE_2D, this.textureImage)
        }
})(ChemDoodle.structures.d3, ChemDoodle.extensions, document, window);
(function(f, q, l) {
    f.TextMesh = function() {};
    f = f.TextMesh.prototype;
    f.init = function(f) {
        this.vertexPositionBuffer = f.createBuffer();
        this.vertexTexCoordBuffer = f.createBuffer();
        this.vertexTranslationBuffer = f.createBuffer()
    };
    f.setVertexData = function(f, e, k, b) {
        f.bindBuffer(f.ARRAY_BUFFER, e);
        f.bufferData(f.ARRAY_BUFFER, new Float32Array(k), f.STATIC_DRAW);
        e.itemSize = b;
        e.numItems = k.length / b
    };
    f.storeData = function(f, e, k, b) {
        this.setVertexData(f, this.vertexPositionBuffer, e, 3);
        this.setVertexData(f, this.vertexTexCoordBuffer,
            k, 2);
        this.setVertexData(f, this.vertexTranslationBuffer, b, 3)
    };
    f.bindBuffers = function(f) {
        f.bindBuffer(f.ARRAY_BUFFER, this.vertexPositionBuffer);
        f.vertexAttribPointer(f.shader.vertexPositionAttribute, this.vertexPositionBuffer.itemSize, f.FLOAT, !1, 0, 0);
        f.bindBuffer(f.ARRAY_BUFFER, this.vertexTexCoordBuffer);
        f.vertexAttribPointer(f.shader.vertexTexCoordAttribute, this.vertexTexCoordBuffer.itemSize, f.FLOAT, !1, 0, 0);
        f.bindBuffer(f.ARRAY_BUFFER, this.vertexTranslationBuffer);
        f.vertexAttribPointer(f.shader.vertexNormalAttribute,
            this.vertexTranslationBuffer.itemSize, f.FLOAT, !1, 0, 0)
    };
    f.render = function(f) {
        let e = this.vertexPositionBuffer.numItems;
        e && (this.bindBuffers(f), f.drawArrays(f.TRIANGLES, 0, e))
    }
})(ChemDoodle.structures.d3, Math);
(function(f, q, l, t, e, k, b) {
    l.Torsion = function(b, e, a, g) {
        this.a1 = b;
        this.a2 = e;
        this.a3 = a;
        this.a4 = g
    };
    f = l.Torsion.prototype = new l._Measurement;
    f.calculateData = function(d) {
        let e = [],
            a = [],
            g = [];
        var f = this.a2.distance3D(this.a1),
            l = this.a2.distance3D(this.a3);
        this.distUse = t.min(f, l) / 2;
        l = [this.a2.x - this.a1.x, this.a2.y - this.a1.y, this.a2.z - this.a1.z];
        f = [this.a3.x - this.a2.x, this.a3.y - this.a2.y, this.a3.z - this.a2.z];
        var m = [this.a4.x - this.a3.x, this.a4.y - this.a3.y, this.a4.z - this.a3.z],
            q = k.cross(l, f, []);
        m = k.cross(f, m, []);
        k.scale(l, k.length(f));
        this.torsion = t.atan2(k.dot(l, m), k.dot(q, m));
        q = k.normalize(k.cross(q, f, []));
        l = k.normalize(k.cross(f, q, []));
        this.pos = k.add([this.a2.x, this.a2.y, this.a2.z], k.scale(k.normalize(f, []), this.distUse));
        m = [];
        let u = d.measurement_angleBands_3D;
        var w = b;
        for (d = 0; d <= u; ++d) {
            var z = this.torsion * d / u;
            w = k.scale(q, t.cos(z), []);
            z = k.scale(l, t.sin(z), []);
            w = k.scale(k.normalize(k.add(w, z, [])), this.distUse);
            0 == d && (m = w);
            e.push(this.pos[0] + w[0], this.pos[1] + w[1], this.pos[2] + w[2]);
            a.push(0, 0, 0);
            d < u && g.push(d,
                d + 1)
        }
        this.vecText = k.normalize(k.add(m, w, []));
        f = k.normalize(f, []);
        k.scale(f, .0625);
        m = this.torsion - 2 * t.asin(.125) * this.torsion / t.abs(this.torsion);
        q = k.scale(q, t.cos(m), []);
        l = k.scale(l, t.sin(m), []);
        w = k.scale(k.normalize(k.add(q, l, [])), this.distUse);
        e.push(this.pos[0] + f[0] + w[0], this.pos[1] + f[1] + w[1], this.pos[2] + f[2] + w[2]);
        a.push(0, 0, 0);
        e.push(this.pos[0] - f[0] + w[0], this.pos[1] - f[1] + w[1], this.pos[2] - f[2] + w[2]);
        a.push(0, 0, 0);
        g.push(--d, d + 1, d, d + 2);
        this.storeData(e, a, g)
    };
    f.getText = function(b) {
        k.add(this.pos,
            k.scale(this.vecText, this.distUse + .3, []));
        return {
            pos: this.pos,
            value: [q.angleBounds(this.torsion, !0, !0).toFixed(2), " \u00b0"].join("")
        }
    }
})(ChemDoodle.ELEMENT, ChemDoodle.math, ChemDoodle.structures.d3, Math, ChemDoodle.lib.mat4, ChemDoodle.lib.vec3);
(function(f, q, l, t, e, k, b, d, h) {
    let a = function(a, b) {
            a.bindBuffer(a.ARRAY_BUFFER, b.vertexPositionBuffer);
            a.vertexAttribPointer(a.shader.vertexPositionAttribute, b.vertexPositionBuffer.itemSize, a.FLOAT, !1, 0, 0);
            a.bindBuffer(a.ARRAY_BUFFER, b.vertexNormalBuffer);
            a.vertexAttribPointer(a.shader.vertexNormalAttribute, b.vertexNormalBuffer.itemSize, a.FLOAT, !1, 0, 0);
            a.bindBuffer(a.ELEMENT_ARRAY_BUFFER, b.vertexIndexBuffer)
        },
        g = function(a, b, d) {
            let g = e.sqrt(b[1] * b[1] + b[2] * b[2]),
                f = [1, 0, 0, 0, 0, b[2] / g, -b[1] / g, 0, 0, b[1] / g,
                    b[2] / g, 0, 0, 0, 0, 1
                ],
                h = [1, 0, 0, 0, 0, b[2] / g, b[1] / g, 0, 0, -b[1] / g, b[2] / g, 0, 0, 0, 0, 1],
                n = [g, 0, -b[0], 0, 0, 1, 0, 0, b[0], 0, g, 0, 0, 0, 0, 1];
            b = [g, 0, b[0], 0, 0, 1, 0, 0, -b[0], 0, g, 0, 0, 0, 0, 1];
            d = [e.cos(d), -e.sin(d), 0, 0, e.sin(d), e.cos(d), 0, 0, 0, 0, 1, 0, 0, 0, 0, 1];
            let m = k.multiply(f, k.multiply(n, k.multiply(d, k.multiply(b, h, []))));
            this.rotate = function() {
                return k.multiplyVec3(m, a)
            }
        };
    t.Tube = function(h, v, m) {
        var n = h[0].lineSegments[0].length;
        this.partitions = [];
        this.ends = [];
        this.ends.push(h[0].lineSegments[0][0]);
        this.ends.push(h[h.length - 1].lineSegments[0][0]);
        var u = [1, 0, 0];
        for (let a = 0, d = h.length; a < d; a++) {
            if (!w || 65E3 < w.positionData.length) {
                0 < this.partitions.length && a--;
                var w = {
                    count: 0,
                    positionData: [],
                    normalData: [],
                    indexData: []
                };
                this.partitions.push(w)
            }
            var t = h[a];
            w.count++;
            var y = Infinity,
                c = new l.Atom("", h[a].cp1.x, h[a].cp1.y, h[a].cp1.z);
            for (let d = 0; d < n; d++) {
                let f = t.lineSegments[0][d];
                var p = d === n - 1 ? a === h.length - 1 ? t.lineSegments[0][d - 1] : h[a + 1].lineSegments[0][0] : t.lineSegments[0][d + 1];
                p = [p.x - f.x, p.y - f.y, p.z - f.z];
                b.normalize(p);
                a === h.length - 1 && d === n - 1 && b.scale(p,
                    -1);
                var A = b.cross(p, u, []);
                b.normalize(A);
                b.scale(A, v / 2);
                p = new g(A, p, 2 * Math.PI / m);
                for (let a = 0, b = m; a < b; a++) A = p.rotate(), a === e.floor(m / 4) && (u = [A[0], A[1], A[2]]), w.normalData.push(A[0], A[1], A[2]), w.positionData.push(f.x + A[0], f.y + A[1], f.z + A[2]);
                c && (p = f.distance3D(c), p < y && (y = p, h[a].pPoint = f))
            }
        }
        for (let a = 0, b = this.partitions.length; a < b; a++) {
            w = this.partitions[a];
            for (let a = 0, b = w.count - 1; a < b; a++) {
                u = a * n * m;
                for (let a = 0, b = n; a < b; a++)
                    for (t = u + a * m, y = 0; y < m; y++) c = t + y, w.indexData.push(c), w.indexData.push(c + m), w.indexData.push(c +
                        m + 1), w.indexData.push(c), w.indexData.push(c + m + 1), w.indexData.push(c + 1)
            }
        }
        this.storeData(this.partitions[0].positionData, this.partitions[0].normalData, this.partitions[0].indexData);
        m = [new l.Point(2, 0)];
        for (n = 0; 60 > n; n++) w = n / 60 * e.PI, m.push(new l.Point(2 * e.cos(w), -2 * e.sin(w)));
        m.push(new l.Point(-2, 0), new l.Point(-2, 4), new l.Point(2, 4));
        let B = new l.d3.Shape(m, 1);
        this.render = function(c, g) {
            this.bindBuffers(c);
            c.material.setDiffuseColor(c, g.macro_colorByChain ? this.chainColor : g.nucleics_tubeColor);
            c.drawElements(c.TRIANGLES,
                this.vertexIndexBuffer.numItems, c.UNSIGNED_SHORT, 0);
            if (this.partitions)
                for (let b = 1, d = this.partitions.length; b < d; b++) {
                    var n = this.partitions[b];
                    a(c, n);
                    c.drawElements(c.TRIANGLES, n.vertexIndexBuffer.numItems, c.UNSIGNED_SHORT, 0)
                }
            c.sphereBuffer.bindBuffers(c);
            for (n = 0; 2 > n; n++) {
                var m = this.ends[n];
                m = k.translate(k.identity(), [m.x, m.y, m.z]);
                var p = v / 2;
                k.scale(m, [p, p, p]);
                c.shader.setMatrixUniforms(c, m);
                c.drawElements(c.TRIANGLES, c.sphereBuffer.vertexIndexBuffer.numItems, c.UNSIGNED_SHORT, 0)
            }
            c.cylinderBuffer.bindBuffers(c);
            for (let a = 0, d = h.length - 1; a < d; a++) {
                m = h[a];
                n = m.pPoint;
                m = new l.Atom("", m.cp2.x, m.cp2.y, m.cp2.z);
                p = 1.001 * n.distance3D(m);
                p = [v / 4, p, v / 4];
                var u = k.translate(k.identity(), [n.x, n.y, n.z]),
                    w = [0, 1, 0],
                    t = 0,
                    x = [m.x - n.x, m.y - n.y, m.z - n.z];
                n.x === m.x && n.z === m.z ? (m = [0, 0, 1], n.y < n.y && (t = e.PI)) : (t = f.vec3AngleFrom(w, x), m = b.cross(w, x, []));
                0 !== t && k.rotate(u, t, m);
                k.scale(u, p);
                c.shader.setMatrixUniforms(c, u);
                c.drawArrays(c.TRIANGLE_STRIP, 0, c.cylinderBuffer.vertexPositionBuffer.numItems)
            }
            B.bindBuffers(c);
            "none" !== g.nucleics_residueColor ||
                g.macro_colorByChain || c.material.setDiffuseColor(c, g.nucleics_baseColor);
            for (let a = 0, l = h.length - 1; a < l; a++)
                if (n = h[a], u = n.cp2, m = k.translate(k.identity(), [u.x, u.y, u.z]), w = [0, 1, 0], t = 0, x = n.cp3) {
                    p = [x.x - u.x, x.y - u.y, x.z - u.z];
                    u.x === x.x && u.z === x.z ? (w = [0, 0, 1], u.y < u.y && (t = e.PI)) : (t = f.vec3AngleFrom(w, p), w = b.cross(w, p, []));
                    0 !== t && k.rotate(m, t, w);
                    u = [1, 0, 0];
                    t = k.rotate(k.identity([]), t, w);
                    k.multiplyVec3(t, u);
                    t = n.cp4;
                    w = n.cp5;
                    if (t.y !== w.y || t.z !== w.z) t = [w.x - t.x, w.y - t.y, w.z - t.z], w = f.vec3AngleFrom(u, t), 0 > b.dot(p, b.cross(u,
                        t)) && (w *= -1), k.rotateY(m, w);
                    g.macro_colorByChain || ("shapely" === g.nucleics_residueColor ? q[n.name] ? c.material.setDiffuseColor(c, q[n.name].shapelyColor) : c.material.setDiffuseColor(c, q["*"].shapelyColor) : "rainbow" === g.nucleics_residueColor && c.material.setDiffuseColor(c, d.rainbowAt(a, l, g.macro_rainbowColors)));
                    c.shader.setMatrixUniforms(c, m);
                    c.drawElements(c.TRIANGLES, B.vertexIndexBuffer.numItems, c.UNSIGNED_SHORT, 0)
                }
        }
    };
    t.Tube.prototype = new t._Mesh;
    t.CatmullTube = function(a, d, f, h) {
        var k = [];
        a.push(a[a.length -
            1]);
        for (let b = 0, d = a.length - 2; b <= d; b++) {
            var n = a[0 == b ? 0 : b - 1],
                m = a[b + 0],
                v = a[b + 1],
                c = a[b == d ? b + 1 : b + 2],
                p = [];
            for (let a = 0; a < h; a++) {
                var t = a / h;
                b == d && (t = a / (h - 1));
                t = new l.Atom("C", .5 * (2 * m.x + (v.x - n.x) * t + (2 * n.x - 5 * m.x + 4 * v.x - c.x) * t * t + (3 * m.x - n.x - 3 * v.x + c.x) * t * t * t), .5 * (2 * m.y + (v.y - n.y) * t + (2 * n.y - 5 * m.y + 4 * v.y - c.y) * t * t + (3 * m.y - n.y - 3 * v.y + c.y) * t * t * t), .5 * (2 * m.z + (v.z - n.z) * t + (2 * n.z - 5 * m.z + 4 * v.z - c.z) * t * t + (3 * m.z - n.z - 3 * v.z + c.z) * t * t * t));
                p.push(t)
            }
            k.push(p)
        }
        a = k[0].length;
        this.partitions = [];
        this.ends = [];
        this.ends.push(k[0][0]);
        this.ends.push(k[k.length -
            1][0]);
        h = [1, 0, 0];
        for (let l = 0, u = k.length; l < u; l++) {
            if (!q || 65E3 < q.positionData.length) {
                0 < this.partitions.length && l--;
                var q = {
                    count: 0,
                    positionData: [],
                    normalData: [],
                    indexData: []
                };
                this.partitions.push(q)
            }
            n = k[l];
            q.count++;
            for (m = 0; m < a; m++) {
                v = n[m];
                c = m === a - 1 ? l === k.length - 1 ? n[m - 1] : k[l + 1][0] : n[m + 1];
                c = [c.x - v.x, c.y - v.y, c.z - v.z];
                b.normalize(c);
                l === k.length - 1 && m === a - 1 && b.scale(c, -1);
                p = b.cross(c, h, []);
                b.normalize(p);
                b.scale(p, d / 2);
                c = new g(p, c, 2 * Math.PI / f);
                for (let a = 0, b = f; a < b; a++) p = c.rotate(), a === e.floor(f / 4) && (h = [p[0],
                    p[1], p[2]
                ]), q.normalData.push(p[0], p[1], p[2]), q.positionData.push(v.x + p[0], v.y + p[1], v.z + p[2])
            }
        }
        for (let b = 0, c = this.partitions.length; b < c; b++) {
            d = this.partitions[b];
            for (let b = 0, c = d.count - 1; b < c; b++) {
                k = b * a * f;
                for (let b = 0, c = a; b < c; b++)
                    for (q = k + b * f, h = 0; h <= f; h++) n = q + h % f, d.indexData.push(n, n + f)
            }
        }
        this.storeData(this.partitions[0].positionData, this.partitions[0].normalData, this.partitions[0].indexData)
    };
    (t.CatmullTube.prototype = new t._Mesh).render = function(b, d) {
        this.bindBuffers(b);
        for (let d = 0, e = this.partitions.length; d <
            e; d++) {
            var g = this.partitions[d];
            a(b, g);
            b.drawElements(b.TRIANGLE_STRIP, g.vertexIndexBuffer.numItems, b.UNSIGNED_SHORT, 0)
        }
        b.sphereBuffer.bindBuffers(b);
        for (g = 0; 2 > g; g++) {
            var e = this.ends[g];
            e = k.translate(k.identity(), [e.x, e.y, e.z]);
            let a = d.proteins_tubeThickness / 2;
            k.scale(e, [a, a, a]);
            b.shader.setMatrixUniforms(b, e);
            b.drawElements(b.TRIANGLES, b.sphereBuffer.vertexIndexBuffer.numItems, b.UNSIGNED_SHORT, 0)
        }
    }
})(ChemDoodle.extensions, ChemDoodle.RESIDUE, ChemDoodle.structures, ChemDoodle.structures.d3, Math, ChemDoodle.lib.mat4,
    ChemDoodle.lib.vec3, ChemDoodle.math);
(function(f, q, l, t, e) {
    f.UnitCell = function(e, b, d) {
        this.lengths = e;
        this.angles = b;
        this.offset = d;
        e = q.CIFInterpreter.generateABC2XYZ(e[0], e[1], e[2], b[0], b[1], b[2]);
        d || (this.offset = [0, 0, 0]);
        this.unitCellVectors = {
            o: l.multiplyVec3(e, this.offset, []),
            x: l.multiplyVec3(e, [this.offset[0] + 1, this.offset[1], this.offset[2]]),
            y: l.multiplyVec3(e, [this.offset[0], this.offset[1] + 1, this.offset[2]]),
            z: l.multiplyVec3(e, [this.offset[0], this.offset[1], this.offset[2] + 1]),
            xy: l.multiplyVec3(e, [this.offset[0] + 1, this.offset[1] + 1,
                this.offset[2]
            ]),
            xz: l.multiplyVec3(e, [this.offset[0] + 1, this.offset[1], this.offset[2] + 1]),
            yz: l.multiplyVec3(e, [this.offset[0], this.offset[1] + 1, this.offset[2] + 1]),
            xyz: l.multiplyVec3(e, [this.offset[0] + 1, this.offset[1] + 1, this.offset[2] + 1])
        };
        let f = [],
            a = [];
        d = function(b, d, e, h) {
            f.push(b[0], b[1], b[2]);
            f.push(d[0], d[1], d[2]);
            f.push(e[0], e[1], e[2]);
            f.push(h[0], h[1], h[2]);
            for (b = 0; 4 > b; b++) a.push(0, 0, 0)
        };
        d(this.unitCellVectors.o, this.unitCellVectors.x, this.unitCellVectors.xy, this.unitCellVectors.y);
        d(this.unitCellVectors.o,
            this.unitCellVectors.y, this.unitCellVectors.yz, this.unitCellVectors.z);
        d(this.unitCellVectors.o, this.unitCellVectors.z, this.unitCellVectors.xz, this.unitCellVectors.x);
        d(this.unitCellVectors.yz, this.unitCellVectors.y, this.unitCellVectors.xy, this.unitCellVectors.xyz);
        d(this.unitCellVectors.xyz, this.unitCellVectors.xz, this.unitCellVectors.z, this.unitCellVectors.yz);
        d(this.unitCellVectors.xy, this.unitCellVectors.x, this.unitCellVectors.xz, this.unitCellVectors.xyz);
        d = [];
        for (e = 0; 6 > e; e++) b = 4 * e, d.push(b, b +
            1, b + 1, b + 2, b + 2, b + 3, b + 3, b);
        this.storeData(f, a, d)
    };
    (f.UnitCell.prototype = new f._Mesh).render = function(e, b) {
        e.shader.setMatrixUniforms(e);
        this.bindBuffers(e);
        e.material.setDiffuseColor(e, b.shapes_color);
        e.lineWidth(b.shapes_lineWidth);
        e.drawElements(e.LINES, this.vertexIndexBuffer.numItems, e.UNSIGNED_SHORT, 0)
    }
})(ChemDoodle.structures.d3, ChemDoodle.io, ChemDoodle.lib.mat4, ChemDoodle.lib.vec3);
(function(f, q, l, t) {
    f.Framebuffer = function() {};
    f = f.Framebuffer.prototype;
    f.init = function(e) {
        this.framebuffer = e.createFramebuffer()
    };
    f.setColorTexture = function(e, f, b) {
        b = b === t ? 0 : b;
        e.bindFramebuffer(e.FRAMEBUFFER, this.framebuffer);
        e.bindTexture(e.TEXTURE_2D, f);
        e.framebufferTexture2D(e.FRAMEBUFFER, e.COLOR_ATTACHMENT0 + b, e.TEXTURE_2D, f, 0);
        e.bindTexture(e.TEXTURE_2D, null);
        e.bindFramebuffer(e.FRAMEBUFFER, null)
    };
    f.setColorRenderbuffer = function(e, f, b) {
        b = b === t ? 0 : b;
        e.bindFramebuffer(e.FRAMEBUFFER, this.framebuffer);
        e.bindRenderbuffer(e.RENDERBUFFER, f);
        e.framebufferRenderbuffer(e.FRAMEBUFFER, e.COLOR_ATTACHMENT0 + b, e.RENDERBUFFER, f);
        e.bindRenderbuffer(e.RENDERBUFFER, null);
        e.bindFramebuffer(e.FRAMEBUFFER, null)
    };
    f.setDepthTexture = function(e, f) {
        e.bindFramebuffer(e.FRAMEBUFFER, this.framebuffer);
        e.bindTexture(e.TEXTURE_2D, f);
        e.framebufferTexture2D(e.FRAMEBUFFER, e.DEPTH_ATTACHMENT, e.TEXTURE_2D, f, 0);
        e.bindTexture(e.TEXTURE_2D, null);
        e.bindFramebuffer(e.FRAMEBUFFER, null)
    };
    f.setDepthRenderbuffer = function(e, f) {
        e.bindFramebuffer(e.FRAMEBUFFER,
            this.framebuffer);
        e.bindRenderbuffer(e.RENDERBUFFER, f);
        e.framebufferRenderbuffer(e.FRAMEBUFFER, e.DEPTH_ATTACHMENT, e.RENDERBUFFER, f);
        e.bindRenderbuffer(e.RENDERBUFFER, null);
        e.bindFramebuffer(e.FRAMEBUFFER, null)
    };
    f.bind = function(e, f, b) {
        e.bindFramebuffer(e.FRAMEBUFFER, this.framebuffer);
        e.viewport(0, 0, f, b)
    }
})(ChemDoodle.structures.d3, ChemDoodle.math, document);
(function(f, q, l, t) {
    f.Renderbuffer = function() {};
    f = f.Renderbuffer.prototype;
    f.init = function(e, f) {
        this.renderbuffer = e.createRenderbuffer();
        this.format = f
    };
    f.setParameter = function(e, f, b) {
        this.width = f;
        this.height = b;
        e.bindRenderbuffer(e.RENDERBUFFER, this.renderbuffer);
        e.renderbufferStorage(e.RENDERBUFFER, this.format, this.width, this.height);
        e.bindRenderbuffer(e.RENDERBUFFER, null)
    }
})(ChemDoodle.structures.d3, ChemDoodle.math, document);
(function(f, q, l, t) {
    q.SSAO = function() {};
    f = q.SSAO.prototype;
    f.initSampleKernel = function(e) {
        let f = [];
        for (let d = 0; d < e; d++) {
            let h = 2 * l.random() - 1,
                a = 2 * l.random() - 1,
                g = 2 * l.random() - 1;
            var b = d / e;
            b = .1 + b * b * .9;
            h *= b;
            a *= b;
            g *= b;
            f.push(h, a, g)
        }
        this.sampleKernel = new Float32Array(f)
    };
    f.initNoiseTexture = function(e) {
        let f = [];
        for (let b = 0; 16 > b; b++) f.push(2 * l.random() - 1), f.push(2 * l.random() - 1), f.push(0);
        this.noiseTexture = e.createTexture();
        e.bindTexture(e.TEXTURE_2D, this.noiseTexture);
        e.texImage2D(e.TEXTURE_2D, 0, e.RGB, 4, 4,
            0, e.RGB, e.FLOAT, new Float32Array(f));
        e.texParameteri(e.TEXTURE_2D, e.TEXTURE_MIN_FILTER, e.NEAREST);
        e.texParameteri(e.TEXTURE_2D, e.TEXTURE_MAG_FILTER, e.NEAREST);
        e.texParameteri(e.TEXTURE_2D, e.TEXTURE_WRAP_S, e.REPEAT);
        e.texParameteri(e.TEXTURE_2D, e.TEXTURE_WRAP_T, e.REPEAT);
        e.bindTexture(e.TEXTURE_2D, null)
    }
})(ChemDoodle.math, ChemDoodle.structures.d3, Math);
(function(f, q, l, t) {
    f.Texture = function() {};
    f = f.Texture.prototype;
    f.init = function(e, f, b, d) {
        this.texture = e.createTexture();
        this.type = f;
        this.internalFormat = b;
        this.format = d !== t ? d : b;
        e.bindTexture(e.TEXTURE_2D, this.texture);
        e.texParameteri(e.TEXTURE_2D, e.TEXTURE_MAG_FILTER, e.NEAREST);
        e.texParameteri(e.TEXTURE_2D, e.TEXTURE_MIN_FILTER, e.NEAREST);
        e.texParameteri(e.TEXTURE_2D, e.TEXTURE_WRAP_S, e.CLAMP_TO_EDGE);
        e.texParameteri(e.TEXTURE_2D, e.TEXTURE_WRAP_T, e.CLAMP_TO_EDGE);
        e.bindTexture(e.TEXTURE_2D, null)
    };
    f.setParameter =
        function(e, f, b) {
            this.width = f;
            this.height = b;
            e.bindTexture(e.TEXTURE_2D, this.texture);
            e.texImage2D(e.TEXTURE_2D, 0, this.internalFormat, this.width, this.height, 0, this.format, this.type, null);
            e.bindTexture(e.TEXTURE_2D, null)
        }
})(ChemDoodle.structures.d3, ChemDoodle.math, document);
(function(f, q, l, t, e) {
    f._Shader = function() {};
    f = f._Shader.prototype;
    f.useShaderProgram = function(e) {
        e.useProgram(this.gProgram);
        e.shader = this
    };
    f.init = function(e) {
        let b = this.getShader(e, "vertex-shader");
        b || (b = this.loadDefaultVertexShader(e));
        let d = this.getShader(e, "fragment-shader");
        d || (d = this.loadDefaultFragmentShader(e));
        this.gProgram = e.createProgram();
        e.attachShader(this.gProgram, b);
        e.attachShader(this.gProgram, d);
        this.onShaderAttached(e);
        e.linkProgram(this.gProgram);
        e.getProgramParameter(this.gProgram,
            e.LINK_STATUS) || alert("Could not initialize shaders: " + e.getProgramInfoLog(this.gProgram));
        e.useProgram(this.gProgram);
        this.initUniformLocations(e);
        e.useProgram(null)
    };
    f.onShaderAttached = function(e) {
        this.vertexPositionAttribute = 0;
        this.vertexNormalAttribute = 1;
        e.bindAttribLocation(this.gProgram, this.vertexPositionAttribute, "a_vertex_position");
        e.bindAttribLocation(this.gProgram, this.vertexNormalAttribute, "a_vertex_normal")
    };
    f.getShaderFromStr = function(f, b, d) {
        b = f.createShader(b);
        f.shaderSource(b, d);
        f.compileShader(b);
        return f.getShaderParameter(b, f.COMPILE_STATUS) ? b : (alert(shaderScript.type + " " + f.getShaderInfoLog(b)), f.deleteShader(b), e)
    };
    f.enableAttribsArray = function(e) {
        e.enableVertexAttribArray(this.vertexPositionAttribute)
    };
    f.disableAttribsArray = function(e) {
        e.disableVertexAttribArray(this.vertexPositionAttribute)
    };
    f.getShader = function(f, b) {
        b = t.getElementById(b);
        if (!b) return e;
        var d = [];
        let h = b.firstChild;
        for (; h;) 3 === h.nodeType && d.push(h.textContent), h = h.nextSibling;
        d = d.join("");
        if ("x-shader/x-fragment" ===
            b.type) f = this.getShaderFromStr(f, f.FRAGMENT_SHADER, d);
        else if ("x-shader/x-vertex" === b.type) f = this.getShaderFromStr(f, f.VERTEX_SHADER, d);
        else return e;
        return f
    };
    f.initUniformLocations = function(e) {
        this.modelViewMatrixUniform = e.getUniformLocation(this.gProgram, "u_model_view_matrix");
        this.projectionMatrixUniform = e.getUniformLocation(this.gProgram, "u_projection_matrix")
    };
    f.loadDefaultVertexShader = function(e) {};
    f.loadDefaultFragmentShader = function(e) {};
    f.setMatrixUniforms = function(f, b) {
        b === e ? this.setModelViewMatrix(f,
            f.modelViewMatrix) : this.setModelViewMatrix(f, l.multiply(f.modelViewMatrix, b, []))
    };
    f.setProjectionMatrix = function(e, b) {
        e.uniformMatrix4fv(this.projectionMatrixUniform, !1, b)
    };
    f.setModelViewMatrix = function(e, b) {
        e.uniformMatrix4fv(this.modelViewMatrixUniform, !1, b)
    };
    f.setMaterialAmbientColor = function(e, b) {};
    f.setMaterialDiffuseColor = function(e, b) {};
    f.setMaterialSpecularColor = function(e, b) {};
    f.setMaterialShininess = function(e, b) {};
    f.setMaterialAlpha = function(e, b) {}
})(ChemDoodle.structures.d3, ChemDoodle.lib.mat3,
    ChemDoodle.lib.mat4, document);
(function(f, q, l, t, e) {
    f.FXAAShader = function() {};
    let k = f._Shader.prototype;
    f = f.FXAAShader.prototype = new f._Shader;
    f.initUniformLocations = function(b) {
        k.initUniformLocations.call(this, b);
        this.buffersizeUniform = b.getUniformLocation(this.gProgram, "u_buffersize");
        this.antialiasUniform = b.getUniformLocation(this.gProgram, "u_antialias");
        this.edgeThresholdUniform = b.getUniformLocation(this.gProgram, "u_edge_threshold");
        this.edgeThresholdMinUniform = b.getUniformLocation(this.gProgram, "u_edge_threshold_min");
        this.searchStepsUniform =
            b.getUniformLocation(this.gProgram, "u_search_steps");
        this.searchThresholdUniform = b.getUniformLocation(this.gProgram, "u_search_threshold");
        this.subpixCapUniform = b.getUniformLocation(this.gProgram, "u_subpix_cap");
        this.subpixTrimUniform = b.getUniformLocation(this.gProgram, "u_subpix_trim")
    };
    f.setBuffersize = function(b, d, e) {
        b.uniform2f(this.buffersizeUniform, d, e)
    };
    f.setAntialias = function(b, d) {
        b.uniform1f(this.antialiasUniform, d)
    };
    f.setEdgeThreshold = function(b, d) {
        b.uniform1f(this.edgeThresholdUniform, d)
    };
    f.setEdgeThresholdMin = function(b, d) {
        b.uniform1f(this.edgeThresholdMinUniform, d)
    };
    f.setSearchSteps = function(b, d) {
        b.uniform1i(this.searchStepsUniform, d)
    };
    f.setSearchThreshold = function(b, d) {
        b.uniform1f(this.searchThresholdUniform, d)
    };
    f.setSubpixCap = function(b, d) {
        b.uniform1f(this.subpixCapUniform, d)
    };
    f.setSubpixTrim = function(b, d) {
        b.uniform1f(this.subpixTrimUniform, d)
    };
    f.loadDefaultVertexShader = function(b) {
        return this.getShaderFromStr(b, b.VERTEX_SHADER, "precision mediump float;attribute vec3 a_vertex_position;varying vec2 v_texcoord;void main() {gl_Position \x3d vec4(a_vertex_position, 1.);v_texcoord \x3d a_vertex_position.xy * .5 + .5;}")
    };
    f.loadDefaultFragmentShader = function(b) {
        return this.getShaderFromStr(b, b.FRAGMENT_SHADER, "precision mediump float;\nconst int fxaaMaxSearchSteps \x3d 128;\nuniform float u_edge_threshold;\nuniform float u_edge_threshold_min;\nuniform int u_search_steps;\nuniform float u_search_threshold;\nuniform float u_subpix_cap;\nuniform float u_subpix_trim;\nuniform sampler2D u_sampler0;\nuniform vec2 u_buffersize;\nuniform bool u_antialias;\nvarying vec2 v_texcoord;\nfloat FxaaLuma(vec3 rgb) {\nreturn rgb.y * (0.587/0.299) + rgb.x;\n}\nvec3 FxaaLerp3(vec3 a, vec3 b, float amountOfA) {\nreturn (vec3(-amountOfA) * b) + ((a * vec3(amountOfA)) + b);\n}\nvec4 FxaaTexOff(sampler2D tex, vec2 pos, vec2 off, vec2 rcpFrame) {\nreturn texture2D(tex, pos + off * rcpFrame);\n}\nvec3 FxaaPixelShader(vec2 pos, sampler2D tex, vec2 rcpFrame) {\nfloat subpix_trim_scale \x3d (1.0/(1.0 - u_subpix_trim));\nvec3 rgbN \x3d FxaaTexOff(tex, pos.xy, vec2( 0.,-1.), rcpFrame).xyz;\nvec3 rgbW \x3d FxaaTexOff(tex, pos.xy, vec2(-1., 0.), rcpFrame).xyz;\nvec3 rgbM \x3d FxaaTexOff(tex, pos.xy, vec2( 0., 0.), rcpFrame).xyz;\nvec3 rgbE \x3d FxaaTexOff(tex, pos.xy, vec2( 1., 0.), rcpFrame).xyz;\nvec3 rgbS \x3d FxaaTexOff(tex, pos.xy, vec2( 0., 1.), rcpFrame).xyz;\nfloat lumaN \x3d FxaaLuma(rgbN);\nfloat lumaW \x3d FxaaLuma(rgbW);\nfloat lumaM \x3d FxaaLuma(rgbM);\nfloat lumaE \x3d FxaaLuma(rgbE);\nfloat lumaS \x3d FxaaLuma(rgbS);\nfloat rangeMin \x3d min(lumaM, min(min(lumaN, lumaW), min(lumaS, lumaE)));\nfloat rangeMax \x3d max(lumaM, max(max(lumaN, lumaW), max(lumaS, lumaE)));\nfloat range \x3d rangeMax - rangeMin;\nif(range \x3c max(u_edge_threshold_min, rangeMax * u_edge_threshold)) {\nreturn rgbM;\n}\nvec3 rgbL \x3d rgbN + rgbW + rgbM + rgbE + rgbS;\nfloat lumaL \x3d (lumaN + lumaW + lumaE + lumaS) * 0.25;\nfloat rangeL \x3d abs(lumaL - lumaM);\nfloat blendL \x3d max(0.0, (rangeL / range) - u_subpix_trim) * subpix_trim_scale;\nblendL \x3d min(u_subpix_cap, blendL);\nvec3 rgbNW \x3d FxaaTexOff(tex, pos.xy, vec2(-1.,-1.), rcpFrame).xyz;\nvec3 rgbNE \x3d FxaaTexOff(tex, pos.xy, vec2( 1.,-1.), rcpFrame).xyz;\nvec3 rgbSW \x3d FxaaTexOff(tex, pos.xy, vec2(-1., 1.), rcpFrame).xyz;\nvec3 rgbSE \x3d FxaaTexOff(tex, pos.xy, vec2( 1., 1.), rcpFrame).xyz;\nrgbL +\x3d (rgbNW + rgbNE + rgbSW + rgbSE);\nrgbL *\x3d vec3(1.0/9.0);\nfloat lumaNW \x3d FxaaLuma(rgbNW);\nfloat lumaNE \x3d FxaaLuma(rgbNE);\nfloat lumaSW \x3d FxaaLuma(rgbSW);\nfloat lumaSE \x3d FxaaLuma(rgbSE);\nfloat edgeVert \x3d\nabs((0.25 * lumaNW) + (-0.5 * lumaN) + (0.25 * lumaNE)) +\nabs((0.50 * lumaW ) + (-1.0 * lumaM) + (0.50 * lumaE )) +\nabs((0.25 * lumaSW) + (-0.5 * lumaS) + (0.25 * lumaSE));\nfloat edgeHorz \x3d\nabs((0.25 * lumaNW) + (-0.5 * lumaW) + (0.25 * lumaSW)) +\nabs((0.50 * lumaN ) + (-1.0 * lumaM) + (0.50 * lumaS )) +\nabs((0.25 * lumaNE) + (-0.5 * lumaE) + (0.25 * lumaSE));\nbool horzSpan \x3d edgeHorz \x3e\x3d edgeVert;\nfloat lengthSign \x3d horzSpan ? -rcpFrame.y : -rcpFrame.x;\nif(!horzSpan) {\nlumaN \x3d lumaW;\nlumaS \x3d lumaE;\n}\nfloat gradientN \x3d abs(lumaN - lumaM);\nfloat gradientS \x3d abs(lumaS - lumaM);\nlumaN \x3d (lumaN + lumaM) * 0.5;\nlumaS \x3d (lumaS + lumaM) * 0.5;\nif (gradientN \x3c gradientS) {\nlumaN \x3d lumaS;\nlumaN \x3d lumaS;\ngradientN \x3d gradientS;\nlengthSign *\x3d -1.0;\n}\nvec2 posN;\nposN.x \x3d pos.x + (horzSpan ? 0.0 : lengthSign * 0.5);\nposN.y \x3d pos.y + (horzSpan ? lengthSign * 0.5 : 0.0);\ngradientN *\x3d u_search_threshold;\nvec2 posP \x3d posN;\nvec2 offNP \x3d horzSpan ? vec2(rcpFrame.x, 0.0) : vec2(0.0, rcpFrame.y);\nfloat lumaEndN \x3d lumaN;\nfloat lumaEndP \x3d lumaN;\nbool doneN \x3d false;\nbool doneP \x3d false;\nposN +\x3d offNP * vec2(-1.0, -1.0);\nposP +\x3d offNP * vec2( 1.0,  1.0);\nfor(int i \x3d 0; i \x3c fxaaMaxSearchSteps; i++) {\nif(i \x3e\x3d u_search_steps) break;\nif(!doneN) {\nlumaEndN \x3d FxaaLuma(texture2D(tex, posN.xy).xyz);\n}\nif(!doneP) {\nlumaEndP \x3d FxaaLuma(texture2D(tex, posP.xy).xyz);\n}\ndoneN \x3d doneN || (abs(lumaEndN - lumaN) \x3e\x3d gradientN);\ndoneP \x3d doneP || (abs(lumaEndP - lumaN) \x3e\x3d gradientN);\nif(doneN \x26\x26 doneP) {\nbreak;\n}\nif(!doneN) {\nposN -\x3d offNP;\n}\nif(!doneP) {\nposP +\x3d offNP;\n}\n}\nfloat dstN \x3d horzSpan ? pos.x - posN.x : pos.y - posN.y;\nfloat dstP \x3d horzSpan ? posP.x - pos.x : posP.y - pos.y;\nbool directionN \x3d dstN \x3c dstP;\nlumaEndN \x3d directionN ? lumaEndN : lumaEndP;\nif(((lumaM - lumaN) \x3c 0.0) \x3d\x3d ((lumaEndN - lumaN) \x3c 0.0)) {\nlengthSign \x3d 0.0;\n}\nfloat spanLength \x3d (dstP + dstN);\ndstN \x3d directionN ? dstN : dstP;\nfloat subPixelOffset \x3d (0.5 + (dstN * (-1.0/spanLength))) * lengthSign;\nvec3 rgbF \x3d texture2D(tex, vec2(\npos.x + (horzSpan ? 0.0 : subPixelOffset),\npos.y + (horzSpan ? subPixelOffset : 0.0))).xyz;\nreturn FxaaLerp3(rgbL, rgbF, blendL);\n}\nvoid main() {\ngl_FragColor \x3d texture2D(u_sampler0, v_texcoord);\nif(u_antialias) {\ngl_FragColor.xyz \x3d FxaaPixelShader(v_texcoord, u_sampler0, 1. / u_buffersize).xyz;\n}\n}")
    }
})(ChemDoodle.structures.d3,
    ChemDoodle.lib.mat3, ChemDoodle.lib.mat4, document);
(function(f, q, l, t, e) {
    f.LabelShader = function() {};
    let k = f._Shader.prototype;
    f = f.LabelShader.prototype = new f._Shader;
    f.initUniformLocations = function(b) {
        k.initUniformLocations.call(this, b);
        this.dimensionUniform = b.getUniformLocation(this.gProgram, "u_dimension")
    };
    f.onShaderAttached = function(b) {
        k.onShaderAttached.call(this, b);
        this.vertexTexCoordAttribute = 2;
        b.bindAttribLocation(this.gProgram, this.vertexTexCoordAttribute, "a_vertex_texcoord")
    };
    f.loadDefaultVertexShader = function(b) {
        return this.getShaderFromStr(b,
            b.VERTEX_SHADER, "precision mediump float;attribute vec3 a_vertex_position;attribute vec3 a_vertex_normal;attribute vec2 a_vertex_texcoord;uniform mat4 u_model_view_matrix;uniform mat4 u_projection_matrix;uniform vec2 u_dimension;varying vec2 v_texcoord;void main() {gl_Position \x3d u_model_view_matrix * vec4(a_vertex_position, 1.);vec4 depth_pos \x3d vec4(gl_Position);depth_pos.z +\x3d a_vertex_normal.z;gl_Position \x3d u_projection_matrix * gl_Position;depth_pos \x3d u_projection_matrix * depth_pos;gl_Position /\x3d gl_Position.w;gl_Position.xy +\x3d a_vertex_normal.xy / u_dimension * 2.;gl_Position.z \x3d depth_pos.z / depth_pos.w;v_texcoord \x3d a_vertex_texcoord;}")
    };
    f.loadDefaultFragmentShader = function(b) {
        let d = [b.depthTextureExt ? "#define CWC_DEPTH_TEX\n" : "", "precision mediump float;uniform sampler2D u_image;varying vec2 v_texcoord;void main(void) {gl_FragColor \x3d texture2D(u_image, v_texcoord);}"].join("");
        return this.getShaderFromStr(b, b.FRAGMENT_SHADER, d)
    };
    f.enableAttribsArray = function(b) {
        k.enableAttribsArray.call(this, b);
        b.enableVertexAttribArray(this.vertexNormalAttribute);
        b.enableVertexAttribArray(this.vertexTexCoordAttribute)
    };
    f.disableAttribsArray =
        function(b) {
            k.disableAttribsArray.call(this, b);
            b.disableVertexAttribArray(this.vertexNormalAttribute);
            b.disableVertexAttribArray(this.vertexTexCoordAttribute)
        };
    f.setDimension = function(b, d, e) {
        b.uniform2f(this.dimensionUniform, d, e)
    }
})(ChemDoodle.structures.d3, ChemDoodle.lib.mat3, ChemDoodle.lib.mat4, document);
(function(f, q, l, t, e) {
    f.LightingShader = function() {};
    let k = f._Shader.prototype;
    f = f.LightingShader.prototype = new f._Shader;
    f.initUniformLocations = function(b) {
        k.initUniformLocations.call(this, b);
        this.positionSampleUniform = b.getUniformLocation(this.gProgram, "u_position_sample");
        this.colorSampleUniform = b.getUniformLocation(this.gProgram, "u_color_sample");
        this.ssaoSampleUniform = b.getUniformLocation(this.gProgram, "u_ssao_sample");
        this.outlineSampleUniform = b.getUniformLocation(this.gProgram, "u_outline_sample")
    };
    f.loadDefaultVertexShader = function(b) {
        return this.getShaderFromStr(b, b.VERTEX_SHADER, "precision mediump float;attribute vec3 a_vertex_position;varying vec2 v_texcoord;void main() {gl_Position \x3d vec4(a_vertex_position, 1.);v_texcoord \x3d a_vertex_position.xy * .5 + .5;}")
    };
    f.loadDefaultFragmentShader = function(b) {
        return this.getShaderFromStr(b, b.FRAGMENT_SHADER, "precision mediump float;uniform sampler2D u_position_sample;uniform sampler2D u_color_sample;uniform sampler2D u_ssao_sample;uniform sampler2D u_outline_sample;varying vec2 v_texcoord;void main() {vec4 position \x3d texture2D(u_position_sample, v_texcoord);vec4 color \x3d texture2D(u_color_sample, v_texcoord);vec4 ao \x3d texture2D(u_ssao_sample, v_texcoord);float outline \x3d texture2D(u_outline_sample, v_texcoord).r;if(position.w \x3d\x3d 0. \x26\x26 outline \x3d\x3d 1.) {return;}gl_FragColor \x3d vec4(color.rgb * ao.r * outline, 1.);}")
    }
})(ChemDoodle.structures.d3,
    ChemDoodle.lib.mat3, ChemDoodle.lib.mat4, document);
(function(f, q, l, t, e) {
    f.NormalShader = function() {};
    let k = f._Shader.prototype;
    f = f.NormalShader.prototype = new f._Shader;
    f.initUniformLocations = function(b) {
        k.initUniformLocations.call(this, b);
        this.normalMatrixUniform = b.getUniformLocation(this.gProgram, "u_normal_matrix")
    };
    f.loadDefaultVertexShader = function(b) {
        return this.getShaderFromStr(b, b.VERTEX_SHADER, "precision mediump float;attribute vec3 a_vertex_position;attribute vec3 a_vertex_normal;uniform mat4 u_model_view_matrix;uniform mat4 u_projection_matrix;uniform mat3 u_normal_matrix;varying vec3 v_normal;void main() {v_normal \x3d length(a_vertex_normal)\x3d\x3d0. ? a_vertex_normal : u_normal_matrix * a_vertex_normal;gl_Position \x3d u_projection_matrix * u_model_view_matrix * vec4(a_vertex_position, 1.);}")
    };
    f.loadDefaultFragmentShader =
        function(b) {
            return this.getShaderFromStr(b, b.FRAGMENT_SHADER, "precision mediump float;varying vec3 v_normal;void main(void) {vec3 normal \x3d length(v_normal)\x3d\x3d0. ? vec3(0., 0., 1.) : normalize(v_normal);gl_FragColor \x3d vec4(normal, 0.);}")
        };
    f.enableAttribsArray = function(b) {
        k.enableAttribsArray.call(this, b);
        b.enableVertexAttribArray(this.vertexNormalAttribute)
    };
    f.disableAttribsArray = function(b) {
        k.disableAttribsArray.call(this, b);
        b.disableVertexAttribArray(this.vertexNormalAttribute)
    };
    f.setModelViewMatrix =
        function(b, d) {
            k.setModelViewMatrix.call(this, b, d);
            d = q.transpose(l.toInverseMat3(d, []));
            b.uniformMatrix3fv(this.normalMatrixUniform, !1, d)
        }
})(ChemDoodle.structures.d3, ChemDoodle.lib.mat3, ChemDoodle.lib.mat4, document);
(function(f, q, l, t, e) {
    f.OutlineShader = function() {};
    let k = f._Shader.prototype;
    f = f.OutlineShader.prototype = new f._Shader;
    f.initUniformLocations = function(b) {
        k.initUniformLocations.call(this, b);
        this.normalSampleUniform = b.getUniformLocation(this.gProgram, "u_normal_sample");
        this.depthSampleUniform = b.getUniformLocation(this.gProgram, "u_depth_sample");
        this.gbufferTextureSizeUniform = b.getUniformLocation(this.gProgram, "u_gbuffer_texture_size");
        this.normalThresholdUniform = b.getUniformLocation(this.gProgram, "u_normal_threshold");
        this.depthThresholdUniform = b.getUniformLocation(this.gProgram, "u_depth_threshold");
        this.thicknessUniform = b.getUniformLocation(this.gProgram, "u_thickness")
    };
    f.loadDefaultVertexShader = function(b) {
        return this.getShaderFromStr(b, b.VERTEX_SHADER, "precision mediump float;attribute vec3 a_vertex_position;varying vec2 v_texcoord;void main() {gl_Position \x3d vec4(a_vertex_position, 1.);v_texcoord \x3d a_vertex_position.xy * .5 + .5;}")
    };
    f.loadDefaultFragmentShader = function(b) {
        return this.getShaderFromStr(b,
            b.FRAGMENT_SHADER, "precision mediump float;uniform sampler2D u_normal_sample;uniform sampler2D u_depth_sample;uniform float u_normal_threshold;uniform float u_depth_threshold;uniform float u_thickness;uniform vec2 u_gbuffer_texture_size;varying vec2 v_texcoord;void main() {vec3 normal \x3d texture2D(u_normal_sample, v_texcoord).xyz;float depth \x3d texture2D(u_depth_sample, v_texcoord).r;vec2 texelSize \x3d u_thickness/u_gbuffer_texture_size * .5;vec2 offsets[8];offsets[0] \x3d vec2(-texelSize.x, -texelSize.y);offsets[1] \x3d vec2(-texelSize.x, 0);offsets[2] \x3d vec2(-texelSize.x, texelSize.y);offsets[3] \x3d vec2(0, -texelSize.y);offsets[4] \x3d vec2(0,  texelSize.y);offsets[5] \x3d vec2(texelSize.x, -texelSize.y);offsets[6] \x3d vec2(texelSize.x, 0);offsets[7] \x3d vec2(texelSize.x, texelSize.y);float edge \x3d 0.;for (int i \x3d 0; i \x3c 8; i++) {vec3 sampleNorm \x3d texture2D(u_normal_sample, v_texcoord + offsets[i]).xyz;if(normal \x3d\x3d vec3(.0, .0, .0)) {if(sampleNorm !\x3d vec3(.0, .0, .0)) {edge \x3d 1.0;break;}continue;}if (dot(sampleNorm, normal) \x3c u_normal_threshold) {edge \x3d 1.0;break;}float sampleDepth \x3d texture2D(u_depth_sample, v_texcoord + offsets[i]).r;if (abs(sampleDepth - depth) \x3e u_depth_threshold) {edge \x3d 1.0;break;}}edge \x3d 1. - edge;gl_FragColor \x3d vec4(edge, edge, edge, 1.);}")
    };
    f.setGbufferTextureSize = function(b, d, e) {
        b.uniform2f(this.gbufferTextureSizeUniform, d, e)
    };
    f.setNormalThreshold = function(b, d) {
        b.uniform1f(this.normalThresholdUniform, d)
    };
    f.setDepthThreshold = function(b, d) {
        b.uniform1f(this.depthThresholdUniform, d)
    };
    f.setThickness = function(b, d) {
        b.uniform1f(this.thicknessUniform, d)
    }
})(ChemDoodle.structures.d3, ChemDoodle.lib.mat3, ChemDoodle.lib.mat4, document);
(function(f, q, l, t, e) {
    f.PhongShader = function() {};
    let k = f._Shader.prototype;
    f = f.PhongShader.prototype = new f._Shader;
    f.initUniformLocations = function(b) {
        k.initUniformLocations.call(this, b);
        this.shadowUniform = b.getUniformLocation(this.gProgram, "u_shadow");
        this.flatColorUniform = b.getUniformLocation(this.gProgram, "u_flat_color");
        this.normalMatrixUniform = b.getUniformLocation(this.gProgram, "u_normal_matrix");
        this.lightModelViewMatrixUniform = b.getUniformLocation(this.gProgram, "u_light_model_view_matrix");
        this.lightProjectionMatrixUniform =
            b.getUniformLocation(this.gProgram, "u_light_projection_matrix");
        this.lightDiffuseColorUniform = b.getUniformLocation(this.gProgram, "u_light_diffuse_color");
        this.lightSpecularColorUniform = b.getUniformLocation(this.gProgram, "u_light_specular_color");
        this.lightDirectionUniform = b.getUniformLocation(this.gProgram, "u_light_direction");
        this.materialAmbientColorUniform = b.getUniformLocation(this.gProgram, "u_material_ambient_color");
        this.materialDiffuseColorUniform = b.getUniformLocation(this.gProgram, "u_material_diffuse_color");
        this.materialSpecularColorUniform = b.getUniformLocation(this.gProgram, "u_material_specular_color");
        this.materialShininessUniform = b.getUniformLocation(this.gProgram, "u_material_shininess");
        this.materialAlphaUniform = b.getUniformLocation(this.gProgram, "u_material_alpha");
        this.fogModeUniform = b.getUniformLocation(this.gProgram, "u_fog_mode");
        this.fogColorUniform = b.getUniformLocation(this.gProgram, "u_fog_color");
        this.fogStartUniform = b.getUniformLocation(this.gProgram, "u_fog_start");
        this.fogEndUniform = b.getUniformLocation(this.gProgram,
            "u_fog_end");
        this.fogDensityUniform = b.getUniformLocation(this.gProgram, "u_fog_density");
        this.shadowDepthSampleUniform = b.getUniformLocation(this.gProgram, "u_shadow_depth_sample");
        this.shadowTextureSizeUniform = b.getUniformLocation(this.gProgram, "u_shadow_texture_size");
        this.shadowIntensityUniform = b.getUniformLocation(this.gProgram, "u_shadow_intensity");
        this.gammaCorrectionUniform = b.getUniformLocation(this.gProgram, "u_gamma_inverted");
        this.pointSizeUniform = b.getUniformLocation(this.gProgram, "u_point_size")
    };
    f.loadDefaultVertexShader = function(b) {
        return this.getShaderFromStr(b, b.VERTEX_SHADER, "precision mediump float;attribute vec3 a_vertex_position;attribute vec3 a_vertex_normal;uniform vec3 u_light_diffuse_color;uniform vec3 u_material_ambient_color;uniform vec3 u_material_diffuse_color;uniform mat4 u_model_view_matrix;uniform mat4 u_projection_matrix;uniform mat3 u_normal_matrix;uniform mat4 u_light_model_view_matrix;uniform mat4 u_light_projection_matrix;uniform bool u_shadow;varying vec3 v_viewpos;varying vec4 v_shadcoord;varying vec3 v_diffuse;varying vec3 v_ambient;varying vec3 v_normal;uniform float u_point_size;void main() {v_normal \x3d length(a_vertex_normal)\x3d\x3d0. ? a_vertex_normal : u_normal_matrix * a_vertex_normal;v_ambient \x3d u_material_ambient_color;v_diffuse \x3d u_material_diffuse_color * u_light_diffuse_color;if(u_shadow) {v_shadcoord \x3d u_light_projection_matrix * u_light_model_view_matrix * vec4(a_vertex_position, 1.);v_shadcoord /\x3d v_shadcoord.w;}vec4 viewPos \x3d u_model_view_matrix * vec4(a_vertex_position, 1.);v_viewpos \x3d viewPos.xyz / viewPos.w;gl_Position \x3d u_projection_matrix * viewPos;gl_Position /\x3d gl_Position.w;gl_PointSize \x3d u_point_size;}")
    };
    f.loadDefaultFragmentShader = function(b) {
        let d = [b.depthTextureExt ? "#define CWC_DEPTH_TEX\n" : "", "precision mediump float;uniform vec3 u_light_specular_color;uniform vec3 u_light_direction;uniform vec3 u_material_specular_color;uniform float u_material_shininess;uniform float u_material_alpha;uniform int u_fog_mode;uniform vec3 u_fog_color;uniform float u_fog_density;uniform float u_fog_start;uniform float u_fog_end;uniform bool u_shadow;uniform float u_shadow_intensity;uniform bool u_flat_color;uniform float u_gamma_inverted;uniform sampler2D u_shadow_depth_sample;uniform vec2 u_shadow_texture_size;varying vec3 v_viewpos;varying vec4 v_shadcoord;varying vec3 v_diffuse;varying vec3 v_ambient;varying vec3 v_normal;\n#ifndef CWC_DEPTH_TEX\nfloat unpack (vec4 colour) {const vec4 bitShifts \x3d vec4(1.,1. / 255.,1. / (255. * 255.),1. / (255. * 255. * 255.));return dot(colour, bitShifts);}\n#endif\nfloat shadowMapDepth(vec4 shadowMapColor) {float zShadowMap;\n#ifdef CWC_DEPTH_TEX\nzShadowMap \x3d shadowMapColor.r;\n#else\nzShadowMap \x3d unpack(shadowMapColor);\n#endif\nreturn zShadowMap;}void main(void) {vec3 color \x3d v_diffuse;if(length(v_normal)!\x3d0.){vec3 normal \x3d normalize(v_normal);vec3 lightDir \x3d normalize(-u_light_direction);float nDotL \x3d dot(normal, lightDir);float shadow \x3d 0.0;if(u_shadow) {vec3 depthCoord \x3d .5 + v_shadcoord.xyz / v_shadcoord.w * .5;if(depthCoord.z \x3c\x3d 1. \x26\x26 depthCoord.z \x3e\x3d 0.) {float bias \x3d max(.05 * (1. - nDotL), .005);vec2 texelSize \x3d 1. / u_shadow_texture_size;for(int x \x3d -1; x \x3c\x3d 1; ++x) {for(int y \x3d -1; y \x3c\x3d 1; ++y)  {vec4 shadowMapColor \x3d texture2D(u_shadow_depth_sample, depthCoord.xy + vec2(x, y) * texelSize);float zShadowMap \x3d shadowMapDepth(shadowMapColor);shadow +\x3d zShadowMap + bias \x3c depthCoord.z ? 1. : 0.;}}shadow /\x3d 9.;shadow *\x3d u_shadow_intensity;}}if(!u_flat_color) {vec3 viewDir \x3d normalize(-v_viewpos);vec3 halfDir \x3d normalize(lightDir + viewDir);float nDotHV \x3d max(dot(halfDir, normal), 0.);vec3 specular \x3d u_material_specular_color * u_light_specular_color;color*\x3dmax(nDotL, 0.);color+\x3dspecular * pow(nDotHV, u_material_shininess);}color \x3d (1.-shadow)*color+v_ambient;}gl_FragColor \x3d vec4(pow(color, vec3(u_gamma_inverted)), u_material_alpha);if(u_fog_mode !\x3d 0){float fogCoord \x3d 1.-clamp((u_fog_end - gl_FragCoord.z/gl_FragCoord.w) / (u_fog_end - u_fog_start), 0., 1.);float fogFactor \x3d 1.;if(u_fog_mode \x3d\x3d 1){fogFactor \x3d 1.-fogCoord;}else if(u_fog_mode \x3d\x3d 2) {fogFactor \x3d clamp(exp(-u_fog_density*fogCoord), 0., 1.);}else if(u_fog_mode \x3d\x3d 3) {fogFactor \x3d clamp(exp(-pow(u_fog_density*fogCoord, 2.)), 0., 1.);}gl_FragColor \x3d mix(vec4(u_fog_color, 1.), gl_FragColor, fogFactor);}}"].join("");
        return this.getShaderFromStr(b, b.FRAGMENT_SHADER, d)
    };
    f.enableAttribsArray = function(b) {
        k.enableAttribsArray.call(this, b);
        b.enableVertexAttribArray(this.vertexNormalAttribute)
    };
    f.disableAttribsArray = function(b) {
        k.disableAttribsArray.call(this, b);
        b.disableVertexAttribArray(this.vertexNormalAttribute)
    };
    f.setMatrixUniforms = function(b, d) {
        if (d === e) this.setModelViewMatrix(b, b.modelViewMatrix), this.setLightModelViewMatrix(b, b.lightViewMatrix);
        else {
            let e = l.multiply(b.modelViewMatrix, d, []);
            d = l.multiply(b.lightViewMatrix,
                d, []);
            this.setModelViewMatrix(b, e);
            this.setLightModelViewMatrix(b, d)
        }
    };
    f.setModelViewMatrix = function(b, d) {
        k.setModelViewMatrix.call(this, b, d);
        d = q.transpose(l.toInverseMat3(d, []));
        b.uniformMatrix3fv(this.normalMatrixUniform, !1, d)
    };
    f.setFlatColor = function(b, d) {
        b.uniform1i(this.flatColorUniform, d)
    };
    f.setShadow = function(b, d) {
        b.uniform1i(this.shadowUniform, d)
    };
    f.setFogMode = function(b, d) {
        b.uniform1i(this.fogModeUniform, d)
    };
    f.setFogColor = function(b, d) {
        b.uniform3fv(this.fogColorUniform, d)
    };
    f.setFogStart =
        function(b, d) {
            b.uniform1f(this.fogStartUniform, d)
        };
    f.setFogEnd = function(b, d) {
        b.uniform1f(this.fogEndUniform, d)
    };
    f.setFogDensity = function(b, d) {
        b.uniform1f(this.fogDensityUniform, d)
    };
    f.setMaterialAmbientColor = function(b, d) {
        b.uniform3fv(this.materialAmbientColorUniform, d)
    };
    f.setMaterialDiffuseColor = function(b, d) {
        b.uniform3fv(this.materialDiffuseColorUniform, d)
    };
    f.setMaterialSpecularColor = function(b, d) {
        b.uniform3fv(this.materialSpecularColorUniform, d)
    };
    f.setMaterialShininess = function(b, d) {
        b.uniform1f(this.materialShininessUniform,
            d)
    };
    f.setMaterialAlpha = function(b, d) {
        b.uniform1f(this.materialAlphaUniform, d)
    };
    f.setLightDiffuseColor = function(b, d) {
        b.uniform3fv(this.lightDiffuseColorUniform, d)
    };
    f.setLightSpecularColor = function(b, d) {
        b.uniform3fv(this.lightSpecularColorUniform, d)
    };
    f.setLightDirection = function(b, d) {
        b.uniform3fv(this.lightDirectionUniform, d)
    };
    f.setLightModelViewMatrix = function(b, d) {
        b.uniformMatrix4fv(this.lightModelViewMatrixUniform, !1, d)
    };
    f.setLightProjectionMatrix = function(b, d) {
        b.uniformMatrix4fv(this.lightProjectionMatrixUniform,
            !1, d)
    };
    f.setShadowTextureSize = function(b, d, e) {
        b.uniform2f(this.shadowTextureSizeUniform, d, e)
    };
    f.setShadowIntensity = function(b, d) {
        b.uniform1f(this.shadowIntensityUniform, d)
    };
    f.setGammaCorrection = function(b, d) {
        b.uniform1f(this.gammaCorrectionUniform, 1 / d)
    };
    f.setPointSize = function(b, d) {
        b.uniform1f(this.pointSizeUniform, d)
    }
})(ChemDoodle.structures.d3, ChemDoodle.lib.mat3, ChemDoodle.lib.mat4, document);
(function(f, q, l, t, e) {
    f.PickShader = function() {};
    let k = f._Shader.prototype;
    f = f.PickShader.prototype = new f._Shader;
    f.initUniformLocations = function(b) {
        k.initUniformLocations.call(this, b);
        this.materialDiffuseColorUniform = b.getUniformLocation(this.gProgram, "u_material_diffuse_color")
    };
    f.loadDefaultVertexShader = function(b) {
        return this.getShaderFromStr(b, b.VERTEX_SHADER, "precision mediump float;attribute vec3 a_vertex_position;uniform mat4 u_model_view_matrix;uniform mat4 u_projection_matrix;void main() {gl_Position \x3d u_projection_matrix * u_model_view_matrix * vec4(a_vertex_position, 1.);gl_Position /\x3d gl_Position.w;}")
    };
    f.loadDefaultFragmentShader = function(b) {
        let d = [b.depthTextureExt ? "#define CWC_DEPTH_TEX\n" : "", "precision mediump float;uniform vec3 u_material_diffuse_color;void main(void) {gl_FragColor \x3d vec4(u_material_diffuse_color, 1.);}"].join("");
        return this.getShaderFromStr(b, b.FRAGMENT_SHADER, d)
    };
    f.setMaterialDiffuseColor = function(b, d) {
        b.uniform3fv(this.materialDiffuseColorUniform, d)
    }
})(ChemDoodle.structures.d3, ChemDoodle.lib.mat3, ChemDoodle.lib.mat4, document);
(function(f, q, l, t, e) {
    f.PositionShader = function() {};
    f = f.PositionShader.prototype = new f._Shader;
    f.loadDefaultVertexShader = function(e) {
        return this.getShaderFromStr(e, e.VERTEX_SHADER, "precision mediump float;attribute vec3 a_vertex_position;uniform mat4 u_model_view_matrix;uniform mat4 u_projection_matrix;varying vec4 v_position;void main() {vec4 viewPos \x3d u_model_view_matrix * vec4(a_vertex_position, 1.);gl_Position \x3d u_projection_matrix * viewPos;v_position \x3d viewPos / viewPos.w;}")
    };
    f.loadDefaultFragmentShader =
        function(e) {
            return this.getShaderFromStr(e, e.FRAGMENT_SHADER, "precision mediump float;varying vec4 v_position;void main(void) {gl_FragColor \x3d v_position;}")
        }
})(ChemDoodle.structures.d3, ChemDoodle.lib.mat3, ChemDoodle.lib.mat4, document);
(function(f, q, l, t, e) {
    f.QuadShader = function() {};
    f = f.QuadShader.prototype = new f._Shader;
    f.loadDefaultVertexShader = function(e) {
        return this.getShaderFromStr(e, e.VERTEX_SHADER, "precision mediump float;attribute vec3 a_vertex_position;varying vec2 v_texcoord;void main() {gl_Position \x3d vec4(a_vertex_position, 1.);v_texcoord \x3d a_vertex_position.xy * .5 + .5;}")
    };
    f.loadDefaultFragmentShader = function(e) {
        return this.getShaderFromStr(e, e.FRAGMENT_SHADER, "precision mediump float;uniform sampler2D u_image;varying vec2 v_texcoord;void main() {gl_FragColor \x3d texture2D(u_image, v_texcoord);}")
    }
})(ChemDoodle.structures.d3,
    ChemDoodle.lib.mat3, ChemDoodle.lib.mat4, document);
(function(f, q, l, t, e, k, b) {
    function d(a, b, d, e, h, l) {
        d = a[0] * l + d - l;
        e = a[1] * l + e - l;
        a = a[2] * l + h - l;
        h = -1;
        for (let g = 0, f = b.length; g < f; g++)
            if (l = b[g], .001 > k.abs(l.x - d) && .001 > k.abs(l.y - e) && .001 > k.abs(l.z - a)) {
                h = g;
                break
            } - 1 == h && (h = b.length, b.push(new f.Atom("C", d, e, a)));
        return h
    }
    let h = function(a, b, d) {
        this.i1 = a;
        this.i2 = b;
        this.i3 = d
    };
    q._Surface = function() {};
    q = q._Surface.prototype = new q._Mesh;
    q.generate = function(a, b, d, e, f, h, k, l) {
        a = [];
        b = f[4] - e;
        for (d = 0; d < l; d++) {
            let d = f[2] - e;
            for (let g = 0; g < k; g++) {
                let c = f[0] - e;
                for (let g = 0; g <
                    h; g++) a.push(this.calculate(c, d, b)), c += e;
                d += e
            }
            b += e
        }
        return a
    };
    q.build = function(a, b, n) {
        let g = [],
            m = [],
            l = [];
        var u = [Infinity, -Infinity, Infinity, -Infinity, Infinity, -Infinity];
        b += 2;
        for (let c = 0, d = a.length; c < d; c++) {
            var w = a[c];
            u[0] = k.min(u[0], w.x - b);
            u[1] = k.max(u[1], w.x + b);
            u[2] = k.min(u[2], w.y - b);
            u[3] = k.max(u[3], w.y + b);
            u[4] = k.min(u[4], w.z - b);
            u[5] = k.max(u[5], w.z + b)
        }
        a = u;
        b = a[1] - a[0];
        w = a[3] - a[2];
        var q = a[5] - a[4];
        u = k.min(b, k.min(w, q)) / n;
        n = 2 + k.ceil(b / u);
        var y = 2 + k.ceil(w / u),
            c = 2 + k.ceil(q / u);
        b = this.generate(b, w, q, u, a,
            n, y, c);
        b = t(b, [n, y, c]);
        n = [];
        w = [];
        for (let c = 0, e = b.vertices.length; c < e; c++) w.push(d(b.vertices[c], n, a[0], a[2], a[4], u));
        a = [];
        for (let c = 0, d = b.faces.length; c < d; c++) y = b.faces[c], u = w[y[0]], q = w[y[1]], y = w[y[2]], a.push(new h(u, q, y)), l.push(u, q, y);
        u = [];
        for (let c = 0, d = n.length; c < d; c++) {
            b = [];
            for (let d = 0, e = a.length; d < e; d++)
                if (w = a[d], w.i1 === c || w.i2 === c || w.i3 === c) w.i1 != c && -1 === b.indexOf(w.i1) && b.push(w.i1), w.i2 != c && -1 === b.indexOf(w.i2) && b.push(w.i2), w.i3 != c && -1 === b.indexOf(w.i3) && b.push(w.i3);
            u.push(b)
        }
        b = [];
        for (let a =
                0, d = n.length; a < d; a++) {
            q = n[a];
            y = u[a];
            w = new f.Atom;
            if (3 > y.length) w.x = q.x, w.y = q.y, w.z = q.z;
            else {
                c = 1;
                5 > y.length && (c = .5);
                for (let a = 0, b = y.length; a < b; a++) {
                    let b = n[y[a]];
                    w.x += b.x;
                    w.y += b.y;
                    w.z += b.z
                }
                w.x += q.x * c;
                w.y += q.y * c;
                w.z += q.z * c;
                q = 1 / (c + y.length);
                w.x *= q;
                w.y *= q;
                w.z *= q
            }
            b.push(w)
        }
        n = b;
        for (let a = 0, b = n.length; a < b; a++) u = n[a], g.push(u.x, u.y, u.z);
        for (let c = 0, d = a.length; c < d; c++) u = a[c], b = n[u.i1], q = n[u.i2], w = n[u.i3], q = [q.x - b.x, q.y - b.y, q.z - b.z], e.cross(q, [w.x - b.x, w.y - b.y, w.z - b.z]), isNaN(q[0]) && (q = [0, 0, 0]), u.normal = q;
        for (let b =
                0, c = n.length; b < c; b++) {
            n = [0, 0, 0];
            for (let c = 0, d = a.length; c < d; c++)
                if (u = a[c], u.i1 === b || u.i2 === b || u.i3 === b) n[0] += u.normal[0], n[1] += u.normal[1], n[2] += u.normal[2];
            e.normalize(n);
            m.push(n[0], n[1], n[2])
        }
        this.storeData(g, m, l)
    };
    q.render = function(a, b) {
        this.styles && (b = this.styles);
        b.surfaces_display && (a.shader.setMatrixUniforms(a), this.bindBuffers(a), a.material.setTempColors(a, b.surfaces_materialAmbientColor_3D, b.surfaces_color, b.surfaces_materialSpecularColor_3D, b.surfaces_materialShininess_3D), a.material.setAlpha(a,
            b.surfaces_alpha), "Dots" === b.surfaces_style ? (a.shader.setPointSize(a, b.shapes_pointSize), a.drawElements(a.POINTS, this.vertexIndexBuffer.numItems, a.UNSIGNED_SHORT, 0)) : "Mesh" === b.surfaces_style ? (a.lineWidth(b.shapes_lineWidth), a.drawElements(a.LINES, this.vertexIndexBuffer.numItems, a.UNSIGNED_SHORT, 0)) : a.drawElements(a.TRIANGLES, this.vertexIndexBuffer.numItems, a.UNSIGNED_SHORT, 0))
    }
})(ChemDoodle.structures, ChemDoodle.structures.d3, ChemDoodle.ELEMENT, ChemDoodle.lib.MarchingCubes, ChemDoodle.lib.vec3, Math);
(function(f, q, l, t, e) {
    q.SASSurface = function(e, b, d) {
        this.atoms = e;
        this.probeRadius = b;
        this.resolution = d;
        this.build(e, b, d)
    };
    (q.SASSurface.prototype = new q._Surface).calculate = function(e, b, d) {
        let h = Infinity;
        e = new f.Atom("C", e, b, d);
        for (let a = 0, g = this.atoms.length; a < g; a++) b = this.atoms[a], d = l[b.label] && 0 !== l[b.label].vdWRadius ? l[b.label].vdWRadius : 2, b = b.distance3D(e) - this.probeRadius - d, h = t.min(h, b);
        return h
    }
})(ChemDoodle.structures, ChemDoodle.structures.d3, ChemDoodle.ELEMENT, Math);
(function(f, q, l, t, e) {
    q.VDWSurface = function(e, b) {
        this.atoms = e;
        this.probeRadius = 0;
        this.resolution = b;
        this.build(e, 0, b)
    };
    (q.VDWSurface.prototype = new q._Surface).calculate = function(e, b, d) {
        let h = Infinity;
        e = new f.Atom("C", e, b, d);
        for (let a = 0, g = this.atoms.length; a < g; a++) b = this.atoms[a], d = l[b.label] && 0 !== l[b.label].vdWRadius ? l[b.label].vdWRadius : 2, b = b.distance3D(e) - d, h = t.min(h, b);
        return h
    }
})(ChemDoodle.structures, ChemDoodle.structures.d3, ChemDoodle.ELEMENT, Math);
(function(f, q, l, t) {
    f.Plate = function(e) {
        this.lanes = Array(e);
        i = 0;
        for (ii = e; i < ii; i++) this.lanes[i] = []
    };
    t = f.Plate.prototype;
    t.sort = function() {
        i = 0;
        for (ii = this.lanes.length; i < ii; i++) this.lanes[i].sort(function(e, f) {
            return e - f
        })
    };
    t.draw = function(e, f) {
        f = e.canvas.width;
        var b = e.canvas.height;
        this.origin = 9 * b / 10;
        this.front = b / 10;
        this.laneLength = this.origin - this.front;
        e.strokeStyle = "#000000";
        e.beginPath();
        e.moveTo(0, this.front);
        e.lineTo(f, this.front);
        e.setLineDash([3]);
        e.stroke();
        e.setLineDash([]);
        e.beginPath();
        e.moveTo(0, this.origin);
        e.lineTo(f, this.origin);
        e.closePath();
        e.stroke();
        i = 0;
        for (ii = this.lanes.length; i < ii; i++)
            for (b = (i + 1) * f / (ii + 1), e.beginPath(), e.moveTo(b, this.origin), e.lineTo(b, this.origin + 3), e.closePath(), e.stroke(), s = 0, ss = this.lanes[i].length; s < ss; s++) {
                let d = this.origin - this.laneLength * this.lanes[i][s].rf;
                switch (this.lanes[i][s].type) {
                    case "compact":
                        e.beginPath();
                        e.arc(b, d, 3, 0, 2 * l.PI, !1);
                        e.closePath();
                        break;
                    case "expanded":
                        e.beginPath();
                        e.arc(b, d, 7, 0, 2 * l.PI, !1);
                        e.closePath();
                        break;
                    case "widened":
                        q.contextEllipse(e,
                            b - 18, d - 10, 36, 10);
                        break;
                    case "cresent":
                        e.beginPath(), e.arc(b, d, 9, 0, l.PI, !0), e.closePath()
                }
                switch (this.lanes[i][s].style) {
                    case "solid":
                        e.fillStyle = "#000000";
                        e.fill();
                        break;
                    case "transparent":
                        e.stroke()
                }
            }
    };
    f.Plate.Spot = function(e, f, b) {
        this.type = e;
        this.rf = f;
        this.style = b ? b : "solid"
    }
})(ChemDoodle.structures, ChemDoodle.extensions, Math);
(function(f, q, l, t, e, k) {
    f.DEFAULT_STYLES = {
        backgroundColor: "#FFFFFF",
        scale: 1,
        rotateAngle: 0,
        bondLength_2D: 20,
        angstromsPerBondLength: 1.25,
        lightDirection_3D: [-.1, -.1, -1],
        lightDiffuseColor_3D: "#FFFFFF",
        lightSpecularColor_3D: "#FFFFFF",
        projectionPerspective_3D: !0,
        projectionPerspectiveVerticalFieldOfView_3D: 45,
        projectionOrthoWidth_3D: 40,
        projectionWidthHeightRatio_3D: k,
        projectionFrontCulling_3D: .1,
        projectionBackCulling_3D: 1E4,
        cullBackFace_3D: !0,
        fog_mode_3D: 0,
        fog_color_3D: "#000000",
        fog_start_3D: 0,
        fog_end_3D: 1,
        fog_density_3D: 1,
        shadow_3D: !1,
        shadow_intensity_3D: .85,
        flat_color_3D: !1,
        antialias_3D: !0,
        gammaCorrection_3D: 2.2,
        colorHover: "#885110",
        colorSelect: "#0060B2",
        colorError: "#c10000",
        colorPreview: "#00FF00",
        ssao_3D: !1,
        ssao_kernel_radius: 17,
        ssao_kernel_samples: 32,
        ssao_power: 1,
        outline_3D: !1,
        outline_thickness: 1,
        outline_normal_threshold: .85,
        outline_depth_threshold: .1,
        fxaa_edgeThreshold: .0625,
        fxaa_edgeThresholdMin: 1 / 12,
        fxaa_searchSteps: 64,
        fxaa_searchThreshold: .25,
        fxaa_subpixCap: 1,
        fxaa_subpixTrim: 0,
        atoms_display: !0,
        atoms_color: "#000000",
        atoms_font_size_2D: 12,
        atoms_font_families_2D: ["Helvetica", "Arial", "Dialog"],
        atoms_font_bold_2D: !1,
        atoms_font_italic_2D: !1,
        atoms_circles_2D: !1,
        atoms_circleDiameter_2D: 10,
        atoms_circleBorderWidth_2D: 1,
        atoms_lonePairDistance_2D: 8,
        atoms_lonePairSpread_2D: 4,
        atoms_lonePairDiameter_2D: 1,
        atoms_useJMOLColors: !1,
        atoms_usePYMOLColors: !1,
        atoms_HBlack_2D: !0,
        atoms_implicitHydrogens_2D: !0,
        atoms_displayTerminalCarbonLabels_2D: !1,
        atoms_showHiddenCarbons_2D: !0,
        atoms_showAttributedCarbons_2D: !0,
        atoms_displayAllCarbonLabels_2D: !1,
        atoms_resolution_3D: 30,
        atoms_sphereDiameter_3D: .8,
        atoms_useVDWDiameters_3D: !1,
        atoms_vdwMultiplier_3D: 1,
        atoms_materialAmbientColor_3D: "#000000",
        atoms_materialSpecularColor_3D: "#555555",
        atoms_materialShininess_3D: 32,
        atoms_nonBondedAsStars_3D: !1,
        atoms_displayLabels_3D: !1,
        bonds_display: !0,
        bonds_color: "#000000",
        bonds_width_2D: 1,
        bonds_useAbsoluteSaturationWidths_2D: !0,
        bonds_saturationWidth_2D: .2,
        bonds_saturationWidthAbs_2D: 5,
        bonds_ends_2D: "round",
        bonds_splitColor: !1,
        bonds_colorGradient: !1,
        bonds_saturationAngle_2D: l.PI / 3,
        bonds_symmetrical_2D: !1,
        bonds_clearOverlaps_2D: !1,
        bonds_overlapClearWidth_2D: .5,
        bonds_atomLabelBuffer_2D: 1,
        bonds_wedgeThickness_2D: 6,
        bonds_wavyLength_2D: 4,
        bonds_hashWidth_2D: 1,
        bonds_hashSpacing_2D: 2.5,
        bonds_dotSize_2D: 2,
        bonds_lewisStyle_2D: !1,
        bonds_showBondOrders_3D: !1,
        bonds_resolution_3D: 30,
        bonds_renderAsLines_3D: !1,
        bonds_cylinderDiameter_3D: .3,
        bonds_pillLatitudeResolution_3D: 10,
        bonds_pillLongitudeResolution_3D: 20,
        bonds_pillHeight_3D: .3,
        bonds_pillSpacing_3D: .1,
        bonds_pillDiameter_3D: .3,
        bonds_materialAmbientColor_3D: "#000000",
        bonds_materialSpecularColor_3D: "#555555",
        bonds_materialShininess_3D: 32,
        proteins_displayRibbon: !0,
        proteins_displayBackbone: !1,
        proteins_backboneThickness: 1.5,
        proteins_backboneColor: "#CCCCCC",
        proteins_ribbonCartoonize: !1,
        proteins_displayPipePlank: !1,
        proteins_residueColor: "none",
        proteins_primaryColor: "#FF0D0D",
        proteins_secondaryColor: "#FFFF30",
        proteins_ribbonCartoonHelixPrimaryColor: "#00E740",
        proteins_ribbonCartoonHelixSecondaryColor: "#9905FF",
        proteins_ribbonCartoonSheetColor: "#E8BB99",
        proteins_tubeColor: "#FF0D0D",
        proteins_tubeResolution_3D: 15,
        proteins_ribbonThickness: .2,
        proteins_tubeThickness: .5,
        proteins_plankSheetWidth: 3.5,
        proteins_cylinderHelixDiameter: 4,
        proteins_verticalResolution: 8,
        proteins_horizontalResolution: 8,
        proteins_materialAmbientColor_3D: "#000000",
        proteins_materialSpecularColor_3D: "#555555",
        proteins_materialShininess_3D: 32,
        nucleics_display: !0,
        nucleics_tubeColor: "#CCCCCC",
        nucleics_baseColor: "#C10000",
        nucleics_residueColor: "none",
        nucleics_tubeThickness: 1.5,
        nucleics_tubeResolution_3D: 15,
        nucleics_verticalResolution: 8,
        nucleics_materialAmbientColor_3D: "#000000",
        nucleics_materialSpecularColor_3D: "#555555",
        nucleics_materialShininess_3D: 32,
        macro_displayAtoms: !1,
        macro_displayBonds: !1,
        macro_atomToLigandDistance: -1,
        macro_showWater: !1,
        macro_colorByChain: !1,
        macro_rainbowColors: ["#0000FF", "#00FFFF", "#00FF00", "#FFFF00", "#FF0000"],
        surfaces_display: !0,
        surfaces_alpha: .5,
        surfaces_style: "Solid",
        surfaces_color: "white",
        surfaces_materialAmbientColor_3D: "#000000",
        surfaces_materialSpecularColor_3D: "#000000",
        surfaces_materialShininess_3D: 32,
        plots_color: "#000000",
        plots_width: 1,
        plots_showIntegration: !1,
        plots_integrationColor: "#c10000",
        plots_integrationLineWidth: 1,
        plots_showGrid: !1,
        plots_gridColor: "gray",
        plots_gridLineWidth: .5,
        plots_showYAxis: !0,
        plots_flipXAxis: !1,
        text_font_size: 12,
        text_font_families: ["Helvetica", "Arial", "Dialog"],
        text_font_bold: !0,
        text_font_italic: !1,
        text_font_stroke_3D: !0,
        text_color: "#000000",
        shapes_color: "#000000",
        shapes_lineWidth: 1,
        shapes_pointSize: 2,
        shapes_arrowLength_2D: 8,
        compass_display: !1,
        compass_axisXColor_3D: "#FF0000",
        compass_axisYColor_3D: "#00FF00",
        compass_axisZColor_3D: "#0000FF",
        compass_size_3D: 50,
        compass_resolution_3D: 10,
        compass_displayText_3D: !0,
        compass_type_3D: 0,
        measurement_update_3D: !1,
        measurement_angleBands_3D: 10,
        measurement_displayText_3D: !0
    };
    q.Styles = function(b) {
        e.assign(this, t.parse(t.stringify(b === k ? f.DEFAULT_STYLES : b)))
    };
    l = q.Styles.prototype;
    l.set3DRepresentation = function(b) {
        this.bonds_display = this.atoms_display = !0;
        this.bonds_color = "#777777";
        this.bonds_showBondOrders_3D =
            this.bonds_splitColor = this.atoms_useJMOLColors = this.atoms_useVDWDiameters_3D = !0;
        this.bonds_renderAsLines_3D = !1;
        "Ball and Stick" === b ? (this.atoms_vdwMultiplier_3D = .3, this.bonds_splitColor = !1, this.bonds_cylinderDiameter_3D = .3, this.bonds_materialAmbientColor_3D = ChemDoodle.DEFAULT_STYLES.atoms_materialAmbientColor_3D, this.bonds_pillDiameter_3D = .15) : "van der Waals Spheres" === b ? (this.bonds_display = !1, this.atoms_vdwMultiplier_3D = 1) : "Stick" === b ? (this.bonds_showBondOrders_3D = this.atoms_useVDWDiameters_3D = !1,
            this.bonds_cylinderDiameter_3D = this.atoms_sphereDiameter_3D = .8, this.bonds_materialAmbientColor_3D = this.atoms_materialAmbientColor_3D) : "Wireframe" === b ? (this.atoms_useVDWDiameters_3D = !1, this.bonds_cylinderDiameter_3D = this.bonds_pillDiameter_3D = .05, this.atoms_sphereDiameter_3D = .15, this.bonds_materialAmbientColor_3D = ChemDoodle.DEFAULT_STYLES.atoms_materialAmbientColor_3D) : "Line" === b ? (this.atoms_display = !1, this.bonds_renderAsLines_3D = !0, this.bonds_width_2D = 1, this.bonds_cylinderDiameter_3D = .05) : alert('"' +
            b + '" is not recognized. Use one of the following strings:\n\n1. Ball and Stick\n2. van der Waals Spheres\n3. Stick\n4. Wireframe\n5. Line\n')
    };
    l.copy = function() {
        return new q.Styles(this)
    }
})(ChemDoodle, ChemDoodle.structures, Math, JSON, Object);
(function(f, q, l, t, e) {
    l.getPointsPerAngstrom = function() {
        return f.DEFAULT_STYLES.bondLength_2D / f.DEFAULT_STYLES.angstromsPerBondLength
    };
    l.BondDeducer = function() {};
    e = l.BondDeducer.prototype;
    e.margin = 1.1;
    e.deduceCovalentBonds = function(e, b) {
        let d = l.getPointsPerAngstrom();
        b && (d = b);
        for (let f = 0, a = e.atoms.length; f < a; f++)
            for (b = f + 1; b < a; b++) {
                let a = e.atoms[f],
                    h = e.atoms[b];
                a.distance3D(h) < (q[a.label].covalentRadius + q[h.label].covalentRadius) * d * this.margin && e.bonds.push(new t.Bond(a, h, 1))
            }
    }
})(ChemDoodle, ChemDoodle.ELEMENT,
    ChemDoodle.informatics, ChemDoodle.structures);
(function(f, q, l) {
    f.HydrogenDeducer = function() {};
    f.HydrogenDeducer.prototype.removeHydrogens = function(f, e) {
        let k = [],
            b = [];
        for (let d = 0, h = f.bonds.length; d < h; d++) {
            let a = f.bonds[d],
                g = "H" !== a.a1.label && "H" !== a.a2.label;
            g || e || a.stereo === q.Bond.STEREO_NONE || (g = !0);
            g ? (a.a1.tag = !0, b.push(a)) : ("H" === a.a1.label && (a.a1.remove = !0), "H" === a.a2.label && (a.a2.remove = !0))
        }
        for (let b = 0, h = f.atoms.length; b < h; b++) e = f.atoms[b], e.remove ? e.remove = l : k.push(e);
        f.atoms = k;
        f.bonds = b
    }
})(ChemDoodle.informatics, ChemDoodle.structures);
(function(f, q, l) {
    f.Splitter = function() {};
    f.Splitter.prototype.split = function(f) {
        let e = [];
        for (let b = 0, e = f.atoms.length; b < e; b++) f.atoms[b].visited = !1;
        for (let b = 0, e = f.bonds.length; b < e; b++) f.bonds[b].visited = !1;
        for (let d = 0, h = f.atoms.length; d < h; d++) {
            var k = f.atoms[d];
            if (!k.visited) {
                let a = new q.Molecule;
                a.atoms.push(k);
                k.visited = !0;
                let d = new q.Queue;
                for (d.enqueue(k); !d.isEmpty();) {
                    k = d.dequeue();
                    for (let e = 0, g = f.bonds.length; e < g; e++) {
                        var b = f.bonds[e];
                        b.contains(k) && !b.visited && (b.visited = !0, a.bonds.push(b),
                            b = b.getNeighbor(k), b.visited || (b.visited = !0, a.atoms.push(b), d.enqueue(b)))
                    }
                }
                e.push(a)
            }
        }
        return e
    }
})(ChemDoodle.informatics, ChemDoodle.structures);
(function(f, q, l, t) {
    f.StructureBuilder = function() {};
    f.StructureBuilder.prototype.copy = function(e) {
        let f = new q.JSONInterpreter;
        return f.molFrom(f.molTo(e))
    }
})(ChemDoodle.informatics, ChemDoodle.io, ChemDoodle.structures);
(function(f, q) {
    f._Counter = function() {};
    f = f._Counter.prototype;
    f.value = 0;
    f.molecule = q;
    f.setMolecule = function(f) {
        this.value = 0;
        this.molecule = f;
        this.innerCalculate && this.innerCalculate()
    }
})(ChemDoodle.informatics);
(function(f, q) {
    f.FrerejacqueNumberCounter = function(f) {
        this.setMolecule(f)
    };
    (f.FrerejacqueNumberCounter.prototype = new f._Counter).innerCalculate = function() {
        this.value = this.molecule.bonds.length - this.molecule.atoms.length + (new f.NumberOfMoleculesCounter(this.molecule)).value
    }
})(ChemDoodle.informatics);
(function(f, q, l) {
    q.NumberOfMoleculesCounter = function(f) {
        this.setMolecule(f)
    };
    (q.NumberOfMoleculesCounter.prototype = new q._Counter).innerCalculate = function() {
        for (let e = 0, f = this.molecule.atoms.length; e < f; e++) this.molecule.atoms[e].visited = !1;
        for (let e = 0, k = this.molecule.atoms.length; e < k; e++)
            if (!this.molecule.atoms[e].visited) {
                this.value++;
                let b = new f.Queue;
                this.molecule.atoms[e].visited = !0;
                for (b.enqueue(this.molecule.atoms[e]); !b.isEmpty();) {
                    let d = b.dequeue();
                    for (let e = 0, a = this.molecule.bonds.length; e <
                        a; e++) {
                        var l = this.molecule.bonds[e];
                        l.contains(d) && (l = l.getNeighbor(d), l.visited || (l.visited = !0, b.enqueue(l)))
                    }
                }
            }
    }
})(ChemDoodle.structures, ChemDoodle.informatics);
(function(f, q) {
    f._RingFinder = function() {};
    f = f._RingFinder.prototype;
    f.atoms = q;
    f.bonds = q;
    f.rings = q;
    f.reduce = function(f) {
        for (let e = 0, k = f.atoms.length; e < k; e++) f.atoms[e].visited = !1;
        for (let e = 0, k = f.bonds.length; e < k; e++) f.bonds[e].visited = !1;
        let l = !0;
        for (; l;) {
            l = !1;
            for (let e = 0, k = f.atoms.length; e < k; e++) {
                let b = 0,
                    d;
                for (let h = 0, a = f.bonds.length; h < a; h++)
                    if (f.bonds[h].contains(f.atoms[e]) && !f.bonds[h].visited) {
                        b++;
                        if (2 === b) break;
                        d = f.bonds[h]
                    } 1 === b && (l = !0, d.visited = !0, f.atoms[e].visited = !0)
            }
        }
        for (let e = 0, k = f.atoms.length; e <
            k; e++) f.atoms[e].visited || this.atoms.push(f.atoms[e]);
        for (let e = 0, k = f.bonds.length; e < k; e++) f.bonds[e].visited || this.bonds.push(f.bonds[e]);
        0 === this.bonds.length && 0 !== this.atoms.length && (this.atoms = [])
    };
    f.setMolecule = function(f) {
        this.atoms = [];
        this.bonds = [];
        this.rings = [];
        this.reduce(f);
        2 < this.atoms.length && this.innerGetRings && this.innerGetRings()
    };
    f.fuse = function() {
        for (let f = 0, q = this.rings.length; f < q; f++)
            for (let e = 0, k = this.bonds.length; e < k; e++) - 1 !== this.rings[f].atoms.indexOf(this.bonds[e].a1) && -1 !==
                this.rings[f].atoms.indexOf(this.bonds[e].a2) && this.rings[f].bonds.push(this.bonds[e])
    }
})(ChemDoodle.informatics);
(function(f, q, l) {
    function t(e, b) {
        this.atoms = [];
        if (b)
            for (let d = 0, e = b.atoms.length; d < e; d++) this.atoms[d] = b.atoms[d];
        this.atoms.push(e)
    }
    let e = t.prototype;
    e.grow = function(e, b) {
        let d = this.atoms[this.atoms.length - 1],
            f = [];
        for (let a = 0, g = e.length; a < g; a++)
            if (e[a].contains(d)) {
                let g = e[a].getNeighbor(d); - 1 === b.indexOf(g) && f.push(g)
            } e = [];
        for (let a = 0, b = f.length; a < b; a++) e.push(new t(f[a], this));
        return e
    };
    e.check = function(e, b, d) {
        for (let a = 0, d = b.atoms.length - 1; a < d; a++)
            if (-1 !== this.atoms.indexOf(b.atoms[a])) return l;
        let f;
        if (b.atoms[b.atoms.length - 1] === this.atoms[this.atoms.length - 1]) {
            f = new q.Ring;
            f.atoms[0] = d;
            for (let a = 0, b = this.atoms.length; a < b; a++) f.atoms.push(this.atoms[a]);
            for (e = b.atoms.length - 2; 0 <= e; e--) f.atoms.push(b.atoms[e])
        } else {
            let a = [];
            for (let d = 0, f = e.length; d < f; d++) e[d].contains(b.atoms[b.atoms.length - 1]) && a.push(e[d]);
            for (let g = 0, h = a.length; g < h; g++)
                if ((1 === b.atoms.length || !a[g].contains(b.atoms[b.atoms.length - 2])) && a[g].contains(this.atoms[this.atoms.length - 1])) {
                    f = new q.Ring;
                    f.atoms[0] = d;
                    for (let a =
                            0, b = this.atoms.length; a < b; a++) f.atoms.push(this.atoms[a]);
                    for (e = b.atoms.length - 1; 0 <= e; e--) f.atoms.push(b.atoms[e]);
                    break
                }
        }
        return f
    };
    f.EulerFacetRingFinder = function(e) {
        this.setMolecule(e)
    };
    f = f.EulerFacetRingFinder.prototype = new f._RingFinder;
    f.fingerBreak = 5;
    f.innerGetRings = function() {
        for (let g = 0, h = this.atoms.length; g < h; g++) {
            let h = [];
            for (let a = 0, b = this.bonds.length; a < b; a++) this.bonds[a].contains(this.atoms[g]) && h.push(this.bonds[a].getNeighbor(this.atoms[g]));
            for (let m = 0, n = h.length; m < n; m++)
                for (let n =
                        m + 1; n < h.length; n++) {
                    var e = [];
                    e[0] = new t(h[m]);
                    e[1] = new t(h[n]);
                    var b = [];
                    b[0] = this.atoms[g];
                    for (let a = 0, d = h.length; a < d; a++) a !== m && a !== n && b.push(h[a]);
                    var d = [],
                        f = e[0].check(this.bonds, e[1], this.atoms[g]);
                    for (f && (d[0] = f); 0 === d.length && 0 < e.length && e[0].atoms.length < this.fingerBreak;) {
                        f = [];
                        for (let d = 0, g = e.length; d < g; d++) {
                            var a = e[d].grow(this.bonds, b);
                            for (let b = 0, c = a.length; b < c; b++) f.push(a[b])
                        }
                        e = f;
                        for (let b = 0, h = e.length; b < h; b++)
                            for (f = b + 1; f < h; f++)(a = e[b].check(this.bonds, e[f], this.atoms[g])) && d.push(a);
                        if (0 === d.length) {
                            f = [];
                            for (let d = 0, e = b.length; d < e; d++)
                                for (let e = 0, c = this.bonds.length; e < c; e++) this.bonds[e].contains(b[d]) && (a = this.bonds[e].getNeighbor(b[d]), -1 === b.indexOf(a) && -1 === f.indexOf(a) && f.push(a));
                            for (let a = 0, d = f.length; a < d; a++) b.push(f[a])
                        }
                    }
                    if (0 < d.length) {
                        e = l;
                        for (let a = 0, b = d.length; a < b; a++)
                            if (!e || e.atoms.length > d[a].atoms.length) e = d[a];
                        d = !1;
                        for (let a = 0, g = this.rings.length; a < g; a++) {
                            b = !0;
                            for (let d = 0, c = e.atoms.length; d < c; d++)
                                if (-1 === this.rings[a].atoms.indexOf(e.atoms[d])) {
                                    b = !1;
                                    break
                                } if (b) {
                                d = !0;
                                break
                            }
                        }
                        d || this.rings.push(e)
                    }
                }
        }
        this.fuse()
    }
})(ChemDoodle.informatics, ChemDoodle.structures);
(function(f, q) {
    f.SSSRFinder = function(l) {
        this.rings = [];
        if (0 < l.atoms.length) {
            let q = (new f.FrerejacqueNumberCounter(l)).value,
                e = (new f.EulerFacetRingFinder(l)).rings;
            e.sort(function(e, b) {
                return e.atoms.length - b.atoms.length
            });
            for (let e = 0, b = l.bonds.length; e < b; e++) l.bonds[e].visited = !1;
            for (let f = 0, b = e.length; f < b; f++) {
                l = !1;
                for (let b = 0, h = e[f].bonds.length; b < h; b++)
                    if (!e[f].bonds[b].visited) {
                        l = !0;
                        break
                    } if (l) {
                    for (let b = 0, h = e[f].bonds.length; b < h; b++) e[f].bonds[b].visited = !0;
                    this.rings.push(e[f])
                }
                if (this.rings.length ===
                    q) break
            }
        }
    }
})(ChemDoodle.informatics);
(function(f, q) {
    f._Interpreter = function() {};
    f._Interpreter.prototype.fit = function(f, q, e) {
        let k = f.length,
            b = [];
        for (let d = 0; d < q - k; d++) b.push(" ");
        return e ? f + b.join("") : b.join("") + f
    }
})(ChemDoodle.io);
(function(f, q, l, t, e, k, b, d) {
    let h = /\s+/g,
        a = /\(|\)|\s+/g,
        g = /'|\s+/g,
        n = /,|'|\s+/g,
        v = /^\s+/,
        m = /[0-9]/g,
        x = /[0-9]|\+|\-/g,
        u = function(a) {
            return 0 !== a.length
        },
        w = {
            P: [],
            A: [
                [0, .5, .5]
            ],
            B: [
                [.5, 0, .5]
            ],
            C: [
                [.5, .5, 0]
            ],
            I: [
                [.5, .5, .5]
            ],
            R: [
                [2 / 3, 1 / 3, 1 / 3],
                [1 / 3, 2 / 3, 2 / 3]
            ],
            S: [
                [1 / 3, 1 / 3, 2 / 3],
                [2 / 3, 2 / 3, 1 / 3]
            ],
            T: [
                [1 / 3, 2 / 3, 1 / 3],
                [2 / 3, 1 / 3, 2 / 3]
            ],
            F: [
                [0, .5, .5],
                [.5, 0, .5],
                [.5, .5, 0]
            ]
        },
        z = function(a) {
            let b = 0,
                c = 0,
                d = 0,
                e = 0;
            var g = a.indexOf("x"),
                f = a.indexOf("y");
            let h = a.indexOf("z"); - 1 !== g && (c++, 0 < g && "+" !== a.charAt(g - 1) && (c *= -1)); - 1 !== f && (d++,
                0 < f && "+" !== a.charAt(f - 1) && (d *= -1)); - 1 !== h && (e++, 0 < h && "+" !== a.charAt(h - 1) && (e *= -1));
            if (2 < a.length) {
                g = "+";
                for (let c = 0, d = a.length; c < d; c++) f = a.charAt(c), "-" !== f && "/" !== f || c !== a.length - 1 && !a.charAt(c + 1).match(m) || (g = f), f.match(m) && ("+" === g ? b += parseInt(f) : "-" === g ? b -= parseInt(f) : "/" === g && (b /= parseInt(f)))
            }
            return [b, c, d, e]
        };
    q.CIFInterpreter = function() {};
    q.CIFInterpreter.generateABC2XYZ = function(a, b, d, g, f, h) {
        g = (e.cos(g) - e.cos(h) * e.cos(f)) / e.sin(h);
        return [a, 0, 0, 0, b * e.cos(h), b * e.sin(h), 0, 0, d * e.cos(f), d * g, d * e.sqrt(1 -
            e.pow(e.cos(f), 2) - g * g), 0, 0, 0, 0, 1]
    };
    (q.CIFInterpreter.prototype = new q._Interpreter).read = function(b, m, y, B) {
        m = m ? m : 1;
        y = y ? y : 1;
        B = B ? B : 1;
        let c = new l.Molecule;
        if (!b) return c;
        var p = b.split("\n");
        let A = b = 0,
            L = 0,
            H = 0,
            K = 0,
            N = 0;
        var P = "P",
            Z, E;
        let fa;
        for (var J, O = !0; 0 < p.length;)
            if (O ? J = p.shift() : O = !0, 0 < J.length)
                if (J.startsWith("_cell_length_a")) b = parseFloat(J.split(a)[1]);
                else if (J.startsWith("_cell_length_b")) A = parseFloat(J.split(a)[1]);
        else if (J.startsWith("_cell_length_c")) L = parseFloat(J.split(a)[1]);
        else if (J.startsWith("_cell_angle_alpha")) H =
            e.PI * parseFloat(J.split(a)[1]) / 180;
        else if (J.startsWith("_cell_angle_beta")) K = e.PI * parseFloat(J.split(a)[1]) / 180;
        else if (J.startsWith("_cell_angle_gamma")) N = e.PI * parseFloat(J.split(a)[1]) / 180;
        else if (J.startsWith("_symmetry_space_group_name_H-M")) P = J.split(g)[1];
        else if (J.startsWith("loop_")) {
            for (var Q = {
                    fields: [],
                    lines: []
                }, V = !1;
                (J = p.shift()) !== d && !(J = J.replace(v, "")).startsWith("loop_") && 0 < J.length;)
                if (J.startsWith("_")) {
                    if (V) break;
                    Q.fields = Q.fields.concat(J.split(h).filter(u))
                } else V = !0, Q.lines.push(J);
            0 !== p.length && (J.startsWith("loop_") || J.startsWith("_")) && (O = !1); - 1 !== Q.fields.indexOf("_symmetry_equiv_pos_as_xyz") || -1 !== Q.fields.indexOf("_space_group_symop_operation_xyz") ? Z = Q : -1 !== Q.fields.indexOf("_atom_site_label") ? E = Q : -1 !== Q.fields.indexOf("_geom_bond_atom_site_label_1") && (fa = Q)
        }
        p = q.CIFInterpreter.generateABC2XYZ(b, A, L, H, K, N);
        if (E) {
            var X = V = Q = O = -1,
                ha = -1;
            for (let a = 0, b = E.fields.length; a < b; a++) J = E.fields[a], "_atom_site_type_symbol" === J ? O = a : "_atom_site_label" === J ? Q = a : "_atom_site_fract_x" === J ? V =
                a : "_atom_site_fract_y" === J ? X = a : "_atom_site_fract_z" === J && (ha = a);
            for (let a = 0, b = E.lines.length; a < b; a++) {
                J = E.lines[a];
                J = J.split(h).filter(u);
                var R = new l.Atom(J[-1 === O ? Q : O].split(x)[0], parseFloat(J[V]), parseFloat(J[X]), parseFloat(J[ha]));
                c.atoms.push(R); - 1 !== Q && (R.cifId = J[Q], R.cifPart = 0)
            }
        }
        if (Z && !fa) {
            E = 0;
            for (let a = 0, b = Z.fields.length; a < b; a++)
                if (J = Z.fields[a], "_symmetry_equiv_pos_as_xyz" === J || "_space_group_symop_operation_xyz" === J) E = a;
            J = w[P];
            P = [];
            for (let a = 0, b = Z.lines.length; a < b; a++) {
                V = Z.lines[a].split(n).filter(u);
                O = z(V[E]);
                Q = z(V[E + 1]);
                V = z(V[E + 2]);
                for (let b = 0, e = c.atoms.length; b < e; b++) {
                    X = c.atoms[b];
                    ha = X.x * O[1] + X.y * O[2] + X.z * O[3] + O[0];
                    R = X.x * Q[1] + X.y * Q[2] + X.z * Q[3] + Q[0];
                    let e = X.x * V[1] + X.y * V[2] + X.z * V[3] + V[0];
                    var U = new l.Atom(X.label, ha, R, e);
                    P.push(U);
                    X.cifId !== d && (U.cifId = X.cifId, U.cifPart = a + 1);
                    if (J)
                        for (let b = 0, c = J.length; b < c; b++) U = J[b], U = new l.Atom(X.label, ha + U[0], R + U[1], e + U[2]), P.push(U), X.cifId !== d && (U.cifId = X.cifId, U.cifPart = a + 1)
                }
            }
            for (let a = 0, b = P.length; a < b; a++) {
                for (E = P[a]; 1 <= E.x;) E.x--;
                for (; 0 > E.x;) E.x++;
                for (; 1 <=
                    E.y;) E.y--;
                for (; 0 > E.y;) E.y++;
                for (; 1 <= E.z;) E.z--;
                for (; 0 > E.z;) E.z++
            }
            E = [];
            for (let a = 0, b = P.length; a < b; a++) {
                J = !1;
                O = P[a];
                for (let a = 0, b = c.atoms.length; a < b; a++)
                    if (1E-4 > c.atoms[a].distance3D(O)) {
                        J = !0;
                        break
                    } if (!J) {
                    for (let a = 0, b = E.length; a < b; a++)
                        if (1E-4 > E[a].distance3D(O)) {
                            J = !0;
                            break
                        } J || E.push(O)
                }
            }
            c.atoms = c.atoms.concat(E)
        }
        P = [];
        for (E = 0; E < m; E++)
            for (J = 0; J < y; J++)
                for (O = 0; O < B; O++)
                    if (0 !== E || 0 !== J || 0 !== O)
                        for (let a = 0, b = c.atoms.length; a < b; a++) Q = c.atoms[a], V = new l.Atom(Q.label, Q.x + E, Q.y + J, Q.z + O), P.push(V), Q.cifId !== d &&
                            (V.cifId = Q.cifId, V.cifPart = Q.cifPart + (Z ? Z.lines.length : 0) + E + 10 * J + 100 * O);
        c.atoms = c.atoms.concat(P);
        for (let a = 0, b = c.atoms.length; a < b; a++) m = c.atoms[a], y = k.multiplyVec3(p, [m.x, m.y, m.z]), m.x = y[0], m.y = y[1], m.z = y[2];
        if (fa) {
            y = m = -1;
            for (let a = 0, b = fa.fields.length; a < b; a++) B = fa.fields[a], "_geom_bond_atom_site_label_1" === B ? m = a : "_geom_bond_atom_site_label_2" === B && (y = a);
            for (let a = 0, b = fa.lines.length; a < b; a++) {
                Z = fa.lines[a].split(h).filter(u);
                B = Z[m];
                Z = Z[y];
                for (let a = 0, b = c.atoms.length; a < b; a++)
                    for (p = a + 1; p < b; p++) {
                        P =
                            c.atoms[a];
                        E = c.atoms[p];
                        if (P.cifPart !== E.cifPart) break;
                        (P.cifId === B && E.cifId === Z || P.cifId === Z && E.cifId === B) && c.bonds.push(new l.Bond(P, E))
                    }
            }
        } else(new f.informatics.BondDeducer).deduceCovalentBonds(c, 1);
        return {
            molecule: c,
            unitCell: new t.UnitCell([b, A, L], [H, K, N], [0, 0, 0])
        }
    };
    let y = new q.CIFInterpreter;
    f.readCIF = function(a, b, d, e) {
        return y.read(a, b, d, e)
    }
})(ChemDoodle, ChemDoodle.io, ChemDoodle.structures, ChemDoodle.structures.d3, Math, ChemDoodle.lib.mat4, ChemDoodle.lib.vec3);
(function(f, q, l, t, e) {
    q.CMLInterpreter = function() {};
    let k = q.CMLInterpreter.prototype = new q._Interpreter;
    k.read = function(b) {
        let d = [];
        b = t.parseXML(b);
        b = t(b).find("cml");
        for (let h = 0, n = b.length; h < n; h++) {
            let n = t(b[h]).find("molecule");
            for (let b = 0, h = n.length; b < h; b++) {
                let c = d[b] = new l.Molecule,
                    h = [];
                var a = t(n[b]).find("atom");
                for (let c = 0, n = a.length; c < n; c++) {
                    var g = t(a[c]),
                        f = g.attr("elementType");
                    let n;
                    if (g.attr("x2") == e) {
                        var k = g.attr("x3");
                        var m = g.attr("y3");
                        n = g.attr("z3")
                    } else k = g.attr("x2"), m = g.attr("y2"),
                        n = 0;
                    f = d[b].atoms[c] = new l.Atom(f, k, m, n);
                    h[c] = g.attr("id");
                    g.attr("formalCharge") != e && (f.charge = g.attr("formalCharge"))
                }
                a = t(n[b]).find("bond");
                for (let e = 0, n = a.length; e < n; e++) {
                    g = t(a[e]);
                    k = g.attr("atomRefs2").split(" ");
                    f = c.atoms[t.inArray(k[0], h)];
                    k = c.atoms[t.inArray(k[1], h)];
                    switch (g.attr("order")) {
                        case "2":
                        case "D":
                            m = 2;
                            break;
                        case "3":
                        case "T":
                            m = 3;
                            break;
                        case "A":
                            m = 1.5;
                            break;
                        default:
                            m = 1
                    }
                    f = d[b].bonds[e] = new l.Bond(f, k, m);
                    switch (g.find("bondStereo").text()) {
                        case "W":
                            f.stereo = l.Bond.STEREO_PROTRUDING;
                            break;
                        case "H":
                            f.stereo = l.Bond.STEREO_RECESSED
                    }
                }
            }
        }
        return d
    };
    k.write = function(b) {
        let d = [];
        d.push('\x3c?xml version\x3d"1.0" encoding\x3d"UTF-8"?\x3e\n');
        d.push('\x3ccml convention\x3d"conventions:molecular" xmlns\x3d"http://www.xml-cml.org/schema" xmlns:conventions\x3d"http://www.xml-cml.org/convention/" xmlns:dc\x3d"http://purl.org/dc/elements/1.1/"\x3e\n');
        for (let e = 0, f = b.length; e < f; e++) {
            d.push('\x3cmolecule id\x3d"m');
            d.push(e);
            d.push('"\x3e');
            d.push("\x3catomArray\x3e");
            for (let g = 0, f = b[e].atoms.length; g <
                f; g++) {
                var a = b[e].atoms[g];
                d.push('\x3catom elementType\x3d"');
                d.push(a.label);
                d.push('" id\x3d"a');
                d.push(g);
                d.push('" ');
                d.push('x3\x3d"');
                d.push(a.x);
                d.push('" y3\x3d"');
                d.push(a.y);
                d.push('" z3\x3d"');
                d.push(a.z);
                d.push('" ');
                0 != a.charge && (d.push('formalCharge\x3d"'), d.push(a.charge), d.push('" '));
                d.push("/\x3e")
            }
            d.push("\x3c/atomArray\x3e");
            d.push("\x3cbondArray\x3e");
            for (let g = 0, f = b[e].bonds.length; g < f; g++) {
                a = b[e].bonds[g];
                d.push('\x3cbond atomRefs2\x3d"a');
                d.push(b[e].atoms.indexOf(a.a1));
                d.push(" a");
                d.push(b[e].atoms.indexOf(a.a2));
                d.push('" order\x3d"');
                switch (a.bondOrder) {
                    case 1.5:
                        d.push("A");
                        break;
                    case 1:
                    case 2:
                    case 3:
                        d.push(a.bondOrder);
                        break;
                    default:
                        d.push("S")
                }
                d.push('"/\x3e')
            }
            d.push("\x3c/bondArray\x3e");
            d.push("\x3c/molecule\x3e")
        }
        d.push("\x3c/cml\x3e");
        return d.join("")
    };
    let b = new q.CMLInterpreter;
    f.readCML = function(d) {
        return b.read(d)
    };
    f.writeCML = function(d) {
        return b.write(d)
    }
})(ChemDoodle, ChemDoodle.io, ChemDoodle.structures, ChemDoodle.lib.jQuery);
(function(f, q, l, t, e) {
    l.MOLInterpreter = function() {};
    e = l.MOLInterpreter.prototype = new l._Interpreter;
    e.read = function(b, d) {
        d || (d = f.DEFAULT_STYLES.bondLength_2D);
        let e = new t.Molecule;
        if (!b) return e;
        b = b.split("\n");
        var a = b[3];
        let g = parseInt(a.substring(0, 3));
        a = parseInt(a.substring(3, 6));
        for (var n = 0; n < g; n++) {
            var k = b[4 + n];
            e.atoms[n] = new t.Atom(k.substring(31, 34), parseFloat(k.substring(0, 10)) * d, (1 === d ? 1 : -1) * parseFloat(k.substring(10, 20)) * d, parseFloat(k.substring(20, 30)) * d);
            var m = parseInt(k.substring(34, 36));
            0 !== m && q[e.atoms[n].label] && (e.atoms[n].mass = q[e.atoms[n].label].mass + m);
            switch (parseInt(k.substring(36, 39))) {
                case 1:
                    e.atoms[n].charge = 3;
                    break;
                case 2:
                    e.atoms[n].charge = 2;
                    break;
                case 3:
                    e.atoms[n].charge = 1;
                    break;
                case 5:
                    e.atoms[n].charge = -1;
                    break;
                case 6:
                    e.atoms[n].charge = -2;
                    break;
                case 7:
                    e.atoms[n].charge = -3
            }
        }
        for (d = 0; d < a; d++) {
            k = b[4 + g + d];
            m = parseInt(k.substring(6, 9));
            n = parseInt(k.substring(9, 12));
            if (3 < m) switch (m) {
                case 4:
                    m = 1.5;
                    break;
                default:
                    m = 1
            }
            k = new t.Bond(e.atoms[parseInt(k.substring(0, 3)) - 1], e.atoms[parseInt(k.substring(3,
                6)) - 1], m);
            switch (n) {
                case 3:
                    k.stereo = t.Bond.STEREO_AMBIGUOUS;
                    break;
                case 1:
                    k.stereo = t.Bond.STEREO_PROTRUDING;
                    break;
                case 6:
                    k.stereo = t.Bond.STEREO_RECESSED
            }
            e.bonds[d] = k
        }
        return e
    };
    e.write = function(b) {
        let d = [];
        d.push("Molecule from ChemDoodle Web Components\n\nhttp://www.ichemlabs.com\n");
        d.push(this.fit(b.atoms.length.toString(), 3));
        d.push(this.fit(b.bonds.length.toString(), 3));
        d.push("  0  0  0  0            999 V2000\n");
        var e = b.getCenter();
        for (let h = 0, k = b.atoms.length; h < k; h++) {
            var a = b.atoms[h];
            let m =
                " 0";
            if (-1 !== a.mass && q[a.label]) {
                var g = a.mass - q[a.label].mass;
                5 > g && -4 < g && (m = (-1 < g ? " " : "") + g)
            }
            g = "  0";
            if (0 !== a.charge) switch (a.charge) {
                case 3:
                    g = "  1";
                    break;
                case 2:
                    g = "  2";
                    break;
                case 1:
                    g = "  3";
                    break;
                case -1:
                    g = "  5";
                    break;
                case -2:
                    g = "  6";
                    break;
                case -3:
                    g = "  7"
            }
            d.push(this.fit(((a.x - e.x) / f.DEFAULT_STYLES.bondLength_2D).toFixed(4), 10));
            d.push(this.fit((-(a.y - e.y) / f.DEFAULT_STYLES.bondLength_2D).toFixed(4), 10));
            d.push(this.fit((a.z / f.DEFAULT_STYLES.bondLength_2D).toFixed(4), 10));
            d.push(" ");
            d.push(this.fit(a.label,
                3, !0));
            d.push(m);
            d.push(g);
            d.push("  0  0  0  0\n")
        }
        for (let g = 0, f = b.bonds.length; g < f; g++) {
            a = b.bonds[g];
            e = 0;
            a.stereo === t.Bond.STEREO_AMBIGUOUS ? e = 3 : a.stereo === t.Bond.STEREO_PROTRUDING ? e = 1 : a.stereo === t.Bond.STEREO_RECESSED && (e = 6);
            d.push(this.fit((b.atoms.indexOf(a.a1) + 1).toString(), 3));
            d.push(this.fit((b.atoms.indexOf(a.a2) + 1).toString(), 3));
            a = a.bondOrder;
            if (1.5 == a) a = 4;
            else if (3 < a || 0 != a % 1) a = 1;
            d.push(this.fit(a.toString(), 3));
            d.push("  ");
            d.push(e);
            d.push("  0  0  0\n")
        }
        d.push("M  END");
        return d.join("")
    };
    let k = new l.MOLInterpreter;
    f.readMOL = function(b, d) {
        return k.read(b, d)
    };
    f.writeMOL = function(b) {
        return k.write(b)
    }
})(ChemDoodle, ChemDoodle.ELEMENT, ChemDoodle.io, ChemDoodle.structures);
(function(f, q, l, t, e, k, b) {
    function d(a, b, d, e, f) {
        for (let g = 0, h = b.length; g < h; g++) {
            let h = b[g];
            if (h.id === d && e >= h.start && e <= h.end) {
                f ? a.helix = !0 : a.sheet = !0;
                e === h.end && (a.arrow = !0);
                break
            }
        }
    }
    q.PDBInterpreter = function() {};
    b = q.PDBInterpreter.prototype = new q._Interpreter;
    b.calculateRibbonDistances = !1;
    b.deduceResidueBonds = !1;
    b.read = function(a, b) {
        let g = new l.Molecule;
        g.chains = [];
        if (!a) return g;
        var h = a.split("\n");
        b || (b = 1);
        var m = [];
        let q = [];
        let u = [];
        a = [];
        let w = [];
        for (let f = 0, n = h.length; f < n; f++) {
            var z = h[f];
            if (z.startsWith("HELIX")) m.push({
                id: z.substring(19,
                    20),
                start: parseInt(z.substring(21, 25)),
                end: parseInt(z.substring(33, 37))
            });
            else if (z.startsWith("SHEET")) q.push({
                id: z.substring(21, 22),
                start: parseInt(z.substring(22, 26)),
                end: parseInt(z.substring(33, 37))
            });
            else if (z.startsWith("ATOM")) {
                var y = z.substring(16, 17);
                if (" " === y || "A" === y) {
                    y = e(z.substring(76, 78));
                    if (0 === y.length) {
                        var c = e(z.substring(12, 14));
                        "HD" === c ? y = "H" : 0 < c.length && (y = 1 < c.length ? c.charAt(0) + c.substring(1).toLowerCase() : c)
                    }
                    y = new l.Atom(y, parseFloat(z.substring(30, 38)) * b, parseFloat(z.substring(38,
                        46)) * b, parseFloat(z.substring(46, 54)) * b);
                    y.hetatm = !1;
                    a.push(y);
                    c = parseInt(z.substring(22, 26));
                    if (0 === u.length)
                        for (var p = 0; 3 > p; p++) {
                            var A = new l.Residue(-1);
                            A.cp1 = y;
                            A.cp2 = y;
                            u.push(A)
                        }
                    u[u.length - 1].resSeq !== c && (p = new l.Residue(c), p.name = e(z.substring(17, 20)), 3 === p.name.length ? p.name = p.name.substring(0, 1) + p.name.substring(1).toLowerCase() : 2 === p.name.length && "D" === p.name.charAt(0) && (p.name = p.name.substring(1)), u.push(p), A = z.substring(21, 22), d(p, m, A, c, !0), d(p, q, A, c, !1));
                    z = e(z.substring(12, 16));
                    c = u[u.length -
                        1];
                    if ("CA" === z || "P" === z || "O5'" === z) c.cp1 || (c.cp1 = y);
                    else if ("N3" === z && ("C" === c.name || "U" === c.name || "T" === c.name) || "N1" === z && ("A" === c.name || "G" === c.name)) c.cp3 = y;
                    else if ("C2" === z) c.cp4 = y;
                    else if ("C4" === z && ("C" === c.name || "U" === c.name || "T" === c.name) || "C6" === z && ("A" === c.name || "G" === c.name)) c.cp5 = y;
                    else if ("O" === z || "C6" === z && ("C" === c.name || "U" === c.name || "T" === c.name) || "N9" === z) {
                        if (!u[u.length - 1].cp2) {
                            if ("C6" === z || "N9" === z) var B = y;
                            c.cp2 = y
                        }
                    } else "C" === z && (B = y)
                }
            } else if (z.startsWith("HETATM")) y = e(z.substring(76,
                78)), 0 === y.length && (y = e(z.substring(12, 16))), 1 < y.length && (y = y.substring(0, 1) + y.substring(1).toLowerCase()), y = new l.Atom(y, parseFloat(z.substring(30, 38)) * b, parseFloat(z.substring(38, 46)) * b, parseFloat(z.substring(46, 54)) * b), y.hetatm = !0, "HOH" === e(z.substring(17, 20)) && (y.isWater = !0), g.atoms.push(y), w[parseInt(e(z.substring(6, 11)))] = y;
            else if (z.startsWith("CONECT")) {
                if (y = parseInt(e(z.substring(6, 11))), w[y])
                    for (y = w[y], c = 0; 4 > c; c++)
                        if (p = e(z.substring(11 + 5 * c, 16 + 5 * c)), 0 !== p.length && (p = parseInt(p), w[p])) {
                            p =
                                w[p];
                            A = !1;
                            for (let a = 0, b = g.bonds.length; a < b; a++) {
                                let b = g.bonds[a];
                                if (b.a1 === y && b.a2 === p || b.a1 === p && b.a2 === y) {
                                    A = !0;
                                    break
                                }
                            }
                            A || g.bonds.push(new l.Bond(y, p))
                        }
            } else if (z.startsWith("TER")) this.endChain(g, u, B, a), u = [];
            else if (z.startsWith("ENDMDL")) break
        }
        this.endChain(g, u, B, a);
        0 === g.bonds.length && (new f.informatics.BondDeducer).deduceCovalentBonds(g, b);
        if (this.deduceResidueBonds)
            for (let c = 0, d = a.length; c < d; c++)
                for (b = k.min(d, c + 20), B = c + 1; B < b; B++) h = a[c], m = a[B], h.distance3D(m) < 1.1 * (t[h.label].covalentRadius + t[m.label].covalentRadius) &&
                    g.bonds.push(new l.Bond(h, m, 1));
        g.atoms = g.atoms.concat(a);
        this.calculateRibbonDistances && this.calculateDistances(g, a);
        return g
    };
    b.endChain = function(a, b, d, e) {
        if (0 < b.length) {
            var g = b[b.length - 1];
            g.cp1 || (g.cp1 = e[e.length - 2]);
            g.cp2 || (g.cp2 = e[e.length - 1]);
            for (e = 0; 4 > e; e++) g = new l.Residue(-1), g.cp1 = d, g.cp2 = b[b.length - 1].cp2, b.push(g);
            a.chains.push(b)
        }
    };
    b.calculateDistances = function(a, b) {
        let d = [];
        for (let b = 0, e = a.atoms.length; b < e; b++) {
            let e = a.atoms[b];
            e.hetatm && (e.isWater || d.push(e))
        }
        for (let e = 0, g = b.length; e <
            g; e++)
            if (a = b[e], a.closestDistance = Number.POSITIVE_INFINITY, 0 === d.length) a.closestDistance = 0;
            else
                for (let b = 0, e = d.length; b < e; b++) a.closestDistance = Math.min(a.closestDistance, a.distance3D(d[b]))
    };
    let h = new q.PDBInterpreter;
    f.readPDB = function(a, b) {
        return h.read(a, b)
    }
})(ChemDoodle, ChemDoodle.io, ChemDoodle.structures, ChemDoodle.ELEMENT, ChemDoodle.lib.jQuery.trim, Math);
(function(f, q, l, t, e) {
    let k = {
            "@": 0,
            A: 1,
            B: 2,
            C: 3,
            D: 4,
            E: 5,
            F: 6,
            G: 7,
            H: 8,
            I: 9,
            a: -1,
            b: -2,
            c: -3,
            d: -4,
            e: -5,
            f: -6,
            g: -7,
            h: -8,
            i: -9
        },
        b = {
            "%": 0,
            J: 1,
            K: 2,
            L: 3,
            M: 4,
            N: 5,
            O: 6,
            P: 7,
            Q: 8,
            R: 9,
            j: -1,
            k: -2,
            l: -3,
            m: -4,
            n: -5,
            o: -6,
            p: -7,
            q: -8,
            r: -9
        },
        d = {
            S: 1,
            T: 2,
            U: 3,
            V: 4,
            W: 5,
            X: 6,
            Y: 7,
            Z: 8,
            s: 9
        };
    q.JCAMPInterpreter = function() {};
    t = q.JCAMPInterpreter.prototype = new q._Interpreter;
    t.convertHZ2PPM = !1;
    t.read = function(a) {
        this.isBreak = function(a) {
            return k[a] !== e || b[a] !== e || d[a] !== e || " " === a || "-" === a || "+" === a
        };
        this.getValue = function(a, c) {
            let d = a.charAt(0);
            a = a.substring(1);
            return k[d] !== e ? parseFloat(k[d] + a) : b[d] !== e ? parseFloat(b[d] + a) + c : parseFloat(a)
        };
        let g = new l.Spectrum;
        if (a === e || 0 === a.length) return g;
        a = a.split("\n");
        let f = [],
            h, m, q, u, w = 1,
            t = 1,
            y = 1,
            c = -1;
        var p = -1;
        let A = !0,
            B = !1;
        for (let n = 0, v = a.length; n < v; n++) {
            var C = a[n].trim(),
                D = C.indexOf("$$"); - 1 !== D && (C = C.substring(0, D));
            if (0 !== f.length && a[n].startsWith("##"))
                if (D = f.join(""), A && 100 > D.length && g.metadata.push(D), f = [C], D.startsWith("##TITLE\x3d")) g.title = D.substring(8).trim();
                else if (D.startsWith("##XUNITS\x3d")) g.xUnit =
                D.substring(9).trim(), this.convertHZ2PPM && "HZ" === g.xUnit.toUpperCase() && (g.xUnit = "PPM", B = !0);
            else if (D.startsWith("##YUNITS\x3d")) g.yUnit = D.substring(9).trim();
            else {
                if (!D.startsWith("##XYPAIRS\x3d"))
                    if (D.startsWith("##FIRSTX\x3d")) m = parseFloat(D.substring(9).trim());
                    else if (D.startsWith("##LASTX\x3d")) h = parseFloat(D.substring(8).trim());
                else if (D.startsWith("##FIRSTY\x3d")) q = parseFloat(D.substring(9).trim());
                else if (D.startsWith("##NPOINTS\x3d")) u = parseFloat(D.substring(10).trim());
                else if (D.startsWith("##XFACTOR\x3d")) w =
                    parseFloat(D.substring(10).trim());
                else if (D.startsWith("##YFACTOR\x3d")) t = parseFloat(D.substring(10).trim());
                else if (D.startsWith("##DELTAX\x3d")) parseFloat(D.substring(9).trim());
                else if (D.startsWith("##.OBSERVE FREQUENCY\x3d")) this.convertHZ2PPM && (y = parseFloat(D.substring(21).trim()));
                else if (D.startsWith("##.SHIFT REFERENCE\x3d")) this.convertHZ2PPM && (p = D.substring(19).split(","), c = parseInt(p[2].trim()), p = parseFloat(p[3].trim()));
                else if (D.startsWith("##XYDATA\x3d")) {
                    B || (y = 1);
                    C = A = !1;
                    D = D.split("\n");
                    var F = (h - m) / (u - 1),
                        L = m - F,
                        H = q,
                        K = 0;
                    let a;
                    for (let c = 1, f = D.length; c < f; c++) {
                        var N = [];
                        L = D[c].trim();
                        H = [];
                        for (let a = 0, b = L.length; a < b; a++) this.isBreak(L.charAt(a)) ? (0 < H.length && (1 !== H.length || " " !== H[0]) && N.push(H.join("")), H = [L.charAt(a)]) : H.push(L.charAt(a));
                        N.push(H.join(""));
                        L = parseFloat(N[0]) * w - F;
                        for (let c = 1, f = N.length; c < f; c++)
                            if (H = N[c], d[H.charAt(0)] !== e) {
                                let b = parseInt(d[H.charAt(0)] + H.substring(1)) - 1;
                                for (let c = 0; c < b; c++) L += F, K = this.getValue(a, K), H = K * t, g.data[g.data.length - 1] = new l.Point(L / y, H)
                            } else k[H.charAt(0)] !==
                                e && C ? H = this.getValue(H, K) * t : (C = b[H.charAt(0)] !== e, a = H, L += F, K = this.getValue(H, K), H = K * t, g.data.push(new l.Point(L / y, H)))
                    }
                    if (-1 !== c) {
                        C = p - g.data[c - 1].x;
                        for (let a = 0, b = g.data.length; a < b; a++) g.data[a].x += C
                    }
                } else if (D.startsWith("##PEAK TABLE\x3d")) {
                    A = !1;
                    g.continuous = !1;
                    C = D.split("\n");
                    D = /[\s,]+/;
                    for (let a = 1, b = C.length; a < b; a++) {
                        F = C[a].split(D);
                        for (let a = 0, b = F.length; a + 1 < b; a += 2) g.data.push(new l.Point(parseFloat(F[a].trim()), parseFloat(F[a + 1].trim())))
                    }
                } else if (D.startsWith("##ATOMLIST\x3d")) {
                    g.molecule = new l.Molecule;
                    C = D.split("\n");
                    D = /[\s]+/;
                    for (let a = 1, b = C.length; a < b; a++) F = C[a].split(D), g.molecule.atoms.push(new l.Atom(F[1]))
                } else if (D.startsWith("##BONDLIST\x3d")) {
                    C = D.split("\n");
                    D = /[\s]+/;
                    for (let a = 1, b = C.length; a < b; a++) F = C[a].split(D), K = 1, "D" === F[2] ? K = 2 : "T" === F[2] && (K = 3), g.molecule.bonds.push(new l.Bond(g.molecule.atoms[parseInt(F[0]) - 1], g.molecule.atoms[parseInt(F[1]) - 1], K))
                } else if (g.molecule && D.startsWith("##XY_RASTER\x3d")) {
                    C = D.split("\n");
                    D = /[\s]+/;
                    for (let a = 1, b = C.length; a < b; a++) F = C[a].split(D), K = g.molecule.atoms[parseInt(F[0]) -
                        1], K.x = parseInt(F[1]), K.y = parseInt(F[2]), 4 == F.length && (K.z = parseInt(F[3]));
                    g.molecule.scaleToAverageBondLength(20)
                } else if (D.startsWith("##PEAK ASSIGNMENTS\x3d")) {
                    C = D.split("\n");
                    D = /[\s,()<>]+/;
                    g.assignments = [];
                    for (let a = 1, b = C.length; a < b; a++) {
                        N = C[a].split(D);
                        F = parseFloat(N[1]);
                        K = parseFloat(N[2]);
                        N = g.molecule.atoms[parseInt(N[3]) - 1];
                        L = !1;
                        for (let a = 0, b = g.assignments.length; a < b; a++)
                            if (H = g.assignments[a], H.x === F) {
                                H.as.push(N);
                                N.assigned = H;
                                L = !0;
                                break
                            } L || (F = {
                            x: F,
                            y: K,
                            as: [N]
                        }, N.assigned = F, g.assignments.push(F))
                    }
                }
            } else C =
                C.trim(), 0 !== f.length && 0 !== C.length && f.push("\n"), f.push(C)
        }
        g.setup();
        return g
    };
    t.makeStructureSpectrumSet = function(a, b) {
        this.convertHZ2PPM = !0;
        let d = this.read(b),
            g = new f.ViewerCanvas(a + "_molecule", 200, 200);
        g.styles.atoms_displayTerminalCarbonLabels_2D = !0;
        g.styles.atoms_displayImplicitHydrogens_2D = !0;
        g.mouseout = function(a) {
            if (0 !== this.molecules.length) {
                for (let a = 0, b = this.molecules[0].atoms.length; a < b; a++) this.molecules[0].atoms[a].isHover = !1;
                d.hovered = e;
                this.repaint();
                h.repaint()
            }
        };
        g.touchend = g.mouseout;
        g.mousemove = function(a) {
            if (0 !== this.molecules.length) {
                let b = e;
                for (let d = 0, g = this.molecules[0].atoms.length; d < g; d++) {
                    let g = this.molecules[0].atoms[d];
                    g.isHover = !1;
                    g.assigned && (b === e || a.p.distance(g) < a.p.distance(b)) && (b = g)
                }
                d.hovered = e;
                if (20 > a.p.distance(b)) {
                    for (let a = 0, d = b.assigned.as.length; a < d; a++) b.assigned.as[a].isHover = !0;
                    h.spectrum.hovered = b.assigned
                }
                this.repaint();
                h.repaint()
            }
        };
        g.touchmove = g.mousemove;
        g.drawChildExtras = function(a, b) {
            if (0 !== this.molecules.length)
                for (let d = 0, e = this.molecules[0].atoms.length; d <
                    e; d++) this.molecules[0].atoms[d].drawDecorations(a, b)
        };
        let h = new f.ObserverCanvas(a + "_spectrum", 400, 200);
        h.styles.plots_showYAxis = !1;
        h.styles.plots_flipXAxis = !0;
        h.mouseout = function(a) {
            if (this.spectrum && this.spectrum.assignments) {
                for (let a = 0, b = g.molecules[0].atoms.length; a < b; a++) g.molecules[0].atoms[a].isHover = !1;
                this.spectrum.hovered = e;
                g.repaint();
                this.repaint()
            }
        };
        h.touchend = h.mouseout;
        h.mousemove = function(a) {
            if (this.spectrum && this.spectrum.assignments) {
                let b = e;
                for (let a = 0, b = g.molecules[0].atoms.length; a <
                    b; a++) g.molecules[0].atoms[a].isHover = !1;
                this.spectrum.hovered = e;
                for (let d = 0, g = this.spectrum.assignments.length; d < g; d++) {
                    let g = this.spectrum.assignments[d];
                    if (b === e || Math.abs(this.spectrum.getTransformedX(g.x, this.styles, this.spectrum.memory.width, this.spectrum.memory.offsetLeft) - a.p.x) < Math.abs(this.spectrum.getTransformedX(b.x, this.styles, this.spectrum.memory.width, this.spectrum.memory.offsetLeft) - a.p.x)) b = g
                }
                if (20 > Math.abs(this.spectrum.getTransformedX(b.x, this.styles, this.spectrum.memory.width,
                        this.spectrum.memory.offsetLeft) - a.p.x)) {
                    for (let a = 0, d = b.as.length; a < d; a++) b.as[a].isHover = !0;
                    this.spectrum.hovered = b
                }
                g.repaint();
                this.repaint()
            }
        };
        h.touchmove = h.mousemove;
        h.drawChildExtras = function(a) {
            if (this.spectrum && this.spectrum.hovered) {
                let b = this.spectrum.getTransformedX(this.spectrum.hovered.x, h.styles, this.spectrum.memory.width, this.spectrum.memory.offsetLeft);
                b >= this.spectrum.memory.offsetLeft && b < this.spectrum.memory.width && (a.save(), a.strokeStyle = "#885110", a.lineWidth = 3, a.beginPath(), a.moveTo(b,
                    this.spectrum.memory.height - this.spectrum.memory.offsetBottom), a.lineTo(b, this.spectrum.getTransformedY(this.spectrum.hovered.y, h.styles, this.spectrum.memory.height, this.spectrum.memory.offsetBottom, this.spectrum.memory.offsetTop)), a.stroke(), a.restore())
            }
        };
        d && (h.loadSpectrum(d), d.molecule && g.loadMolecule(d.molecule));
        return [g, h]
    };
    let h = new q.JCAMPInterpreter;
    h.convertHZ2PPM = !0;
    f.readJCAMP = function(a) {
        return h.read(a)
    }
})(ChemDoodle, ChemDoodle.io, ChemDoodle.structures, ChemDoodle.lib.jQuery);
(function(f, q, l, t, e, k, b) {
    q.JSONInterpreter = function() {};
    let d = q.JSONInterpreter.prototype;
    d.contentTo = function(a, d) {
        a || (a = []);
        d || (d = []);
        var e = 0,
            g = 0;
        for (let b = 0, d = a.length; b < d; b++) {
            let d = a[b];
            for (let a = 0, b = d.atoms.length; a < b; a++) d.atoms[a].tmpid = "a" + e++;
            for (let a = 0, b = d.bonds.length; a < b; a++) d.bonds[a].tmpid = "b" + g++
        }
        e = 0;
        for (let a = 0, b = d.length; a < b; a++) d[a].tmpid = "s" + e++;
        e = {};
        if (a && 0 < a.length) {
            e.m = [];
            for (let b = 0, d = a.length; b < d; b++) e.m.push(this.molTo(a[b]))
        }
        if (d && 0 < d.length) {
            e.s = [];
            for (let a = 0, b = d.length; a <
                b; a++) e.s.push(this.shapeTo(d[a]))
        }
        for (let d = 0, e = a.length; d < e; d++) {
            g = a[d];
            for (let a = 0, d = g.atoms.length; a < d; a++) g.atoms[a].tmpid = b;
            for (let a = 0, d = g.bonds.length; a < d; a++) g.bonds[a].tmpid = b
        }
        for (let a = 0, e = d.length; a < e; a++) d[a].tmpid = b;
        return e
    };
    d.contentFrom = function(a) {
        let d = {
            molecules: [],
            shapes: []
        };
        if (a.m)
            for (let b = 0, e = a.m.length; b < e; b++) d.molecules.push(this.molFrom(a.m[b]));
        if (a.s)
            for (let b = 0, e = a.s.length; b < e; b++) d.shapes.push(this.shapeFrom(a.s[b], d.molecules));
        for (let e = 0, g = d.molecules.length; e <
            g; e++) {
            a = d.molecules[e];
            for (let d = 0, e = a.atoms.length; d < e; d++) a.atoms[d].tmpid = b;
            for (let d = 0, e = a.bonds.length; d < e; d++) a.bonds[d].tmpid = b
        }
        for (let a = 0, e = d.shapes.length; a < e; a++) d.shapes[a].tmpid = b;
        return d
    };
    d.queryTo = function(a) {
        let b = {},
            d = function(b, d, e, g) {
                d && (b[e] = {
                    v: g ? a.outputRange(d.v) : d.v,
                    n: d.not
                })
            };
        a.type === l.Query.TYPE_ATOM ? (d(b, a.elements, "as"), d(b, a.chirality, "@"), d(b, a.aromatic, "A"), d(b, a.charge, "C", !0), d(b, a.hydrogens, "H", !0), d(b, a.ringCount, "R", !0), d(b, a.saturation, "S"), d(b, a.connectivity,
            "X", !0), d(b, a.connectivityNoH, "x", !0)) : (d(b, a.orders, "bs"), d(b, a.stereo, "@"), d(b, a.aromatic, "A"), d(b, a.ringCount, "R", !0));
        return b
    };
    d.molTo = function(a) {
        let b = {
            a: []
        };
        for (let g = 0, f = a.atoms.length; g < f; g++) {
            var d = a.atoms[g],
                e = {
                    x: d.x,
                    y: d.y
                };
            d.tmpid && (e.i = d.tmpid);
            "C" !== d.label && (e.l = d.label);
            0 !== d.z && (e.z = d.z);
            0 !== d.charge && (e.c = d.charge); - 1 !== d.mass && (e.m = d.mass); - 1 !== d.implicitH && (e.h = d.implicitH);
            0 !== d.numRadical && (e.r = d.numRadical);
            0 !== d.numLonePair && (e.p = d.numLonePair);
            d.query && (e.q = this.queryTo(d.query));
            b.a.push(e)
        }
        if (0 < a.bonds.length) {
            b.b = [];
            for (let g = 0, f = a.bonds.length; g < f; g++) d = a.bonds[g], e = {
                b: a.atoms.indexOf(d.a1),
                e: a.atoms.indexOf(d.a2)
            }, d.tmpid && (e.i = d.tmpid), 1 !== d.bondOrder && (e.o = d.bondOrder), d.stereo !== l.Bond.STEREO_NONE && (e.s = d.stereo), d.query && (e.q = this.queryTo(d.query)), b.b.push(e)
        }
        return b
    };
    d.queryFrom = function(a) {
        let b = new l.Query(a.as ? l.Query.TYPE_ATOM : l.Query.TYPE_BOND),
            d = function(a, b, d, e) {
                b && (a[d] = {}, a[d].v = e ? a.parseRange(b.v) : b.v, b.n && (a[d].not = !0))
            };
        b.type === l.Query.TYPE_ATOM ? (d(b,
            a.as, "elements"), d(b, a["@"], "chirality"), d(b, a.A, "aromatic"), d(b, a.C, "charge", !0), d(b, a.H, "hydrogens", !0), d(b, a.R, "ringCount", !0), d(b, a.S, "saturation"), d(b, a.X, "connectivity", !0), d(b, a.x, "connectivityNoH", !0)) : (d(b, a.bs, "orders"), d(b, a["@"], "stereo"), d(b, a.A, "aromatic"), d(b, a.R, "ringCount", !0));
        return b
    };
    d.molFrom = function(a) {
        let d = new l.Molecule;
        for (let g = 0, h = a.a.length; g < h; g++) {
            var e = a.a[g],
                f = new l.Atom(e.l ? e.l : "C", e.x, e.y);
            e.i && (f.tmpid = e.i);
            e.z && (f.z = e.z);
            e.c && (f.charge = e.c);
            e.m && (f.mass = e.m);
            e.h && (f.implicitH = e.h);
            e.r && (f.numRadical = e.r);
            e.p && (f.numLonePair = e.p);
            e.q && (f.query = this.queryFrom(e.q));
            e.p_h !== b && (f.hetatm = e.p_h);
            e.p_w !== b && (f.isWater = e.p_w);
            e.p_d !== b && (f.closestDistance = e.p_d);
            d.atoms.push(f)
        }
        if (a.b)
            for (let g = 0, h = a.b.length; g < h; g++) e = a.b[g], f = new l.Bond(d.atoms[e.b], d.atoms[e.e], e.o === b ? 1 : e.o), e.i && (f.tmpid = e.i), e.s && (f.stereo = e.s), e.q && (f.query = this.queryFrom(e.q)), d.bonds.push(f);
        return d
    };
    d.shapeTo = function(a) {
        let b = {};
        a.tmpid && (b.i = a.tmpid);
        if (a instanceof t.Line) b.t =
            "Line", b.x1 = a.p1.x, b.y1 = a.p1.y, b.x2 = a.p2.x, b.y2 = a.p2.y, b.a = a.arrowType;
        else if (a instanceof t.Pusher) b.t = "Pusher", b.o1 = a.o1.tmpid, b.o2 = a.o2.tmpid, 1 !== a.numElectron && (b.e = a.numElectron);
        else if (a instanceof t.AtomMapping) b.t = "AtomMapping", b.a1 = a.o1.tmpid, b.a2 = a.o2.tmpid;
        else if (a instanceof t.Bracket) b.t = "Bracket", b.x1 = a.p1.x, b.y1 = a.p1.y, b.x2 = a.p2.x, b.y2 = a.p2.y, 0 !== a.charge && (b.c = a.charge), 0 !== a.mult && (b.m = a.mult), 0 !== a.repeat && (b.r = a.repeat);
        else if (a instanceof t.RepeatUnit) b.t = "RepeatUnit", b.b1 =
            a.b1.tmpid, b.b2 = a.b2.tmpid, b.n1 = a.n1, b.n2 = a.n2, !0 === a.flip && (b.f = !0);
        else if (a instanceof t.VAP) {
            b.t = "VAP";
            b.x = a.asterisk.x;
            b.y = a.asterisk.y;
            1 !== a.bondType && (b.o = a.bondType);
            a.substituent && (b.s = a.substituent.tmpid);
            b.a = [];
            for (let d = 0, e = a.attachments.length; d < e; d++) b.a.push(a.attachments[d].tmpid)
        } else if (a instanceof e.Distance) b.t = "Distance", b.a1 = a.a1.tmpid, b.a2 = a.a2.tmpid, a.node && (b.n = a.node, b.o = a.offset);
        else if (a instanceof e.Angle) b.t = "Angle", b.a1 = a.a1.tmpid, b.a2 = a.a2.tmpid, b.a3 = a.a3.tmpid;
        else if (a instanceof e.Torsion) b.t = "Torsion", b.a1 = a.a1.tmpid, b.a2 = a.a2.tmpid, b.a3 = a.a3.tmpid, b.a4 = a.a4.tmpid;
        else if (a instanceof e._Surface) {
            b.t = "Surface";
            b.a = [];
            for (let d = 0, e = a.atoms.length; d < e; d++) b.a.push(a.atoms[d].tmpid);
            a instanceof e.VDWSurface || (b.p = a.probeRadius);
            b.r = a.resolution;
            let d = "vdw";
            a instanceof e.SASSurface ? d = "sas" : e.SESSurface && a instanceof e.SESSurface && (d = "ses");
            b.f = d
        } else a instanceof e.UnitCell && (b.t = "UnitCell", b.ls = a.lengths, b.as = a.angles, b.os = a.offset);
        return b
    };
    d.shapeFrom = function(a, d) {
        if ("Line" ===
            a.t) {
            var f = new t.Line(new l.Point(a.x1, a.y1), new l.Point(a.x2, a.y2));
            f.arrowType = a.a
        } else if ("Pusher" === a.t) {
            var g, h;
            for (let b = 0, e = d.length; b < e; b++) {
                f = d[b];
                for (let b = 0, d = f.atoms.length; b < d; b++) {
                    var k = f.atoms[b];
                    k.tmpid === a.o1 ? g = k : k.tmpid === a.o2 && (h = k)
                }
                for (let b = 0, d = f.bonds.length; b < d; b++) k = f.bonds[b], k.tmpid === a.o1 ? g = k : k.tmpid === a.o2 && (h = k)
            }
            f = new t.Pusher(g, h);
            a.e && (f.numElectron = a.e)
        } else if ("AtomMapping" === a.t) {
            let b;
            for (let e = 0, h = d.length; e < h; e++) {
                f = d[e];
                for (let d = 0, c = f.atoms.length; d < c; d++) g =
                    f.atoms[d], g.tmpid === a.a1 ? k = g : g.tmpid === a.a2 && (b = g)
            }
            f = new t.AtomMapping(k, b)
        } else if ("Bracket" === a.t) f = new t.Bracket(new l.Point(a.x1, a.y1), new l.Point(a.x2, a.y2)), a.c !== b && (f.charge = a.c), a.m !== b && (f.mult = a.m), a.r !== b && (f.repeat = a.r);
        else if ("RepeatUnit" === a.t || "DynamicBracket" === a.t) {
            let b, e;
            for (let h = 0, m = d.length; h < m; h++) {
                f = d[h];
                for (let c = 0, d = f.bonds.length; c < d; c++) g = f.bonds[c], g.tmpid === a.b1 ? b = g : g.tmpid === a.b2 && (e = g)
            }
            f = new t.RepeatUnit(b, e);
            f.n1 = a.n1;
            f.n2 = a.n2;
            a.f && (f.flip = !0)
        } else if ("VAP" ===
            a.t) {
            f = new t.VAP(a.x, a.y);
            a.o && (f.bondType = a.o);
            for (let b = 0, e = d.length; b < e; b++) {
                g = d[b];
                for (let b = 0, d = g.atoms.length; b < d; b++)
                    if (h = g.atoms[b], h.tmpid === a.s) f.substituent = h;
                    else
                        for (let b = 0, d = a.a.length; b < d; b++) h.tmpid === a.a[b] && f.attachments.push(h)
            }
        } else if ("Distance" === a.t) {
            let b, h;
            for (let e = 0, m = d.length; e < m; e++) {
                f = d[e];
                for (let c = 0, d = f.atoms.length; c < d; c++) g = f.atoms[c], g.tmpid === a.a1 ? b = g : g.tmpid === a.a2 && (h = g)
            }
            f = new e.Distance(b, h, a.n, a.o)
        } else if ("Angle" === a.t) {
            let b, h, m;
            for (let e = 0, c = d.length; e <
                c; e++) {
                f = d[e];
                for (let c = 0, d = f.atoms.length; c < d; c++) g = f.atoms[c], g.tmpid === a.a1 ? b = g : g.tmpid === a.a2 ? h = g : g.tmpid === a.a3 && (m = g)
            }
            f = new e.Angle(b, h, m)
        } else if ("Torsion" === a.t) {
            let b, h, m, k;
            for (let c = 0, e = d.length; c < e; c++) {
                f = d[c];
                for (let c = 0, d = f.atoms.length; c < d; c++) g = f.atoms[c], g.tmpid === a.a1 ? b = g : g.tmpid === a.a2 ? h = g : g.tmpid === a.a3 ? m = g : g.tmpid === a.a4 && (k = g)
            }
            f = new e.Torsion(b, h, m, k)
        } else if ("Surface" === a.t) {
            g = [];
            for (let b = 0, e = d.length; b < e; b++) {
                h = d[b];
                for (let b = 0, d = h.atoms.length; b < d; b++) {
                    k = h.atoms[b];
                    for (let b =
                            0, d = a.a.length; b < d; b++) k.tmpid === a.a[b] && g.push(k)
                }
            }
            d = a.p ? a.p : 1.4;
            h = a.r ? a.r : 30;
            "vdw" === a.f ? f = new e.VDWSurface(g, h) : "sas" === a.f ? f = new e.SASSurface(g, d, h) : "ses" === a.f && (f = new e.SESSurface(g, d, h))
        } else "UnitCell" === a.t && (f = new e.UnitCell(a.ls, a.as, a.os));
        return f
    };
    d.pdbFrom = function(a) {
        let b = this.molFrom(a.mol);
        b.findRings = !1;
        b.fromJSON = !0;
        b.chains = this.chainsFrom(a.ribbons);
        return b
    };
    d.chainsFrom = function(a) {
        let b = [];
        for (let d = 0, e = a.cs.length; d < e; d++) {
            let e = a.cs[d],
                f = [];
            for (let a = 0, b = e.length; a < b; a++) {
                let b =
                    e[a],
                    d = new l.Residue;
                d.name = b.n;
                d.cp1 = new l.Atom("", b.x1, b.y1, b.z1);
                d.cp2 = new l.Atom("", b.x2, b.y2, b.z2);
                b.x3 && (d.cp3 = new l.Atom("", b.x3, b.y3, b.z3), d.cp4 = new l.Atom("", b.x4, b.y4, b.z4), d.cp5 = new l.Atom("", b.x5, b.y5, b.z5));
                d.helix = b.h;
                d.sheet = b.s;
                d.arrow = 0 < a && e[a - 1].a;
                f.push(d)
            }
            b.push(f)
        }
        return b
    };
    let h = new q.JSONInterpreter;
    f.readJSON = function(a) {
        let d;
        try {
            d = k.parse(a)
        } catch (n) {
            return b
        }
        return d ? d.m || d.s ? h.contentFrom(d) : d.a ? {
            molecules: [h.molFrom(d)],
            shapes: []
        } : {
            molecules: [],
            shapes: []
        } : b
    };
    f.writeJSON =
        function(a, b) {
            return k.stringify(h.contentTo(a, b))
        }
})(ChemDoodle, ChemDoodle.io, ChemDoodle.structures, ChemDoodle.structures.d2, ChemDoodle.structures.d3, JSON);
(function(f, q, l, t) {
    q.RXNInterpreter = function() {};
    let e = q.RXNInterpreter.prototype = new q._Interpreter;
    e.read = function(b, d) {
        d || (d = f.DEFAULT_STYLES.bondLength_2D);
        let e = [];
        if (b) {
            var a = b.split("$MOL\n");
            b = a[0].split("\n")[4];
            var g = parseInt(b.substring(0, 3)),
                k = parseInt(b.substring(3, 6)),
                q = 1;
            b = 0;
            for (let h = 0, n = g + k; h < n; h++) {
                e[h] = f.readMOL(a[q], d);
                let g = e[h].getBounds();
                b -= g.maxX - g.minX + 40;
                q++
            }
            for (let f = 0, h = g; f < h; f++) {
                d = e[f].getBounds();
                d = d.maxX - d.minX;
                a = e[f].getCenter();
                for (let g = 0, h = e[f].atoms.length; g <
                    h; g++) q = e[f].atoms[g], q.x += b + d / 2 - a.x, q.y -= a.y;
                b += d + 40
            }
            d = new l.d2.Line(new l.Point(b, 0), new l.Point(b + 40, 0));
            b += 80;
            for (let d = g, f = g + k; d < f; d++) {
                g = e[d].getBounds();
                g = g.maxX - g.minX;
                k = e[d].getCenter();
                for (a = 0; a < e[d].atoms.length; a++) q = e[d].atoms[a], q.x += b + g / 2 - k.x, q.y -= k.y;
                b += g + 40
            }
        } else e.push(new l.Molecule), d = new l.d2.Line(new l.Point(-20, 0), new l.Point(20, 0));
        d.arrowType = l.d2.Line.ARROW_SYNTHETIC;
        return {
            molecules: e,
            shapes: [d]
        }
    };
    e.write = function(b, d) {
        let e = [
                [],
                []
            ],
            a = t;
        if (b && d) {
            for (let b = 0, e = d.length; b <
                e; b++)
                if (d[b] instanceof l.d2.Line) {
                    a = d[b].getPoints();
                    break
                } if (!a) return "";
            for (let d = 0, f = b.length; d < f; d++) b[d].getCenter().x < a[1].x ? e[0].push(b[d]) : e[1].push(b[d]);
            b = [];
            b.push("$RXN\nReaction from ChemDoodle Web Components\n\nhttp://www.ichemlabs.com\n");
            b.push(this.fit(e[0].length.toString(), 3));
            b.push(this.fit(e[1].length.toString(), 3));
            b.push("\n");
            for (d = 0; 2 > d; d++)
                for (let a = 0, h = e[d].length; a < h; a++) b.push("$MOL\n"), b.push(f.writeMOL(e[d][a])), b.push("\n");
            return b.join("")
        }
    };
    let k = new q.RXNInterpreter;
    f.readRXN = function(b, d) {
        return k.read(b, d)
    };
    f.writeRXN = function(b, d) {
        return k.write(b, d)
    }
})(ChemDoodle, ChemDoodle.io, ChemDoodle.structures);
(function(f, q, l, t, e, k, b) {
    t.XYZInterpreter = function() {};
    q = t.XYZInterpreter.prototype = new t._Interpreter;
    q.deduceCovalentBonds = !0;
    q.read = function(b) {
        let a = new e.Molecule;
        if (!b) return a;
        b = b.split("\n");
        let d = parseInt(k(b[0]));
        for (let f = 0; f < d; f++) {
            let d = b[f + 2].split(/\s+/g);
            a.atoms[f] = new e.Atom(isNaN(d[0]) ? d[0] : l[parseInt(d[0]) - 1], parseFloat(d[1]), parseFloat(d[2]), parseFloat(d[3]))
        }
        this.deduceCovalentBonds && (new f.informatics.BondDeducer).deduceCovalentBonds(a, 1);
        return a
    };
    let d = new t.XYZInterpreter;
    f.readXYZ = function(b) {
        return d.read(b)
    }
})(ChemDoodle, ChemDoodle.ELEMENT, ChemDoodle.SYMBOLS, ChemDoodle.io, ChemDoodle.structures, ChemDoodle.lib.jQuery.trim);
ChemDoodle.monitor = function(f, q, l, t) {
    let e = {};
    e.CANVAS_DRAGGING = t;
    e.CANVAS_OVER = t;
    e.ALT = !1;
    e.SHIFT = !1;
    e.META = !1;
    f.supports_touch() || q(l).ready(function() {
        q(l).mousemove(function(f) {
            e.CANVAS_DRAGGING && e.CANVAS_DRAGGING.drag && (e.CANVAS_DRAGGING.prehandleEvent(f), e.CANVAS_DRAGGING.drag(f))
        });
        q(l).mouseup(function(f) {
            e.CANVAS_DRAGGING && e.CANVAS_DRAGGING !== e.CANVAS_OVER && e.CANVAS_DRAGGING.mouseup && (e.CANVAS_DRAGGING.prehandleEvent(f), e.CANVAS_DRAGGING.mouseup(f));
            e.CANVAS_DRAGGING = t
        });
        q(l).keydown(function(f) {
            e.SHIFT =
                f.shiftKey;
            e.ALT = f.altKey;
            e.META = f.metaKey || f.ctrlKey;
            let b = e.CANVAS_OVER;
            e.CANVAS_DRAGGING && (b = e.CANVAS_DRAGGING);
            b && b.keydown && (b.prehandleEvent(f), b.keydown(f))
        });
        q(l).keypress(function(f) {
            let b = e.CANVAS_OVER;
            e.CANVAS_DRAGGING && (b = e.CANVAS_DRAGGING);
            b && b.keypress && (b.prehandleEvent(f), b.keypress(f))
        });
        q(l).keyup(function(f) {
            e.SHIFT = f.shiftKey;
            e.ALT = f.altKey;
            e.META = f.metaKey || f.ctrlKey;
            let b = e.CANVAS_OVER;
            e.CANVAS_DRAGGING && (b = e.CANVAS_DRAGGING);
            b && b.keyup && (b.prehandleEvent(f), b.keyup(f))
        })
    });
    return e
}(ChemDoodle.featureDetection, ChemDoodle.lib.jQuery, document);
(function(f, q, l, t, e, k, b, d, h, a, g) {
    f._Canvas = function() {};
    let n = f._Canvas.prototype;
    n.molecules = g;
    n.shapes = g;
    n.emptyMessage = g;
    n.image = g;
    n.repaint = function() {
        if (!this.test) {
            var a = d.getElementById(this.id);
            if (a.getContext) {
                let b = a.getContext("2d");
                1 !== this.pixelRatio && a.width === this.width && (a.width = this.width * this.pixelRatio, a.height = this.height * this.pixelRatio, b.scale(this.pixelRatio, this.pixelRatio));
                if (this.image) b.drawImage(this.image, 0, 0);
                else {
                    let d = this.styles.backgroundColor ? this.styles.backgroundColor :
                        "transparent";
                    b.clearRect(0, 0, this.width, this.height);
                    this.bgCache !== d && (a.style.backgroundColor = d, this.bgCache = a.style.backgroundColor);
                    "transparent" !== d && (b.fillStyle = d, b.fillRect(0, 0, this.width, this.height))
                }
                if (this.innerRepaint) this.innerRepaint(b);
                else if (0 !== this.molecules.length || 0 !== this.shapes.length) {
                    b.save();
                    b.translate(this.width / 2, this.height / 2);
                    b.rotate(this.styles.rotateAngle);
                    b.scale(this.styles.scale, this.styles.scale);
                    b.translate(-this.width / 2, -this.height / 2);
                    for (let a = 0, d = this.molecules.length; a <
                        d; a++) this.molecules[a].check(!0), this.molecules[a].draw(b, this.styles);
                    this.checksOnAction && this.checksOnAction(!0);
                    for (let a = 0, d = this.shapes.length; a < d; a++) this.shapes[a].draw(b, this.styles);
                    b.restore()
                } else this.emptyMessage && (b.fillStyle = "#737683", b.textAlign = "center", b.textBaseline = "middle", b.font = "18px Helvetica, Verdana, Arial, Sans-serif", b.fillText(this.emptyMessage, this.width / 2, this.height / 2));
                this.drawChildExtras && this.drawChildExtras(b, this.styles)
            }
        }
    };
    n.resize = function(a, b) {
        let d = k("#" +
            this.id);
        d.attr({
            width: a,
            height: b
        });
        d.css("width", a);
        d.css("height", b);
        this.width = a;
        this.height = b;
        if (f._Canvas3D && this instanceof f._Canvas3D) 1 !== this.pixelRatio && (a *= this.pixelRatio, b *= this.pixelRatio, this.gl.canvas.width = a, this.gl.canvas.height = b), this.gl.viewport(0, 0, a, b), this.afterLoadContent();
        else if (0 < this.molecules.length) {
            this.center();
            for (let a = 0, b = this.molecules.length; a < b; a++) this.molecules[a].check()
        }
        this.repaint()
    };
    n.setBackgroundImage = function(a) {
        this.image = new Image;
        let b = this;
        this.image.onload =
            function() {
                b.repaint()
            };
        this.image.src = a
    };
    n.loadMolecule = function(a) {
        this.clear();
        this.molecules.push(a);
        for (let b = 0; 2 > b; b++) this.center(), f._Canvas3D && this instanceof f._Canvas3D || a.check(), this.afterLoadContent && this.afterLoadContent(), this.repaint()
    };
    n.loadContent = function(a, b) {
        this.molecules = a ? a : [];
        this.shapes = b ? b : [];
        for (a = 0; 2 > a; a++) {
            this.center();
            if (!(f._Canvas3D && this instanceof f._Canvas3D))
                for (let a = 0, b = this.molecules.length; a < b; a++) this.molecules[a].check();
            this.afterLoadContent && this.afterLoadContent();
            this.repaint()
        }
    };
    n.addMolecule = function(a) {
        this.molecules.push(a);
        f._Canvas3D && this instanceof f._Canvas3D || a.check();
        this.repaint()
    };
    n.removeMolecule = function(a) {
        this.molecules = k.grep(this.molecules, function(b) {
            return b !== a
        });
        this.repaint()
    };
    n.getMolecule = function() {
        return 0 < this.molecules.length ? this.molecules[0] : g
    };
    n.getMolecules = function() {
        return this.molecules
    };
    n.addShape = function(a) {
        this.shapes.push(a);
        this.repaint()
    };
    n.removeShape = function(a) {
        this.shapes = k.grep(this.shapes, function(b) {
            return b !==
                a
        });
        this.repaint()
    };
    n.getShapes = function() {
        return this.shapes
    };
    n.clear = function() {
        this.molecules = [];
        this.shapes = [];
        this.styles.scale = 1;
        this.repaint()
    };
    n.center = function() {
        var a = this.getContentBounds(),
            d = new e.Point((this.width - a.minX - a.maxX) / 2, (this.height - a.minY - a.maxY) / 2);
        for (let a = 0, b = this.molecules.length; a < b; a++) {
            var f = this.molecules[a];
            for (let a = 0, b = f.atoms.length; a < b; a++) f.atoms[a].add(d)
        }
        for (let a = 0, b = this.shapes.length; a < b; a++) {
            f = this.shapes[a].getPoints();
            for (let a = 0, b = f.length; a < b; a++) f[a].add(d)
        }
        this.styles.scale =
            1;
        d = a.maxX - a.minX;
        a = a.maxY - a.minY;
        if (d > this.width - 20 || a > this.height - 20) this.styles.scale = .85 * b.min(this.width / d, this.height / a)
    };
    n.bondExists = function(a, b) {
        for (let d = 0, e = this.molecules.length; d < e; d++) {
            let e = this.molecules[d];
            for (let d = 0, f = e.bonds.length; d < f; d++) {
                let c = e.bonds[d];
                if (c.contains(a) && c.contains(b)) return !0
            }
        }
        return !1
    };
    n.getBond = function(a, b) {
        for (let d = 0, e = this.molecules.length; d < e; d++) {
            let e = this.molecules[d];
            for (let d = 0, f = e.bonds.length; d < f; d++) {
                let c = e.bonds[d];
                if (c.contains(a) && c.contains(b)) return c
            }
        }
        return g
    };
    n.getMoleculeByAtom = function(a) {
        for (let b = 0, d = this.molecules.length; b < d; b++) {
            let d = this.molecules[b];
            if (-1 !== d.atoms.indexOf(a)) return d
        }
        return h.undefined
    };
    n.getAllAtoms = function() {
        let a = [];
        for (let b = 0, d = this.molecules.length; b < d; b++) a = a.concat(this.molecules[b].atoms);
        return a
    };
    n.getAllBonds = function() {
        let a = [];
        for (let b = 0, d = this.molecules.length; b < d; b++) a = a.concat(this.molecules[b].bonds);
        return a
    };
    n.getAllPoints = function() {
        let a = [];
        for (let b = 0, d = this.molecules.length; b < d; b++) a = a.concat(this.molecules[b].atoms);
        for (let b = 0, d = this.shapes.length; b < d; b++) a = a.concat(this.shapes[b].getPoints());
        return a
    };
    n.getContentBounds = function() {
        let a = new l.Bounds;
        for (let b = 0, d = this.molecules.length; b < d; b++) a.expand(this.molecules[b].getBounds());
        for (let b = 0, d = this.shapes.length; b < d; b++) a.expand(this.shapes[b].getBounds());
        return a
    };
    n.create = function(n, m, l) {
        this.id = n;
        this.width = m;
        this.height = l;
        this.molecules = [];
        this.shapes = [];
        if (d.getElementById(n)) {
            let a = k("#" + n);
            m ? a.attr("width", m) : this.width = parseInt(a.attr("width"));
            l ? a.attr("height", l) : this.height = parseInt(a.attr("height"));
            a.attr("class", "ChemDoodleWebComponent")
        } else if (f.featureDetection.supports_canvas_text() || -1 == a.indexOf("MSIE")) d.writeln('\x3ccanvas class\x3d"ChemDoodleWebComponent" id\x3d"' + n + '" width\x3d"' + m + '" height\x3d"' + l + '" alt\x3d"ChemDoodle Web Component"\x3eThis browser does not support HTML5/Canvas.\x3c/canvas\x3e');
        else {
            d.writeln('\x3cdiv style\x3d"border: 1px solid black;" width\x3d"' + m + '" height\x3d"' + l + '"\x3ePlease install \x3ca href\x3d"http://code.google.com/chrome/chromeframe/"\x3eGoogle Chrome Frame\x3c/a\x3e, then restart Internet Explorer.\x3c/div\x3e');
            return
        }
        n = k("#" + n);
        n.css("width", this.width);
        n.css("height", this.height);
        this.pixelRatio = h.devicePixelRatio ? h.devicePixelRatio : 1;
        this.styles = new e.Styles;
        let u = this;
        q.supports_touch() ? (n.bind("touchstart", function(a) {
            let b = (new Date).getTime();
            if (!q.supports_gesture() && 2 === a.originalEvent.touches.length) {
                var d = a.originalEvent.touches;
                let b = new e.Point(d[0].pageX, d[0].pageY);
                d = new e.Point(d[1].pageX, d[1].pageY);
                u.implementedGestureDist = b.distance(d);
                u.implementedGestureAngle = b.angle(d);
                u.gesturestart &&
                    (u.prehandleEvent(a), u.gesturestart(a))
            }
            u.lastTouch && 1 === a.originalEvent.touches.length && 500 > b - u.lastTouch ? u.dbltap ? (u.prehandleEvent(a), u.dbltap(a)) : u.dblclick ? (u.prehandleEvent(a), u.dblclick(a)) : u.touchstart ? (u.prehandleEvent(a), u.touchstart(a)) : u.mousedown && (u.prehandleEvent(a), u.mousedown(a)) : u.touchstart ? (u.prehandleEvent(a), u.touchstart(a), this.hold && clearTimeout(this.hold), this.touchhold && (this.hold = setTimeout(function() {
                u.touchhold(a)
            }, 1E3))) : u.mousedown && (u.prehandleEvent(a), u.mousedown(a));
            u.lastTouch = b
        }), n.bind("touchmove", function(a) {
            this.hold && (clearTimeout(this.hold), this.hold = g);
            if (!q.supports_gesture() && 2 === a.originalEvent.touches.length && u.gesturechange) {
                var d = a.originalEvent.touches,
                    f = new e.Point(d[0].pageX, d[0].pageY),
                    c = new e.Point(d[1].pageX, d[1].pageY);
                d = f.distance(c);
                f = f.angle(c);
                a.originalEvent.scale = d / u.implementedGestureDist;
                a.originalEvent.rotation = 180 * (u.implementedGestureAngle - f) / b.PI;
                u.prehandleEvent(a);
                u.gesturechange(a)
            }
            if (1 < a.originalEvent.touches.length && u.multitouchmove) {
                f =
                    a.originalEvent.touches.length;
                u.prehandleEvent(a);
                d = new e.Point(-a.offset.left * f, -a.offset.top * f);
                for (c = 0; c < f; c++) d.x += a.originalEvent.changedTouches[c].pageX, d.y += a.originalEvent.changedTouches[c].pageY;
                d.x /= f;
                d.y /= f;
                a.p = d;
                u.multitouchmove(a, f)
            } else u.touchmove ? (u.prehandleEvent(a), u.touchmove(a)) : u.drag && (u.prehandleEvent(a), u.drag(a))
        }), n.bind("touchend", function(a) {
            this.hold && (clearTimeout(this.hold), this.hold = g);
            !q.supports_gesture() && u.implementedGestureDist && (u.implementedGestureDist = g, u.implementedGestureAngle =
                g, u.gestureend && (u.prehandleEvent(a), u.gestureend(a)));
            u.touchend ? (u.prehandleEvent(a), u.touchend(a)) : u.mouseup && (u.prehandleEvent(a), u.mouseup(a));
            250 > (new Date).getTime() - u.lastTouch && (u.tap ? (u.prehandleEvent(a), u.tap(a)) : u.click && (u.prehandleEvent(a), u.click(a)))
        }), n.bind("gesturestart", function(a) {
            u.gesturestart && (u.prehandleEvent(a), u.gesturestart(a))
        }), n.bind("gesturechange", function(a) {
            u.gesturechange && (u.prehandleEvent(a), u.gesturechange(a))
        }), n.bind("gestureend", function(a) {
            u.gestureend &&
                (u.prehandleEvent(a), u.gestureend(a))
        })) : (n.click(function(a) {
            switch (a.which) {
                case 1:
                    u.click && (u.prehandleEvent(a), u.click(a));
                    break;
                case 2:
                    u.middleclick && (u.prehandleEvent(a), u.middleclick(a));
                    break;
                case 3:
                    u.rightclick && (u.prehandleEvent(a), u.rightclick(a))
            }
        }), n.dblclick(function(a) {
            u.dblclick && (u.prehandleEvent(a), u.dblclick(a))
        }), n.mousedown(function(a) {
            switch (a.which) {
                case 1:
                    t.CANVAS_DRAGGING = u;
                    u.mousedown && (u.prehandleEvent(a), u.mousedown(a));
                    break;
                case 2:
                    u.middlemousedown && (u.prehandleEvent(a),
                        u.middlemousedown(a));
                    break;
                case 3:
                    u.rightmousedown && (u.prehandleEvent(a), u.rightmousedown(a))
            }
        }), n.mousemove(function(a) {
            !t.CANVAS_DRAGGING && u.mousemove && (u.prehandleEvent(a), u.mousemove(a))
        }), n.mouseout(function(a) {
            t.CANVAS_OVER = g;
            u.mouseout && (u.prehandleEvent(a), u.mouseout(a))
        }), n.mouseover(function(a) {
            t.CANVAS_OVER = u;
            u.mouseover && (u.prehandleEvent(a), u.mouseover(a))
        }), n.mouseup(function(a) {
            switch (a.which) {
                case 1:
                    u.mouseup && (u.prehandleEvent(a), u.mouseup(a));
                    break;
                case 2:
                    u.middlemouseup && (u.prehandleEvent(a),
                        u.middlemouseup(a));
                    break;
                case 3:
                    u.rightmouseup && (u.prehandleEvent(a), u.rightmouseup(a))
            }
        }), n.mousewheel(function(a, b) {
            u.mousewheel && (u.prehandleEvent(a), u.mousewheel(a, b))
        }));
        this.subCreate && this.subCreate()
    };
    n.prehandleEvent = function(a) {
        a.originalEvent.changedTouches && (a.pageX = a.originalEvent.changedTouches[0].pageX, a.pageY = a.originalEvent.changedTouches[0].pageY);
        this.doEventDefault || (a.preventDefault(), a.returnValue = !1);
        a.offset = k("#" + this.id).offset();
        a.p = new e.Point(a.pageX - a.offset.left, a.pageY -
            a.offset.top)
    }
})(ChemDoodle, ChemDoodle.featureDetection, ChemDoodle.math, ChemDoodle.monitor, ChemDoodle.structures, ChemDoodle.lib.jQuery, Math, document, window, navigator.userAgent);
(function(f, q, l) {
    f._AnimatorCanvas = function(f, e, k) {
        f && this.create(f, e, k)
    };
    f = f._AnimatorCanvas.prototype = new f._Canvas;
    f.timeout = 33;
    f.startAnimation = function() {
        this.stopAnimation();
        this.lastTime = (new Date).getTime();
        let f = this;
        this.nextFrame && (this.handle = q.requestInterval(function() {
            let e = (new Date).getTime();
            f.nextFrame(e - f.lastTime);
            f.repaint();
            f.lastTime = e
        }, this.timeout))
    };
    f.stopAnimation = function() {
        this.handle && (q.clearRequestInterval(this.handle), this.handle = l)
    };
    f.isRunning = function() {
        return this.handle !==
            l
    }
})(ChemDoodle, ChemDoodle.animations);
(function(f, q, l) {
    f.FileCanvas = function(f, e, k, b) {
        f && this.create(f, e, k);
        q.writeln('\x3cbr\x3e\x3cform name\x3d"FileForm" enctype\x3d"multipart/form-data" method\x3d"POST" action\x3d"' + b + '" target\x3d"HiddenFileFrame"\x3e\x3cinput type\x3d"file" name\x3d"f" /\x3e\x3cinput type\x3d"submit" name\x3d"submitbutton" value\x3d"Show File" /\x3e\x3c/form\x3e\x3ciframe id\x3d"HFF-' + f + '" name\x3d"HiddenFileFrame" height\x3d"0" width\x3d"0" style\x3d"display:none;" onLoad\x3d"GetMolFromFrame(\'HFF-' + f + "', " + f +
            ')"\x3e\x3c/iframe\x3e');
        this.emptyMessage = "Click below to load file";
        this.repaint()
    };
    f.FileCanvas.prototype = new f._Canvas
})(ChemDoodle, document);
(function(f, q) {
    f.HyperlinkCanvas = function(f, q, e, k, b, d) {
        f && this.create(f, q, e);
        this.urlOrFunction = k;
        this.color = b ? b : "blue";
        this.size = d ? d : 2
    };
    f = f.HyperlinkCanvas.prototype = new f._Canvas;
    f.openInNewWindow = !0;
    f.hoverImage = q;
    f.drawChildExtras = function(f) {
        this.e && (this.hoverImage ? f.drawImage(this.hoverImage, 0, 0) : (f.strokeStyle = this.color, f.lineWidth = 2 * this.size, f.strokeRect(0, 0, this.width, this.height)))
    };
    f.setHoverImage = function(f) {
        this.hoverImage = new Image;
        this.hoverImage.src = f
    };
    f.click = function(f) {
        this.e =
            q;
        this.repaint();
        this.urlOrFunction instanceof Function ? this.urlOrFunction() : this.openInNewWindow ? window.open(this.urlOrFunction) : location.href = this.urlOrFunction
    };
    f.mouseout = function(f) {
        this.e = q;
        this.repaint()
    };
    f.mouseover = function(f) {
        this.e = f;
        this.repaint()
    }
})(ChemDoodle);
(function(f, q, l, t, e) {
    f.MolGrabberCanvas = function(e, b, d) {
        e && this.create(e, b, d);
        b = [];
        b.push('\x3cbr\x3e\x3cinput type\x3d"text" id\x3d"');
        b.push(e);
        b.push('_query" size\x3d"32" value\x3d"" /\x3e');
        b.push(this.getInputFields());
        t.getElementById(e);
        l("#" + e).after(b.join(""));
        let f = this;
        l("#" + e + "_submit").click(function() {
            f.search()
        });
        l("#" + e + "_query").keypress(function(a) {
            13 === a.which && f.search()
        });
        this.emptyMessage = "Enter search term below";
        this.repaint()
    };
    f = f.MolGrabberCanvas.prototype = new f._Canvas;
    f.setSearchTerm = function(e) {
        l("#" + this.id + "_query").val(e);
        this.search()
    };
    f.getInputFields = function() {
        let e = [];
        e.push("\x3cbr\x3e\x3cnobr\x3e");
        e.push('\x3cselect id\x3d"');
        e.push(this.id);
        e.push('_select"\x3e');
        e.push('\x3coption value\x3d"chemexper"\x3eChemExper');
        e.push('\x3coption value\x3d"chemspider"\x3eChemSpider');
        e.push('\x3coption value\x3d"pubchem" selected\x3ePubChem');
        e.push("\x3c/select\x3e");
        e.push('\x3cbutton type\x3d"button" id\x3d"');
        e.push(this.id);
        e.push('_submit"\x3eShow Molecule\x3c/button\x3e');
        e.push("\x3c/nobr\x3e");
        return e.join("")
    };
    f.search = function() {
        this.emptyMessage = "Searching...";
        this.clear();
        let e = this;
        q.getMoleculeFromDatabase(l("#" + this.id + "_query").val(), {
            database: l("#" + this.id + "_select").val()
        }, function(b) {
            e.loadMolecule(b)
        })
    }
})(ChemDoodle, ChemDoodle.iChemLabs, ChemDoodle.lib.jQuery, document);
(function(f, q, l, t) {
    let e = [],
        k = [1, 0, 0],
        b = [0, 1, 0],
        d = [0, 0, 1];
    f.RotatorCanvas = function(b, a, d, e) {
        b && this.create(b, a, d);
        this.rotate3D = e
    };
    f = f.RotatorCanvas.prototype = new f._AnimatorCanvas;
    q = q.PI / 15;
    f.xIncrement = q;
    f.yIncrement = q;
    f.zIncrement = q;
    f.nextFrame = function(f) {
        if (0 === this.molecules.length && 0 === this.shapes.length) this.stopAnimation();
        else if (f /= 1E3, this.rotate3D) {
            l.identity(e);
            l.rotate(e, this.xIncrement * f, k);
            l.rotate(e, this.yIncrement * f, b);
            l.rotate(e, this.zIncrement * f, d);
            for (let b = 0, d = this.molecules.length; b <
                d; b++) {
                f = this.molecules[b];
                for (let b = 0, d = f.atoms.length; b < d; b++) {
                    var a = f.atoms[b],
                        g = [a.x - this.width / 2, a.y - this.height / 2, a.z];
                    l.multiplyVec3(e, g);
                    a.x = g[0] + this.width / 2;
                    a.y = g[1] + this.height / 2;
                    a.z = g[2]
                }
                for (let a = 0, b = f.rings.length; a < b; a++) f.rings[a].center = f.rings[a].getCenter();
                this.styles.atoms_display && this.styles.atoms_circles_2D && f.sortAtomsByZ();
                this.styles.bonds_display && this.styles.bonds_clearOverlaps_2D && f.sortBondsByZ()
            }
            for (let b = 0, d = this.shapes.length; b < d; b++) {
                f = this.shapes[b].getPoints();
                for (let b = 0, d = f.length; b < d; b++) a = f[b], g = [a.x - this.width / 2, a.y - this.height / 2, 0], l.multiplyVec3(e, g), a.x = g[0] + this.width / 2, a.y = g[1] + this.height / 2
            }
        } else this.styles.rotateAngle += this.zIncrement * f
    };
    f.dblclick = function(b) {
        this.isRunning() ? this.stopAnimation() : this.startAnimation()
    }
})(ChemDoodle, Math, ChemDoodle.lib.mat4);
(function(f, q, l, t) {
    f.SlideshowCanvas = function(e, f, b) {
        e && this.create(e, f, b)
    };
    f = f.SlideshowCanvas.prototype = new f._AnimatorCanvas;
    f.frames = [];
    f.curIndex = 0;
    f.timeout = 5E3;
    f.alpha = 0;
    f.innerHandle = t;
    f.phase = 0;
    f.drawChildExtras = function(e) {
        let f = l.getRGB(this.styles.backgroundColor, 255);
        e.fillStyle = "rgba(" + f[0] + ", " + f[1] + ", " + f[2] + ", " + this.alpha + ")";
        e.fillRect(0, 0, this.width, this.height)
    };
    f.nextFrame = function(e) {
        if (0 === this.frames.length) this.stopAnimation();
        else {
            this.phase = 0;
            var f = this,
                b = 1;
            this.innerHandle =
                setInterval(function() {
                    f.alpha = b / 15;
                    f.repaint();
                    15 === b && f.breakInnerHandle();
                    b++
                }, 33)
        }
    };
    f.breakInnerHandle = function() {
        this.innerHandle && (clearInterval(this.innerHandle), this.innerHandle = t);
        if (0 === this.phase) {
            this.curIndex++;
            this.curIndex > this.frames.length - 1 && (this.curIndex = 0);
            this.alpha = 1;
            let e = this.frames[this.curIndex];
            this.loadContent(e.mols, e.shapes);
            this.phase = 1;
            let f = this,
                b = 1;
            this.innerHandle = setInterval(function() {
                f.alpha = (15 - b) / 15;
                f.repaint();
                15 === b && f.breakInnerHandle();
                b++
            }, 33)
        } else 1 ===
            this.phase && (this.alpha = 0, this.repaint())
    };
    f.addFrame = function(e, f) {
        0 === this.frames.length && this.loadContent(e, f);
        this.frames.push({
            mols: e,
            shapes: f
        })
    }
})(ChemDoodle, ChemDoodle.animations, ChemDoodle.math);
(function(f, q, l, t, e, k) {
    f.TransformCanvas = function(b, d, e, a) {
        b && this.create(b, d, e);
        this.rotate3D = a
    };
    f = f.TransformCanvas.prototype = new f._Canvas;
    f.lastPoint = k;
    f.rotationMultMod = 1.3;
    f.lastPinchScale = 1;
    f.lastGestureRotate = 0;
    f.mousedown = function(b) {
        this.lastPoint = b.p
    };
    f.dblclick = function(b) {
        this.center();
        this.repaint()
    };
    f.drag = function(b) {
        if (!this.lastPoint.multi) {
            if (q.ALT) {
                var d = new l.Point(b.p.x, b.p.y);
                d.sub(this.lastPoint);
                for (let a = 0, b = this.molecules.length; a < b; a++) {
                    var f = this.molecules[a];
                    for (let a =
                            0, b = f.atoms.length; a < b; a++) f.atoms[a].add(d);
                    f.check()
                }
                for (let a = 0, b = this.shapes.length; a < b; a++) {
                    f = this.shapes[a].getPoints();
                    for (let a = 0, b = f.length; a < b; a++) f[a].add(d)
                }
                this.lastPoint = b.p
            } else if (!0 === this.rotate3D) {
                d = t.max(this.width / 4, this.height / 4);
                f = (b.p.x - this.lastPoint.x) / d * this.rotationMultMod;
                var a = -(b.p.y - this.lastPoint.y) / d * this.rotationMultMod;
                d = [];
                e.identity(d);
                e.rotate(d, a, [1, 0, 0]);
                e.rotate(d, f, [0, 1, 0]);
                for (let g = 0, h = this.molecules.length; g < h; g++) {
                    f = this.molecules[g];
                    for (let b = 0, g = f.atoms.length; b <
                        g; b++) {
                        a = f.atoms[b];
                        let g = [a.x - this.width / 2, a.y - this.height / 2, a.z];
                        e.multiplyVec3(d, g);
                        a.x = g[0] + this.width / 2;
                        a.y = g[1] + this.height / 2;
                        a.z = g[2]
                    }
                    for (let a = 0, b = f.rings.length; a < b; a++) f.rings[a].center = f.rings[a].getCenter();
                    this.lastPoint = b.p;
                    this.styles.atoms_display && this.styles.atoms_circles_2D && f.sortAtomsByZ();
                    this.styles.bonds_display && this.styles.bonds_clearOverlaps_2D && f.sortBondsByZ()
                }
            } else f = new l.Point(this.width / 2, this.height / 2), d = f.angle(this.lastPoint), f = f.angle(b.p), this.styles.rotateAngle -=
                f - d, this.lastPoint = b.p;
            this.repaint()
        }
    };
    f.mousewheel = function(b, d) {
        this.styles.scale += d / 50;
        .01 > this.styles.scale && (this.styles.scale = .01);
        this.repaint()
    };
    f.multitouchmove = function(b, d) {
        if (2 === d)
            if (this.lastPoint.multi) {
                d = new l.Point(b.p.x, b.p.y);
                d.sub(this.lastPoint);
                for (let a = 0, b = this.molecules.length; a < b; a++) {
                    var e = this.molecules[a];
                    for (let a = 0, b = e.atoms.length; a < b; a++) e.atoms[a].add(d);
                    e.check()
                }
                for (let a = 0, b = this.shapes.length; a < b; a++) {
                    e = this.shapes[a].getPoints();
                    for (let a = 0, b = e.length; a < b; a++) e[a].add(d)
                }
                this.lastPoint =
                    b.p;
                this.lastPoint.multi = !0;
                this.repaint()
            } else this.lastPoint = b.p, this.lastPoint.multi = !0
    };
    f.gesturechange = function(b) {
        0 !== b.originalEvent.scale - this.lastPinchScale && (this.styles.scale *= b.originalEvent.scale / this.lastPinchScale, .01 > this.styles.scale && (this.styles.scale = .01), this.lastPinchScale = b.originalEvent.scale);
        if (0 !== this.lastGestureRotate - b.originalEvent.rotation) {
            let d = (this.lastGestureRotate - b.originalEvent.rotation) / 180 * t.PI,
                e = new l.Point(this.width / 2, this.height / 2);
            for (let a = 0, b = this.molecules.length; a <
                b; a++) {
                let b = this.molecules[a];
                for (let a = 0, f = b.atoms.length; a < f; a++) {
                    let f = b.atoms[a],
                        g = e.distance(f),
                        h = e.angle(f) + d;
                    f.x = e.x + g * t.cos(h);
                    f.y = e.y - g * t.sin(h)
                }
                b.check()
            }
            this.lastGestureRotate = b.originalEvent.rotation
        }
        this.repaint()
    };
    f.gestureend = function(b) {
        this.lastPinchScale = 1;
        this.lastGestureRotate = 0
    }
})(ChemDoodle, ChemDoodle.monitor, ChemDoodle.structures, Math, ChemDoodle.lib.mat4);
(function(f, q) {
    f.ViewerCanvas = function(f, q, e) {
        f && this.create(f, q, e)
    };
    f.ViewerCanvas.prototype = new f._Canvas
})(ChemDoodle);
(function(f, q, l) {
    f._SpectrumCanvas = function(f, e, k) {
        f && this.create(f, e, k)
    };
    f = f._SpectrumCanvas.prototype = new f._Canvas;
    f.spectrum = l;
    f.emptyMessage = "No Spectrum Loaded or Recognized";
    f.loadMolecule = l;
    f.getMolecule = l;
    f.innerRepaint = function(f) {
        this.spectrum && 0 < this.spectrum.data.length ? this.spectrum.draw(f, this.styles, this.width, this.height) : this.emptyMessage && (f.fillStyle = "#737683", f.textAlign = "center", f.textBaseline = "middle", f.font = "18px Helvetica, Verdana, Arial, Sans-serif", f.fillText(this.emptyMessage,
            this.width / 2, this.height / 2))
    };
    f.loadSpectrum = function(f) {
        this.spectrum = f;
        this.repaint()
    };
    f.getSpectrum = function() {
        return this.spectrum
    };
    f.getSpectrumCoordinates = function(f, e) {
        return spectrum.getInternalCoordinates(f, e, this.width, this.height)
    }
})(ChemDoodle, document);
(function(f, q) {
    f.ObserverCanvas = function(f, q, e) {
        f && this.create(f, q, e)
    };
    f.ObserverCanvas.prototype = new f._SpectrumCanvas
})(ChemDoodle);
(function(f, q) {
    f.OverlayCanvas = function(f, q, e) {
        f && this.create(f, q, e)
    };
    f = f.OverlayCanvas.prototype = new f._SpectrumCanvas;
    f.overlaySpectra = [];
    f.superRepaint = f.innerRepaint;
    f.innerRepaint = function(f) {
        this.superRepaint(f);
        if (this.spectrum && 0 < this.spectrum.data.length)
            for (let l = 0, e = this.overlaySpectra.length; l < e; l++) {
                let e = this.overlaySpectra[l];
                e && 0 < e.data.length && (e.minX = this.spectrum.minX, e.maxX = this.spectrum.maxX, e.drawPlot(f, this.styles, this.width, this.height, this.spectrum.memory.offsetTop, this.spectrum.memory.offsetLeft,
                    this.spectrum.memory.offsetBottom))
            }
    };
    f.addSpectrum = function(f) {
        this.spectrum ? this.overlaySpectra.push(f) : this.spectrum = f
    }
})(ChemDoodle);
(function(f, q, l, t) {
    f.PerspectiveCanvas = function(e, b, d) {
        e && this.create(e, b, d)
    };
    let e = f.PerspectiveCanvas.prototype = new f._SpectrumCanvas;
    e.dragRange = t;
    e.rescaleYAxisOnZoom = !0;
    e.lastPinchScale = 1;
    e.mousedown = function(e) {
        this.dragRange = new f.structures.Point(e.p.x, e.p.x)
    };
    e.mouseup = function(e) {
        this.dragRange && this.dragRange.x !== this.dragRange.y && (this.dragRange.multi || (e = this.spectrum.zoom(this.dragRange.x, e.p.x, this.width, this.rescaleYAxisOnZoom), this.rescaleYAxisOnZoom && (this.styles.scale = e)), this.dragRange =
            t, this.repaint())
    };
    e.drag = function(e) {
        this.dragRange && (this.dragRange.multi ? this.dragRange = t : (q.SHIFT && (this.spectrum.translate(e.p.x - this.dragRange.x, this.width), this.dragRange.x = e.p.x), this.dragRange.y = e.p.x), this.repaint())
    };
    e.drawChildExtras = function(e) {
        if (this.dragRange) {
            var b = l.min(this.dragRange.x, this.dragRange.y);
            let d = l.max(this.dragRange.x, this.dragRange.y);
            e.strokeStyle = "gray";
            e.lineStyle = 1;
            e.beginPath();
            for (e.moveTo(b, this.height / 2); b <= d; b++) 5 > b % 10 ? e.lineTo(b, l.round(this.height / 2)) :
                e.moveTo(b, l.round(this.height / 2));
            e.stroke()
        }
    };
    e.mousewheel = function(e, b) {
        this.styles.scale -= b / 10;
        .01 > this.styles.scale && (this.styles.scale = .01);
        this.repaint()
    };
    e.dblclick = function(e) {
        this.spectrum.setup();
        this.styles.scale = 1;
        this.repaint()
    };
    e.multitouchmove = function(e, b) {
        2 === b && (this.dragRange && this.dragRange.multi ? (this.spectrum.translate(e.p.x - this.dragRange.x, this.width), this.dragRange.x = e.p.x, this.dragRange.y = e.p.x, this.repaint()) : (this.dragRange = new f.structures.Point(e.p.x, e.p.x), this.dragRange.multi = !0))
    };
    e.gesturechange = function(e) {
        this.styles.scale *= e.originalEvent.scale / this.lastPinchScale;
        .01 > this.styles.scale && (this.styles.scale = .01);
        this.lastPinchScale = e.originalEvent.scale;
        this.repaint()
    };
    e.gestureend = function(e) {
        this.lastPinchScale = 1
    }
})(ChemDoodle, ChemDoodle.monitor, Math);
(function(f, q, l, t) {
    f.SeekerCanvas = function(e, b, d, f) {
        e && this.create(e, b, d);
        this.seekType = f
    };
    let e = f.SeekerCanvas.prototype = new f._SpectrumCanvas;
    e.superRepaint = e.innerRepaint;
    e.innerRepaint = function(e) {
        this.superRepaint(e);
        if (this.spectrum && 0 < this.spectrum.data.length && this.p) {
            if (this.seekType === f.SeekerCanvas.SEEK_POINTER) {
                var b = this.p;
                var d = this.spectrum.getInternalCoordinates(b.x, b.y)
            } else if (this.seekType === f.SeekerCanvas.SEEK_PLOT || this.seekType === f.SeekerCanvas.SEEK_PEAK) {
                d = this.seekType === f.SeekerCanvas.SEEK_PLOT ?
                    this.spectrum.getClosestPlotInternalCoordinates(this.p.x) : this.spectrum.getClosestPeakInternalCoordinates(this.p.x);
                if (!d) return;
                b = {
                    x: this.spectrum.getTransformedX(d.x, this.styles, this.width, this.spectrum.memory.offsetLeft),
                    y: this.spectrum.getTransformedY(d.y / 100, this.styles, this.height, this.spectrum.memory.offsetBottom, this.spectrum.memory.offsetTop)
                }
            }
            e.fillStyle = "white";
            e.strokeStyle = this.styles.plots_color;
            e.lineWidth = this.styles.plots_width;
            e.beginPath();
            e.arc(b.x, b.y, 3, 0, 2 * l.PI, !1);
            e.fill();
            e.stroke();
            e.font = q.getFontString(this.styles.text_font_size, this.styles.text_font_families);
            e.textAlign = "left";
            e.textBaseline = "bottom";
            d = "x:" + d.x.toFixed(3) + ", y:" + d.y.toFixed(3);
            let h = b.x + 3,
                a = e.measureText(d).width;
            h + a > this.width - 2 && (h -= 6 + a);
            b = b.y;
            0 > b - this.styles.text_font_size - 2 && (b += this.styles.text_font_size);
            e.fillRect(h, b - this.styles.text_font_size, a, this.styles.text_font_size);
            e.fillStyle = "black";
            e.fillText(d, h, b)
        }
    };
    e.mouseout = function(e) {
        this.p = t;
        this.repaint()
    };
    e.mousemove = function(e) {
        this.p = {
            x: e.p.x - 2,
            y: e.p.y - 3
        };
        this.repaint()
    };
    e.touchstart = function(e) {
        this.mousemove(e)
    };
    e.touchmove = function(e) {
        this.mousemove(e)
    };
    e.touchend = function(e) {
        this.mouseout(e)
    };
    f.SeekerCanvas.SEEK_POINTER = "pointer";
    f.SeekerCanvas.SEEK_PLOT = "plot";
    f.SeekerCanvas.SEEK_PEAK = "peak"
})(ChemDoodle, ChemDoodle.extensions, Math);
(function(f, q, l, t, e, k, b, d, h, a, g, n, v, m) {
    f._Canvas3D = function(a, b, d) {
        a && this.create(a, b, d)
    };
    a = f._Canvas3D.prototype = new f._Canvas;
    let x = f._Canvas.prototype;
    a.rotationMatrix = m;
    a.contentCenter = m;
    a.lastPoint = m;
    a.emptyMessage = "WebGL is Unavailable!";
    a.lastPinchScale = 1;
    a.lastGestureRotate = 0;
    a.afterLoadContent = function() {
        var a = new l.Bounds;
        for (let b = 0, c = this.molecules.length; b < c; b++) a.expand(this.molecules[b].getBounds3D());
        var d = g.dist([a.maxX, a.maxY, a.maxZ], [a.minX, a.minY, a.minZ]) / 2 + 1.5;
        Infinity === d && (d =
            10);
        this.maxDimension = b.max(a.maxX - a.minX, a.maxY - a.minY);
        a = b.min(179.9, b.max(this.styles.projectionPerspectiveVerticalFieldOfView_3D, .1));
        var e = a / 360 * b.PI,
            f = b.tan(e) / .8;
        f = d / f;
        let c = this.width / this.height;
        this.camera.fieldOfView = a;
        this.camera.near = f - d;
        this.camera.far = f + d;
        this.camera.aspect = c;
        h.translate(h.identity(this.camera.viewMatrix), [0, 0, -f]);
        e = d / b.tan(e);
        this.lighting.camera.fieldOfView = a;
        this.lighting.camera.near = e - d;
        this.lighting.camera.far = e + d;
        this.lighting.updateView();
        this.setupScene()
    };
    a.renderDepthMap = function() {
        if (this.styles.shadow_3D && e.DepthShader) {
            let a = this.gl.isEnabled(this.gl.CULL_FACE);
            a || this.gl.enable(this.gl.CULL_FACE);
            this.depthShader.useShaderProgram(this.gl);
            let b = this.gl.getParameter(this.gl.COLOR_CLEAR_VALUE);
            this.gl.clearColor(1, 1, 1, 0);
            this.lightDepthMapFramebuffer.bind(this.gl, this.shadowTextureSize, this.shadowTextureSize);
            this.gl.clear(this.gl.COLOR_BUFFER_BIT | this.gl.DEPTH_BUFFER_BIT);
            this.depthShader.setProjectionMatrix(this.gl, this.lighting.camera.projectionMatrix);
            this.depthShader.enableAttribsArray(this.gl);
            for (let a = 0, b = this.molecules.length; a < b; a++) this.molecules[a].render(this.gl, this.styles);
            this.gl.flush();
            this.depthShader.disableAttribsArray(this.gl);
            this.gl.bindFramebuffer(this.gl.FRAMEBUFFER, null);
            this.gl.clearColor(b[0], b[1], b[2], b[3]);
            a || this.gl.disable(this.gl.CULL_FACE)
        }
    };
    a.renderExtras = function() {
        this.phongShader.useShaderProgram(this.gl);
        this.phongShader.enableAttribsArray(this.gl);
        var a = [];
        for (let b = 0, d = this.shapes.length; b < d; b++) {
            let d = this.shapes[b];
            d instanceof e._Surface && (!d.styles && 1 !== this.styles.surfaces_alpha || d.styles && 1 !== d.styles.surfaces_alpha) ? a.push(d) : d.render(this.gl, this.styles)
        }
        if (0 !== a.length) {
            this.gl.blendFunc(this.gl.SRC_ALPHA, this.gl.ONE_MINUS_SRC_ALPHA);
            this.gl.enable(this.gl.BLEND);
            this.gl.depthMask(!1);
            for (let b = 0, d = a.length; b < d; b++) a[b].render(this.gl, this.styles);
            this.gl.depthMask(!0);
            this.gl.disable(this.gl.BLEND);
            this.gl.blendFuncSeparate(this.gl.SRC_ALPHA, this.gl.ONE_MINUS_SRC_ALPHA, this.gl.ONE, this.gl.ONE_MINUS_SRC_ALPHA)
        }
        this.phongShader.setShadow(this.gl,
            !1);
        this.phongShader.setFogMode(this.gl, 0);
        this.phongShader.setFlatColor(this.gl, !1);
        this.styles.compass_display && (this.phongShader.setLightDirection(this.gl, [0, 0, -1]), this.compass.render(this.gl, this.styles));
        this.phongShader.disableAttribsArray(this.gl);
        this.gl.flush();
        this.gl.enable(this.gl.BLEND);
        this.gl.depthMask(!1);
        this.labelShader.useShaderProgram(this.gl);
        this.labelShader.setMatrixUniforms(this.gl, this.gl.modelViewMatrix);
        this.labelShader.setProjectionMatrix(this.gl, this.camera.projectionMatrix);
        this.labelShader.setDimension(this.gl, this.gl.canvas.clientWidth, this.gl.canvas.clientHeight);
        this.labelShader.enableAttribsArray(this.gl);
        this.styles.atoms_displayLabels_3D && this.label3D.render(this.gl, this.styles, this.getMolecules());
        if (this.styles.measurement_displayText_3D)
            for (let b = 0, d = this.shapes.length; b < d; b++) a = this.shapes[b], a.renderText && a.renderText(this.gl, this.styles);
        this.styles.compass_display && this.styles.compass_displayText_3D && this.compass.renderAxis(this.gl);
        this.labelShader.disableAttribsArray(this.gl);
        this.gl.disable(this.gl.BLEND);
        this.gl.depthMask(!0);
        this.gl.flush();
        this.drawChildExtras && this.drawChildExtras(this.gl);
        this.gl.flush()
    };
    a.renderColor = function() {
        this.phongShader.useShaderProgram(this.gl);
        this.gl.uniform1i(this.phongShader.shadowDepthSampleUniform, 0);
        this.gl.activeTexture(this.gl.TEXTURE0);
        this.gl.bindTexture(this.gl.TEXTURE_2D, this.lightDepthMapTexture.texture);
        this.phongShader.setProjectionMatrix(this.gl, this.camera.projectionMatrix);
        this.phongShader.setShadow(this.gl, this.styles.shadow_3D);
        this.phongShader.setFlatColor(this.gl, this.styles.flat_color_3D);
        this.phongShader.setGammaCorrection(this.gl, this.styles.gammaCorrection_3D);
        this.phongShader.setShadowTextureSize(this.gl, this.shadowTextureSize, this.shadowTextureSize);
        this.phongShader.setShadowIntensity(this.gl, this.styles.shadow_intensity_3D);
        this.phongShader.setFogMode(this.gl, this.styles.fog_mode_3D);
        this.phongShader.setFogColor(this.gl, this.fogging.colorRGB);
        this.phongShader.setFogStart(this.gl, this.fogging.fogStart);
        this.phongShader.setFogEnd(this.gl,
            this.fogging.fogEnd);
        this.phongShader.setFogDensity(this.gl, this.fogging.density);
        this.phongShader.setLightProjectionMatrix(this.gl, this.lighting.camera.projectionMatrix);
        this.phongShader.setLightDiffuseColor(this.gl, this.lighting.diffuseRGB);
        this.phongShader.setLightSpecularColor(this.gl, this.lighting.specularRGB);
        this.phongShader.setLightDirection(this.gl, this.lighting.direction);
        this.phongShader.enableAttribsArray(this.gl);
        for (let a = 0, b = this.molecules.length; a < b; a++) this.molecules[a].render(this.gl,
            this.styles);
        this.phongShader.disableAttribsArray(this.gl);
        this.gl.flush()
    };
    a.renderPosition = function() {
        this.positionShader.useShaderProgram(this.gl);
        this.positionShader.setProjectionMatrix(this.gl, this.camera.projectionMatrix);
        this.positionShader.enableAttribsArray(this.gl);
        for (let a = 0, b = this.molecules.length; a < b; a++) this.molecules[a].render(this.gl, this.styles);
        this.positionShader.disableAttribsArray(this.gl);
        this.gl.flush()
    };
    a.renderNormal = function() {
        this.normalShader.useShaderProgram(this.gl);
        this.normalShader.setProjectionMatrix(this.gl, this.camera.projectionMatrix);
        this.normalShader.enableAttribsArray(this.gl);
        for (let a = 0, b = this.molecules.length; a < b; a++) this.molecules[a].render(this.gl, this.styles);
        this.normalShader.disableAttribsArray(this.gl);
        this.gl.flush()
    };
    a.renderSSAO = function() {
        this.ssaoShader.useShaderProgram(this.gl);
        this.ssaoShader.setProjectionMatrix(this.gl, this.camera.projectionMatrix);
        this.ssaoShader.setSampleKernel(this.gl, this.ssao.sampleKernel);
        this.ssaoShader.setKernelRadius(this.gl,
            this.styles.ssao_kernel_radius);
        this.ssaoShader.setPower(this.gl, this.styles.ssao_power);
        this.ssaoShader.setGbufferTextureSize(this.gl, this.gl.drawingBufferWidth, this.gl.drawingBufferHeight);
        this.gl.uniform1i(this.ssaoShader.positionSampleUniform, 0);
        this.gl.uniform1i(this.ssaoShader.normalSampleUniform, 1);
        this.gl.uniform1i(this.ssaoShader.noiseSampleUniform, 2);
        this.gl.activeTexture(this.gl.TEXTURE0);
        this.gl.bindTexture(this.gl.TEXTURE_2D, this.positionTexture.texture);
        this.gl.activeTexture(this.gl.TEXTURE1);
        this.gl.bindTexture(this.gl.TEXTURE_2D, this.normalTexture.texture);
        this.gl.activeTexture(this.gl.TEXTURE2);
        this.gl.bindTexture(this.gl.TEXTURE_2D, this.ssao.noiseTexture);
        this.gl.activeTexture(this.gl.TEXTURE0);
        this.ssaoShader.enableAttribsArray(this.gl);
        this.gl.quadBuffer.bindBuffers(this.gl);
        this.gl.drawArrays(this.gl.TRIANGLE_STRIP, 0, this.gl.quadBuffer.vertexPositionBuffer.numItems);
        this.ssaoShader.disableAttribsArray(this.gl);
        this.gl.flush();
        this.ssaoFramebuffer.bind(this.gl, this.gl.drawingBufferWidth,
            this.gl.drawingBufferHeight);
        this.gl.clear(this.gl.COLOR_BUFFER_BIT);
        this.ssaoBlurShader.useShaderProgram(this.gl);
        this.ssaoBlurShader.setGbufferTextureSize(this.gl, this.gl.drawingBufferWidth, this.gl.drawingBufferHeight);
        this.gl.uniform1i(this.ssaoBlurShader.aoSampleUniform, 0);
        this.gl.uniform1i(this.ssaoBlurShader.depthSampleUniform, 1);
        this.gl.activeTexture(this.gl.TEXTURE0);
        this.gl.bindTexture(this.gl.TEXTURE_2D, this.imageTexture.texture);
        this.gl.activeTexture(this.gl.TEXTURE1);
        this.gl.bindTexture(this.gl.TEXTURE_2D,
            this.depthTexture.texture);
        this.gl.activeTexture(this.gl.TEXTURE0);
        this.ssaoBlurShader.enableAttribsArray(this.gl);
        this.gl.quadBuffer.bindBuffers(this.gl);
        this.gl.drawArrays(this.gl.TRIANGLE_STRIP, 0, this.gl.quadBuffer.vertexPositionBuffer.numItems);
        this.ssaoBlurShader.disableAttribsArray(this.gl);
        this.gl.activeTexture(this.gl.TEXTURE0);
        this.gl.flush()
    };
    a.renderOutline = function() {
        this.outlineShader.useShaderProgram(this.gl);
        this.outlineShader.setGbufferTextureSize(this.gl, this.gl.drawingBufferWidth,
            this.gl.drawingBufferHeight);
        this.outlineShader.setNormalThreshold(this.gl, this.styles.outline_normal_threshold);
        this.outlineShader.setDepthThreshold(this.gl, this.styles.outline_depth_threshold);
        this.outlineShader.setThickness(this.gl, this.styles.outline_thickness);
        this.gl.uniform1i(this.outlineShader.normalSampleUniform, 0);
        this.gl.uniform1i(this.outlineShader.depthSampleUniform, 1);
        this.gl.activeTexture(this.gl.TEXTURE0);
        this.gl.bindTexture(this.gl.TEXTURE_2D, this.normalTexture.texture);
        this.gl.activeTexture(this.gl.TEXTURE1);
        this.gl.bindTexture(this.gl.TEXTURE_2D, this.depthTexture.texture);
        this.gl.activeTexture(this.gl.TEXTURE0);
        this.outlineShader.enableAttribsArray(this.gl);
        this.gl.quadBuffer.bindBuffers(this.gl);
        this.gl.drawArrays(this.gl.TRIANGLE_STRIP, 0, this.gl.quadBuffer.vertexPositionBuffer.numItems);
        this.outlineShader.disableAttribsArray(this.gl);
        this.gl.flush()
    };
    a.deferredRender = function() {
        let a = this.gl.getParameter(this.gl.COLOR_CLEAR_VALUE);
        this.gl.clearColor(0, 0, 0, 0);
        this.colorFramebuffer.bind(this.gl, this.gl.drawingBufferWidth,
            this.gl.drawingBufferHeight);
        this.gl.clear(this.gl.COLOR_BUFFER_BIT | this.gl.DEPTH_BUFFER_BIT);
        this.renderColor();
        this.positionFramebuffer.bind(this.gl, this.gl.drawingBufferWidth, this.gl.drawingBufferHeight);
        this.gl.clear(this.gl.COLOR_BUFFER_BIT | this.gl.DEPTH_BUFFER_BIT);
        this.renderPosition();
        this.normalFramebuffer.bind(this.gl, this.gl.drawingBufferWidth, this.gl.drawingBufferHeight);
        this.gl.clear(this.gl.COLOR_BUFFER_BIT | this.gl.DEPTH_BUFFER_BIT);
        this.renderNormal();
        this.styles.ssao_3D && e.SSAOShader ?
            (this.quadFramebuffer.bind(this.gl, this.gl.drawingBufferWidth, this.gl.drawingBufferHeight), this.gl.clear(this.gl.COLOR_BUFFER_BIT), this.renderSSAO()) : (this.ssaoFramebuffer.bind(this.gl, this.gl.drawingBufferWidth, this.gl.drawingBufferHeight), this.gl.clearColor(1, 1, 1, 1), this.gl.clear(this.gl.COLOR_BUFFER_BIT));
        this.outlineFramebuffer.bind(this.gl, this.gl.drawingBufferWidth, this.gl.drawingBufferHeight);
        this.gl.clearColor(1, 1, 1, 1);
        this.gl.clear(this.gl.COLOR_BUFFER_BIT);
        this.styles.outline_3D && this.renderOutline();
        this.gl.clearColor(a[0], a[1], a[2], a[3]);
        this.quadFramebuffer.bind(this.gl, this.gl.drawingBufferWidth, this.gl.drawingBufferHeight);
        this.gl.clear(this.gl.COLOR_BUFFER_BIT);
        this.lightingShader.useShaderProgram(this.gl);
        this.gl.uniform1i(this.lightingShader.positionSampleUniform, 0);
        this.gl.uniform1i(this.lightingShader.colorSampleUniform, 1);
        this.gl.uniform1i(this.lightingShader.ssaoSampleUniform, 2);
        this.gl.uniform1i(this.lightingShader.outlineSampleUniform, 3);
        this.gl.activeTexture(this.gl.TEXTURE0);
        this.gl.bindTexture(this.gl.TEXTURE_2D,
            this.positionTexture.texture);
        this.gl.activeTexture(this.gl.TEXTURE1);
        this.gl.bindTexture(this.gl.TEXTURE_2D, this.colorTexture.texture);
        this.gl.activeTexture(this.gl.TEXTURE2);
        this.gl.bindTexture(this.gl.TEXTURE_2D, this.ssaoTexture.texture);
        this.gl.activeTexture(this.gl.TEXTURE3);
        this.gl.bindTexture(this.gl.TEXTURE_2D, this.outlineTexture.texture);
        this.gl.activeTexture(this.gl.TEXTURE0);
        this.lightingShader.enableAttribsArray(this.gl);
        this.gl.quadBuffer.bindBuffers(this.gl);
        this.gl.drawArrays(this.gl.TRIANGLE_STRIP,
            0, this.gl.quadBuffer.vertexPositionBuffer.numItems);
        this.lightingShader.disableAttribsArray(this.gl);
        this.gl.flush();
        this.fxaaFramebuffer.bind(this.gl, this.gl.drawingBufferWidth, this.gl.drawingBufferHeight);
        this.gl.clear(this.gl.COLOR_BUFFER_BIT | this.gl.DEPTH_BUFFER_BIT);
        this.gl.viewport(0, 0, this.gl.drawingBufferWidth, this.gl.drawingBufferHeight);
        this.gl.bindTexture(this.gl.TEXTURE_2D, this.imageTexture.texture);
        this.fxaaShader.useShaderProgram(this.gl);
        this.fxaaShader.setBuffersize(this.gl, this.gl.drawingBufferWidth,
            this.gl.drawingBufferHeight);
        this.fxaaShader.setAntialias(this.gl, this.styles.antialias_3D);
        this.fxaaShader.setEdgeThreshold(this.gl, this.styles.fxaa_edgeThreshold);
        this.fxaaShader.setEdgeThresholdMin(this.gl, this.styles.fxaa_edgeThresholdMin);
        this.fxaaShader.setSearchSteps(this.gl, this.styles.fxaa_searchSteps);
        this.fxaaShader.setSearchThreshold(this.gl, this.styles.fxaa_searchThreshold);
        this.fxaaShader.setSubpixCap(this.gl, this.styles.fxaa_subpixCap);
        this.fxaaShader.setSubpixTrim(this.gl, this.styles.fxaa_subpixTrim);
        this.fxaaShader.enableAttribsArray(this.gl);
        this.gl.quadBuffer.bindBuffers(this.gl);
        this.gl.drawArrays(this.gl.TRIANGLE_STRIP, 0, this.gl.quadBuffer.vertexPositionBuffer.numItems);
        this.fxaaShader.disableAttribsArray(this.gl);
        this.gl.flush();
        this.finalFramebuffer.bind(this.gl, this.gl.drawingBufferWidth, this.gl.drawingBufferHeight);
        this.renderExtras();
        this.gl.clearColor(a[0], a[1], a[2], a[3]);
        this.gl.bindFramebuffer(this.gl.FRAMEBUFFER, null);
        this.gl.clear(this.gl.COLOR_BUFFER_BIT | this.gl.DEPTH_BUFFER_BIT);
        this.gl.viewport(0, 0, this.gl.drawingBufferWidth, this.gl.drawingBufferHeight);
        this.gl.bindTexture(this.gl.TEXTURE_2D, this.fxaaTexture.texture);
        this.quadShader.useShaderProgram(this.gl);
        this.quadShader.enableAttribsArray(this.gl);
        this.gl.quadBuffer.bindBuffers(this.gl);
        this.gl.drawArrays(this.gl.TRIANGLE_STRIP, 0, this.gl.quadBuffer.vertexPositionBuffer.numItems);
        this.quadShader.disableAttribsArray(this.gl);
        this.gl.flush()
    };
    a.forwardRender = function() {
        this.gl.bindFramebuffer(this.gl.FRAMEBUFFER, null);
        this.gl.clear(this.gl.COLOR_BUFFER_BIT | this.gl.DEPTH_BUFFER_BIT);
        this.gl.viewport(0, 0, this.gl.drawingBufferWidth, this.gl.drawingBufferHeight);
        this.renderColor();
        this.renderExtras()
    };
    a.repaint = function() {
        this.gl && (this.gl.lightViewMatrix = h.multiply(this.lighting.camera.viewMatrix, this.rotationMatrix, []), this.gl.rotationMatrix = this.rotationMatrix, this.gl.modelViewMatrix = this.gl.lightViewMatrix, this.renderDepthMap(), this.gl.modelViewMatrix = h.multiply(this.camera.viewMatrix, this.rotationMatrix, []), h.translate(this.gl.modelViewMatrix,
            this.contentCenter), this.isSupportDeferred() && (this.styles.ssao_3D || this.styles.outline_3D) ? this.deferredRender() : this.forwardRender())
    };
    a.pick = function(a, b, d, e) {
        if (this.gl) {
            let c = this.height - b;
            1 !== this.pixelRatio && (a *= this.pixelRatio, c *= this.pixelRatio);
            h.multiply(this.camera.viewMatrix, this.rotationMatrix, this.gl.modelViewMatrix);
            h.translate(this.gl.modelViewMatrix, this.contentCenter);
            this.gl.rotationMatrix = this.rotationMatrix;
            this.pickShader.useShaderProgram(this.gl);
            b = this.gl.getParameter(this.gl.COLOR_CLEAR_VALUE);
            this.gl.clearColor(1, 1, 1, 0);
            this.pickerFramebuffer.bind(this.gl, this.gl.drawingBufferWidth, this.gl.drawingBufferHeight);
            this.gl.clear(this.gl.COLOR_BUFFER_BIT | this.gl.DEPTH_BUFFER_BIT);
            this.pickShader.setProjectionMatrix(this.gl, this.camera.projectionMatrix);
            this.pickShader.enableAttribsArray(this.gl);
            let f = [];
            for (let a = 0, b = this.molecules.length; a < b; a++) this.molecules[a].renderPickFrame(this.gl, this.styles, f, d, e);
            this.pickShader.disableAttribsArray(this.gl);
            this.gl.flush();
            d = new Uint8Array(4);
            this.gl.readPixels(a -
                2, c + 2, 1, 1, this.gl.RGBA, this.gl.UNSIGNED_BYTE, d);
            e = m;
            0 < d[3] && (e = f[d[2] | d[1] << 8 | d[0] << 16]);
            this.gl.bindFramebuffer(this.gl.FRAMEBUFFER, null);
            this.gl.clearColor(b[0], b[1], b[2], b[3]);
            return e
        }
        return m
    };
    a.center = function() {
        let a = new t.Atom,
            b = this.molecules.length;
        for (let d = 0, e = b; d < e; d++) a.add3D(this.molecules[d].getCenter3D());
        a.x /= b;
        a.y /= b;
        a.z /= b;
        this.contentCenter = [-a.x, -a.y, -a.z]
    };
    a.isSupportDeferred = function() {
        return this.gl.textureFloatExt && this.gl.depthTextureExt
    };
    a.create = function(a, b, f) {
        x.create.call(this,
            a, b, f);
        try {
            let a = d.getElementById(this.id);
            this.gl = a.getContext("webgl");
            this.gl || (this.gl = a.getContext("experimental-webgl"))
        } catch (y) {}
        this.gl ? (1 !== this.pixelRatio && this.gl.canvas.width === this.width && (this.gl.canvas.style.width = this.width + "px", this.gl.canvas.style.height = this.height + "px", this.gl.canvas.width = this.width * this.pixelRatio, this.gl.canvas.height = this.height * this.pixelRatio), this.gl.enable(this.gl.DEPTH_TEST), this.gl.depthFunc(this.gl.LEQUAL), this.gl.blendFuncSeparate(this.gl.SRC_ALPHA,
                this.gl.ONE_MINUS_SRC_ALPHA, this.gl.ONE, this.gl.ONE_MINUS_SRC_ALPHA), this.gl.clearDepth(1), this.shadowTextureSize = 1024, this.rotationMatrix = h.identity([]), this.contentCenter = [0, 0, 0], this.camera = new e.Camera, this.label3D = new e.Label, this.lighting = new e.Light(this.styles.lightDiffuseColor_3D, this.styles.lightSpecularColor_3D, this.styles.lightDirection_3D), this.fogging = new e.Fog(this.styles.fog_color_3D || this.styles.backgroundColor, this.styles.fog_start_3D, this.styles.fog_end_3D, this.styles.fog_density_3D),
            this.gl.depthTextureExt = this.gl.getExtension("WEBGL_depth_texture") || this.gl.getExtension("WEBKIT_WEBGL_depth_texture") || this.gl.getExtension("MOZ_WEBGL_depth_texture"), this.gl.textureFloatExt = this.gl.getExtension("OES_texture_float") || this.gl.getExtension("WEBKIT_OES_texture_float") || this.gl.getExtension("MOZ_OES_texture_float"), this.ssao = new e.SSAO, this.pickerColorTexture = new e.Texture, this.pickerColorTexture.init(this.gl, this.gl.UNSIGNED_BYTE, this.gl.RGBA, this.gl.RGBA), this.pickerDepthRenderbuffer =
            new e.Renderbuffer, this.pickerDepthRenderbuffer.init(this.gl, this.gl.DEPTH_COMPONENT16), this.pickerFramebuffer = new e.Framebuffer, this.pickerFramebuffer.init(this.gl), this.pickerFramebuffer.setColorTexture(this.gl, this.pickerColorTexture.texture), this.pickerFramebuffer.setDepthRenderbuffer(this.gl, this.pickerDepthRenderbuffer.renderbuffer), this.lightDepthMapTexture = new e.Texture, this.lightDepthMapRenderbuffer = new e.Renderbuffer, this.lightDepthMapFramebuffer = new e.Framebuffer, this.lightDepthMapFramebuffer.init(this.gl),
            this.gl.depthTextureExt ? (this.lightDepthMapTexture.init(this.gl, this.gl.UNSIGNED_SHORT, this.gl.DEPTH_COMPONENT), this.lightDepthMapRenderbuffer.init(this.gl, this.gl.RGBA4), this.lightDepthMapFramebuffer.setColorRenderbuffer(this.gl, this.lightDepthMapRenderbuffer.renderbuffer), this.lightDepthMapFramebuffer.setDepthTexture(this.gl, this.lightDepthMapTexture.texture)) : (this.lightDepthMapTexture.init(this.gl, this.gl.UNSIGNED_BYTE, this.gl.RGBA, this.gl.RGBA), this.lightDepthMapRenderbuffer.init(this.gl, this.gl.DEPTH_COMPONENT16),
                this.lightDepthMapFramebuffer.setColorTexture(this.gl, this.lightDepthMapTexture.texture), this.lightDepthMapFramebuffer.setDepthRenderbuffer(this.gl, this.lightDepthMapRenderbuffer.renderbuffer)), this.isSupportDeferred() && (this.depthTexture = new e.Texture, this.depthTexture.init(this.gl, this.gl.UNSIGNED_SHORT, this.gl.DEPTH_COMPONENT), this.colorTexture = new e.Texture, this.colorTexture.init(this.gl, this.gl.UNSIGNED_BYTE, this.gl.RGBA), this.positionTexture = new e.Texture, this.positionTexture.init(this.gl, this.gl.FLOAT,
                    this.gl.RGBA), this.normalTexture = new e.Texture, this.normalTexture.init(this.gl, this.gl.FLOAT, this.gl.RGBA), this.ssaoTexture = new e.Texture, this.ssaoTexture.init(this.gl, this.gl.FLOAT, this.gl.RGBA), this.outlineTexture = new e.Texture, this.outlineTexture.init(this.gl, this.gl.UNSIGNED_BYTE, this.gl.RGBA), this.fxaaTexture = new e.Texture, this.fxaaTexture.init(this.gl, this.gl.FLOAT, this.gl.RGBA), this.imageTexture = new e.Texture, this.imageTexture.init(this.gl, this.gl.FLOAT, this.gl.RGBA), this.colorFramebuffer =
                new e.Framebuffer, this.colorFramebuffer.init(this.gl), this.colorFramebuffer.setColorTexture(this.gl, this.colorTexture.texture), this.colorFramebuffer.setDepthTexture(this.gl, this.depthTexture.texture), this.normalFramebuffer = new e.Framebuffer, this.normalFramebuffer.init(this.gl), this.normalFramebuffer.setColorTexture(this.gl, this.normalTexture.texture), this.normalFramebuffer.setDepthTexture(this.gl, this.depthTexture.texture), this.positionFramebuffer = new e.Framebuffer, this.positionFramebuffer.init(this.gl),
                this.positionFramebuffer.setColorTexture(this.gl, this.positionTexture.texture), this.positionFramebuffer.setDepthTexture(this.gl, this.depthTexture.texture), this.ssaoFramebuffer = new e.Framebuffer, this.ssaoFramebuffer.init(this.gl), this.ssaoFramebuffer.setColorTexture(this.gl, this.ssaoTexture.texture), this.outlineFramebuffer = new e.Framebuffer, this.outlineFramebuffer.init(this.gl), this.outlineFramebuffer.setColorTexture(this.gl, this.outlineTexture.texture), this.fxaaFramebuffer = new e.Framebuffer, this.fxaaFramebuffer.init(this.gl),
                this.fxaaFramebuffer.setColorTexture(this.gl, this.fxaaTexture.texture), this.quadFramebuffer = new e.Framebuffer, this.quadFramebuffer.init(this.gl), this.quadFramebuffer.setColorTexture(this.gl, this.imageTexture.texture), this.finalFramebuffer = new e.Framebuffer, this.finalFramebuffer.init(this.gl), this.finalFramebuffer.setColorTexture(this.gl, this.fxaaTexture.texture), this.finalFramebuffer.setDepthTexture(this.gl, this.depthTexture.texture), this.normalShader = new e.NormalShader, this.normalShader.init(this.gl),
                this.positionShader = new e.PositionShader, this.positionShader.init(this.gl), e.SSAOShader && (this.ssaoShader = new e.SSAOShader, this.ssaoShader.init(this.gl), this.ssaoBlurShader = new e.SSAOBlurShader, this.ssaoBlurShader.init(this.gl)), this.outlineShader = new e.OutlineShader, this.outlineShader.init(this.gl), this.lightingShader = new e.LightingShader, this.lightingShader.init(this.gl), this.fxaaShader = new e.FXAAShader, this.fxaaShader.init(this.gl), this.quadShader = new e.QuadShader, this.quadShader.init(this.gl)),
            this.labelShader = new e.LabelShader, this.labelShader.init(this.gl), this.pickShader = new e.PickShader, this.pickShader.init(this.gl), this.phongShader = new e.PhongShader, this.phongShader.init(this.gl), e.DepthShader && (this.depthShader = new e.DepthShader, this.depthShader.init(this.gl)), this.textTextImage = new e.TextImage, this.textTextImage.init(this.gl), this.gl.textImage = new e.TextImage, this.gl.textImage.init(this.gl), this.gl.textMesh = new e.TextMesh, this.gl.textMesh.init(this.gl), this.gl.material = new e.Material,
            this.setupScene()) : this.displayMessage()
    };
    a.displayMessage = function() {
        var a = d.getElementById(this.id);
        a.getContext && (a = a.getContext("2d"), this.styles.backgroundColor && (a.fillStyle = this.styles.backgroundColor, a.fillRect(0, 0, this.width, this.height)), this.emptyMessage && (a.fillStyle = "#737683", a.textAlign = "center", a.textBaseline = "middle", a.font = "18px Helvetica, Verdana, Arial, Sans-serif", a.fillText(this.emptyMessage, this.width / 2, this.height / 2)))
    };
    a.renderText = function(a, b) {
        let d = {
            position: [],
            texCoord: [],
            translation: []
        };
        this.textTextImage.pushVertexData(a, b, 0, d);
        this.gl.textMesh.storeData(this.gl, d.position, d.texCoord, d.translation);
        this.textTextImage.useTexture(this.gl);
        this.gl.textMesh.render(this.gl)
    };
    a.setupScene = function() {
        if (this.gl) {
            var a = n("#" + this.id),
                d = this.styles.backgroundColor ? this.styles.backgroundColor : "transparent";
            a.css("background-color", d);
            a = "transparent" === d ? [0, 0, 0, 0] : l.getRGB(d, 1);
            this.gl.clearColor(a[0], a[1], a[2], 4 == a.length ? a[3] : 1);
            this.styles.cullBackFace_3D ? this.gl.enable(this.gl.CULL_FACE) :
                this.gl.disable(this.gl.CULL_FACE);
            this.gl.sphereBuffer = new e.Sphere(1, this.styles.atoms_resolution_3D, this.styles.atoms_resolution_3D);
            this.gl.starBuffer = new e.Star;
            this.gl.cylinderBuffer = new e.Cylinder(1, 1, this.styles.bonds_resolution_3D);
            this.gl.cylinderClosedBuffer = new e.Cylinder(1, 1, this.styles.bonds_resolution_3D, !0);
            this.gl.boxBuffer = new e.Box(1, 1, 1);
            this.gl.pillBuffer = new e.Pill(this.styles.bonds_pillDiameter_3D / 2, this.styles.bonds_pillHeight_3D, this.styles.bonds_pillLatitudeResolution_3D,
                this.styles.bonds_pillLongitudeResolution_3D);
            this.gl.lineBuffer = new e.Line;
            this.gl.lineArrowBuffer = new e.LineArrow;
            this.gl.arrowBuffer = new e.Arrow(.3, this.styles.compass_resolution_3D);
            this.gl.quadBuffer = new e.Quad;
            this.gl.textImage.updateFont(this.gl, this.styles.text_font_size, this.styles.text_font_families, this.styles.text_font_bold, this.styles.text_font_italic, this.styles.text_font_stroke_3D);
            this.lighting.lightScene(this.styles.lightDiffuseColor_3D, this.styles.lightSpecularColor_3D, this.styles.lightDirection_3D);
            this.fogging.fogScene(this.styles.fog_color_3D || this.styles.backgroundColor, this.styles.fog_start_3D, this.styles.fog_end_3D, this.styles.fog_density_3D);
            this.compass = new e.Compass(this.gl, this.styles);
            this.lightDepthMapTexture.setParameter(this.gl, this.shadowTextureSize, this.shadowTextureSize);
            this.lightDepthMapRenderbuffer.setParameter(this.gl, this.shadowTextureSize, this.shadowTextureSize);
            this.pickerColorTexture.setParameter(this.gl, this.gl.drawingBufferWidth, this.gl.drawingBufferHeight);
            this.pickerDepthRenderbuffer.setParameter(this.gl,
                this.gl.drawingBufferWidth, this.gl.drawingBufferHeight);
            this.isSupportDeferred() && (this.depthTexture.setParameter(this.gl, this.gl.drawingBufferWidth, this.gl.drawingBufferHeight), this.colorTexture.setParameter(this.gl, this.gl.drawingBufferWidth, this.gl.drawingBufferHeight), this.imageTexture.setParameter(this.gl, this.gl.drawingBufferWidth, this.gl.drawingBufferHeight), this.positionTexture.setParameter(this.gl, this.gl.drawingBufferWidth, this.gl.drawingBufferHeight), this.normalTexture.setParameter(this.gl,
                this.gl.drawingBufferWidth, this.gl.drawingBufferHeight), this.ssaoTexture.setParameter(this.gl, this.gl.drawingBufferWidth, this.gl.drawingBufferHeight), this.outlineTexture.setParameter(this.gl, this.gl.drawingBufferWidth, this.gl.drawingBufferHeight), this.fxaaTexture.setParameter(this.gl, this.gl.drawingBufferWidth, this.gl.drawingBufferHeight), this.ssao.initSampleKernel(this.styles.ssao_kernel_samples), this.ssao.initNoiseTexture(this.gl));
            this.camera.updateProjectionMatrix(this.styles.projectionPerspective_3D);
            for (let f = 0, n = this.molecules.length; f < n; f++)
                if (a = this.molecules[f], a.labelMesh instanceof e.TextMesh || (a.labelMesh = new e.TextMesh, a.labelMesh.init(this.gl)), a.chains) {
                    a.ribbons = [];
                    a.cartoons = [];
                    a.tubes = [];
                    a.pipePlanks = [];
                    for (let f = 0, n = a.chains.length; f < n; f++) {
                        d = a.chains[f];
                        for (let a = 0, b = d.length - 1; a < b; a++) d[a].Test = a;
                        var h = 3 < d.length && k[d[3].name] && "#BEA06E" === k[d[3].name].aminoColor;
                        if (0 < d.length && !d[0].lineSegments) {
                            for (let a = 0, b = d.length - 1; a < b; a++) d[a].setup(d[a + 1].cp1, h ? 1 : this.styles.proteins_horizontalResolution);
                            if (!h)
                                for (let a = 1, c = d.length - 1; a < c; a++) q.vec3AngleFrom(d[a - 1].D, d[a].D) > b.PI / 2 && (d[a].guidePointsSmall.reverse(), d[a].guidePointsLarge.reverse(), g.scale(d[a].D, -1));
                            for (let a = 2, b = d.length - 3; a < b; a++) d[a].computeLineSegments(d[a - 2], d[a - 1], d[a + 1], !h, h ? this.styles.nucleics_verticalResolution : this.styles.proteins_verticalResolution);
                            d.pop();
                            d.pop();
                            d.pop();
                            d.shift();
                            d.shift()
                        }
                        var m = l.hsl2rgb(1 === n ? .5 : f / n, 1, .5);
                        m = "rgb(" + m[0] + "," + m[1] + "," + m[2] + ")";
                        d.chainColor = m;
                        if (h) d = new e.Tube(d, this.styles.nucleics_tubeThickness,
                            this.styles.nucleics_tubeResolution_3D), d.chainColor = m, a.tubes.push(d);
                        else {
                            h = new e.PipePlank(d, this.styles);
                            a.pipePlanks.push(h);
                            h = d.shift();
                            var c = {
                                front: new e.Ribbon(d, this.styles.proteins_ribbonThickness, !1),
                                back: new e.Ribbon(d, -this.styles.proteins_ribbonThickness, !1)
                            };
                            c.front.chainColor = m;
                            c.back.chainColor = m;
                            a.ribbons.push(c);
                            c = {
                                front: new e.Ribbon(d, this.styles.proteins_ribbonThickness, !0),
                                back: new e.Ribbon(d, -this.styles.proteins_ribbonThickness, !0)
                            };
                            c.front.chainColor = m;
                            c.back.chainColor = m;
                            a.cartoons.push(c);
                            d.unshift(h)
                        }
                    }
                } this.label3D.updateVerticesBuffer(this.gl, this.getMolecules(), this.styles);
            if (this instanceof f.MovieCanvas3D && this.frames)
                for (let b = 0, c = this.frames.length; b < c; b++) {
                    a = this.frames[b];
                    for (let b = 0, c = a.mols.length; b < c; b++) d = a.mols[b], d.labelMesh instanceof t.d3.TextMesh || (d.labelMesh = new t.d3.TextMesh, d.labelMesh.init(this.gl));
                    this.label3D.updateVerticesBuffer(this.gl, a.mols, this.styles)
                }
        }
    };
    a.updateScene = function() {
        this.camera.updateProjectionMatrix(this.styles.projectionPerspective_3D);
        this.lighting.lightScene(this.styles.lightDiffuseColor_3D, this.styles.lightSpecularColor_3D, this.styles.lightDirection_3D);
        this.fogging.fogScene(this.styles.fog_color_3D || this.styles.backgroundColor, this.styles.fog_start_3D, this.styles.fog_end_3D, this.styles.fog_density_3D);
        this.repaint()
    };
    a.mousedown = function(a) {
        this.lastPoint = a.p
    };
    a.mouseup = function(a) {
        this.lastPoint = m
    };
    a.rightmousedown = function(a) {
        this.lastPoint = a.p
    };
    a.drag = function(a) {
        if (this.lastPoint) {
            if (f.monitor.ALT) {
                var d = new t.Point(a.p.x,
                    a.p.y);
                d.sub(this.lastPoint);
                var e = b.tan(this.camera.fieldOfView / 360 * b.PI);
                e = this.height / 2 / this.camera.zoom / e;
                e = this.camera.focalLength() / e;
                h.translate(this.camera.viewMatrix, [d.x * e, -d.y * e, 0])
            } else e = a.p.x - this.lastPoint.x, d = a.p.y - this.lastPoint.y, e = h.rotate(h.identity([]), e * b.PI / 180, [0, 1, 0]), h.rotate(e, d * b.PI / 180, [1, 0, 0]), this.rotationMatrix = h.multiply(e, this.rotationMatrix);
            this.lastPoint = a.p;
            this.repaint()
        }
    };
    a.mousewheel = function(a, b) {
        0 < b ? this.camera.zoomIn() : this.camera.zoomOut();
        this.updateScene()
    };
    a.multitouchmove = function(a, d) {
        if (2 === d)
            if (this.lastPoint && this.lastPoint.multi) {
                d = new t.Point(a.p.x, a.p.y);
                d.sub(this.lastPoint);
                var e = b.tan(this.camera.fieldOfView / 360 * b.PI);
                e = this.height / 2 / this.camera.zoom / e;
                e = this.camera.focalLength() / e;
                h.translate(this.camera.viewMatrix, [d.x * e, -d.y * e, 0]);
                this.lastPoint = a.p;
                this.repaint()
            } else this.lastPoint = a.p, this.lastPoint.multi = !0
    };
    a.gesturechange = function(a) {
        if (0 !== a.originalEvent.scale - this.lastPinchScale) {
            let b = 30 * -(a.originalEvent.scale / this.lastPinchScale -
                1);
            if (isNaN(b)) return;
            0 < b ? this.camera.zoomOut() : this.camera.zoomIn();
            this.updateScene();
            this.lastPinchScale = a.originalEvent.scale
        }
        this.repaint()
    };
    a.gestureend = function(a) {
        this.lastPinchScale = 1;
        this.lastGestureRotate = 0
    }
})(ChemDoodle, ChemDoodle.extensions, ChemDoodle.math, ChemDoodle.structures, ChemDoodle.structures.d3, ChemDoodle.RESIDUE, Math, document, ChemDoodle.lib.mat4, ChemDoodle.lib.mat3, ChemDoodle.lib.vec3, ChemDoodle.lib.jQuery, window);
(function(f, q, l, t, e) {
    f.MolGrabberCanvas3D = function(e, b, d) {
        e && this.create(e, b, d);
        b = [];
        b.push('\x3cbr\x3e\x3cinput type\x3d"text" id\x3d"');
        b.push(e);
        b.push('_query" size\x3d"32" value\x3d"" /\x3e');
        b.push("\x3cbr\x3e\x3cnobr\x3e");
        b.push('\x3cselect id\x3d"');
        b.push(e);
        b.push('_select"\x3e');
        b.push('\x3coption value\x3d"pubchem" selected\x3ePubChem');
        b.push("\x3c/select\x3e");
        b.push('\x3cbutton type\x3d"button" id\x3d"');
        b.push(e);
        b.push('_submit"\x3eShow Molecule\x3c/button\x3e');
        b.push("\x3c/nobr\x3e");
        t.writeln(b.join(""));
        let f = this;
        l("#" + e + "_submit").click(function() {
            f.search()
        });
        l("#" + e + "_query").keypress(function(a) {
            13 === a.which && f.search()
        })
    };
    f = f.MolGrabberCanvas3D.prototype = new f._Canvas3D;
    f.setSearchTerm = function(e) {
        l("#" + this.id + "_query").val(e);
        this.search()
    };
    f.search = function() {
        let e = this;
        q.getMoleculeFromDatabase(l("#" + this.id + "_query").val(), {
            database: l("#" + this.id + "_select").val(),
            dimension: 3
        }, function(b) {
            e.loadMolecule(b)
        })
    }
})(ChemDoodle, ChemDoodle.iChemLabs, ChemDoodle.lib.jQuery,
    document);
(function(f, q, l) {
    f.MovieCanvas3D = function(f, e, k) {
        f && this.create(f, e, k);
        this.frames = []
    };
    f.MovieCanvas3D.PLAY_ONCE = 0;
    f.MovieCanvas3D.PLAY_LOOP = 1;
    f.MovieCanvas3D.PLAY_SPRING = 2;
    l = f.MovieCanvas3D.prototype = new f._Canvas3D;
    l.timeout = 50;
    l.frameNumber = 0;
    l.playMode = 2;
    l.reverse = !1;
    l.startAnimation = f._AnimatorCanvas.prototype.startAnimation;
    l.stopAnimation = f._AnimatorCanvas.prototype.stopAnimation;
    l.isRunning = f._AnimatorCanvas.prototype.isRunning;
    l.dblclick = f.RotatorCanvas.prototype.dblclick;
    l.nextFrame = function(f) {
        f =
            this.frames[this.frameNumber];
        this.molecules = f.mols;
        this.shapes = f.shapes;
        2 === this.playMode && this.reverse ? (this.frameNumber--, 0 > this.frameNumber && (this.frameNumber = 1, this.reverse = !1)) : (this.frameNumber++, this.frameNumber >= this.frames.length && (2 === this.playMode ? (this.frameNumber -= 2, this.reverse = !0) : (this.frameNumber = 0, 0 === this.playMode && this.stopAnimation())))
    };
    l.center = function() {
        var f = new q.Atom,
            e = this.frames[0];
        for (let k = 0, b = e.mols.length; k < b; k++) f.add3D(e.mols[k].getCenter3D());
        f.x /= e.mols.length;
        f.y /= e.mols.length;
        e = new q.Atom;
        e.sub3D(f);
        for (let k = 0, b = this.frames.length; k < b; k++) {
            f = this.frames[k];
            for (let b = 0, h = f.mols.length; b < h; b++) {
                let a = f.mols[b];
                for (let b = 0, d = a.atoms.length; b < d; b++) a.atoms[b].add3D(e)
            }
        }
    };
    l.addFrame = function(f, e) {
        this.frames.push({
            mols: f,
            shapes: e
        })
    }
})(ChemDoodle, ChemDoodle.structures);
(function(f, q, l, t) {
    let e = [],
        k = [1, 0, 0],
        b = [0, 1, 0],
        d = [0, 0, 1];
    f.RotatorCanvas3D = function(a, b, d) {
        a && this.create(a, b, d)
    };
    let h = f.RotatorCanvas3D.prototype = new f._Canvas3D;
    h.timeout = 33;
    q = q.PI / 15;
    h.xIncrement = q;
    h.yIncrement = q;
    h.zIncrement = q;
    h.startAnimation = f._AnimatorCanvas.prototype.startAnimation;
    h.stopAnimation = f._AnimatorCanvas.prototype.stopAnimation;
    h.isRunning = f._AnimatorCanvas.prototype.isRunning;
    h.dblclick = f.RotatorCanvas.prototype.dblclick;
    h.mousedown = t;
    h.rightmousedown = t;
    h.drag = t;
    h.mousewheel =
        t;
    h.nextFrame = function(a) {
        0 === this.molecules.length && 0 === this.shapes.length ? this.stopAnimation() : (l.identity(e), a /= 1E3, l.rotate(e, this.xIncrement * a, k), l.rotate(e, this.yIncrement * a, b), l.rotate(e, this.zIncrement * a, d), l.multiply(this.rotationMatrix, e))
    }
})(ChemDoodle, Math, ChemDoodle.lib.mat4);
(function(f, q) {
    f.TransformCanvas3D = function(f, q, e) {
        f && this.create(f, q, e)
    };
    f.TransformCanvas3D.prototype = new f._Canvas3D
})(ChemDoodle);
(function(f, q) {
    f.ViewerCanvas3D = function(f, q, e) {
        f && this.create(f, q, e)
    };
    f = f.ViewerCanvas3D.prototype = new f._Canvas3D;
    f.mousedown = q;
    f.rightmousedown = q;
    f.drag = q;
    f.mousewheel = q
})(ChemDoodle);
(function(f, q, l, t, e) {
    function k(b, d, e, a) {
        this.element = b;
        this.x = d;
        this.y = e;
        this.dimension = a;
        this.allowMultipleSelections = !1
    }
    f.PeriodicTableCanvas = function(b, d) {
        this.padding = 5;
        b && this.create(b, 18 * d + 2 * this.padding, 10 * d + 2 * this.padding);
        this.cellDimension = d ? d : 20;
        this.setupTable();
        this.repaint()
    };
    t = f.PeriodicTableCanvas.prototype = new f._Canvas;
    t.loadMolecule = e;
    t.getMolecule = e;
    t.getHoveredElement = function() {
        return this.hovered ? this.hovered.element : e
    };
    t.innerRepaint = function(b) {
        for (let d = 0, e = this.cells.length; d <
            e; d++) this.drawCell(b, this.styles, this.cells[d]);
        this.hovered && this.drawCell(b, this.styles, this.hovered);
        this.selected && this.drawCell(b, this.styles, this.selected)
    };
    t.setupTable = function() {
        this.cells = [];
        let b = this.padding,
            d = this.padding;
        var e = 0;
        for (let g = 0, h = f.SYMBOLS.length; g < h; g++) {
            18 === e && (e = 0, d += this.cellDimension, b = this.padding);
            var a = f.ELEMENT[f.SYMBOLS[g]];
            if (2 === a.atomicNumber) b += 16 * this.cellDimension, e += 16;
            else if (5 === a.atomicNumber || 13 === a.atomicNumber) b += 10 * this.cellDimension, e += 10;
            (58 >
                a.atomicNumber || 71 < a.atomicNumber && 90 > a.atomicNumber || 103 < a.atomicNumber) && 118 >= a.atomicNumber && (this.cells.push(new k(a, b, d, this.cellDimension)), b += this.cellDimension, e++)
        }
        d += 2 * this.cellDimension;
        b = 3 * this.cellDimension + this.padding;
        for (e = 57; 104 > e; e++)
            if (a = f.ELEMENT[f.SYMBOLS[e]], 90 === a.atomicNumber && (d += this.cellDimension, b = 3 * this.cellDimension + this.padding), 58 <= a.atomicNumber && 71 >= a.atomicNumber || 90 <= a.atomicNumber && 103 >= a.atomicNumber) this.cells.push(new k(a, b, d, this.cellDimension)), b += this.cellDimension
    };
    t.drawCell = function(b, d, e) {
        let a = b.createRadialGradient(e.x + e.dimension / 3, e.y + e.dimension / 3, 1.5 * e.dimension, e.x + e.dimension / 3, e.y + e.dimension / 3, e.dimension / 10);
        a.addColorStop(0, "#000000");
        a.addColorStop(.7, e.element.jmolColor);
        a.addColorStop(1, "#FFFFFF");
        b.fillStyle = a;
        q.contextRoundRect(b, e.x, e.y, e.dimension, e.dimension, e.dimension / 8);
        if (e === this.hovered || e === this.selected || e.selected) b.lineWidth = 2, b.strokeStyle = "#c10000", b.stroke(), b.fillStyle = "white";
        b.fill();
        b.font = q.getFontString(d.text_font_size,
            d.text_font_families);
        b.fillStyle = d.text_color;
        b.textAlign = "center";
        b.textBaseline = "middle";
        b.fillText(e.element.symbol, e.x + e.dimension / 2, e.y + e.dimension / 2)
    };
    t.click = function(b) {
        this.hovered && (this.allowMultipleSelections ? this.hovered.selected = !this.hovered.selected : this.selected = this.hovered, this.repaint())
    };
    t.touchstart = function(b) {
        this.mousemove(b)
    };
    t.mousemove = function(b) {
        let d = b.p.x;
        b = b.p.y;
        this.hovered = e;
        for (let e = 0, a = this.cells.length; e < a; e++) {
            let a = this.cells[e];
            if (l.isBetween(d, a.x, a.x + a.dimension) &&
                l.isBetween(b, a.y, a.y + a.dimension)) {
                this.hovered = a;
                break
            }
        }
        this.repaint()
    };
    t.mouseout = function(b) {
        this.hovered = e;
        this.repaint()
    }
})(ChemDoodle, ChemDoodle.extensions, ChemDoodle.math, document);
(function(f, q, l, t) {
    f.png = {};
    f.png.string = function(e) {
        return q.getElementById(e.id).toDataURL("image/png")
    };
    f.png.open = function(e) {
        l.open(this.string(e))
    }
})(ChemDoodle.io, document, window);
(function(f, q, l) {
    f.file = {};
    f.file.content = function(f, e) {
        q.get(f, "", e)
    }
})(ChemDoodle.io, ChemDoodle.lib.jQuery);
(function(f, q, l, t, e, k, b) {
    q.SERVER_URL = "https://ichemlabs.cloud.chemdoodle.com/icl_cdc_v090000/WebHQ";
    q.inRelay = !1;
    q.asynchronous = !0;
    q.INFO = {
        userAgent: navigator.userAgent,
        platform: navigator.platform,
        v_cwc: f.getVersion(),
        v_jQuery: e.fn.jquery,
        v_jQuery_ui: "N/A"
    };
    let d = new l.JSONInterpreter,
        h = new t.Queue;
    q._contactServer = function(a, b, d, f, m) {
        this.inRelay ? h.enqueue({
            call: a,
            content: b,
            options: d,
            callback: f,
            errorback: m
        }) : (q.inRelay = !0, e.ajax({
            dataType: "text",
            type: "POST",
            data: JSON.stringify({
                call: a,
                content: b,
                options: d,
                info: q.INFO
            }),
            url: this.SERVER_URL,
            success: function(a) {
                a = JSON.parse(a);
                a.message && alert(a.message);
                q.inRelay = !1;
                f && a.content && !a.stop && f(a.content);
                a.stop && m && m();
                h.isEmpty() || (a = h.dequeue(), q._contactServer(a.call, a.content, a.options, a.callback, a.errorback))
            },
            error: function(a, b, d) {
                q.inRelay = !1;
                m && m();
                h.isEmpty() || (a = h.dequeue(), q._contactServer(a.call, a.content, a.options, a.callback, a.errorback))
            },
            xhrFields: {
                withCredentials: !0
            },
            async: q.asynchronous
        }))
    };
    // q.authenticate = function(a, b, d, e) {
    //     this._contactServer("authenticate", {
    //         credential: a
    //     }, b, function(a) {
    //         d(a)
    //     }, e)
    // };
    // q.balanceReaction = function(a, b, e, f) {
    //     let g = {};
    //     "string" === typeof a || a instanceof String ? g.equation = a : g.reaction = d.contentTo(a.molecules, a.shapes);
    //     this._contactServer("balanceReaction", g, b, function(a) {
    //         e(a.result, a.message)
    //     }, f)
    // };
    // q.calculate = function(a, b, e, f) {
    //     this._contactServer("calculate", {
    //         mol: d.molTo(a)
    //     }, b, function(a) {
    //         e(a)
    //     }, f)
    // };
    // q.createLewisDotStructure = function(a, b, e, f) {
    //     this._contactServer("createLewisDot", {
    //         mol: d.molTo(a)
    //     }, b, function(a) {
    //         e(d.molFrom(a.mol))
    //     }, f)
    // };
    // q.generateImage = function(a, b, e, f) {
    //     this._contactServer("generateImage", {
    //         mol: d.molTo(a)
    //     }, b, function(a) {
    //         e(a.link)
    //     }, f)
    // };
    // q.generateIUPACName = function(a, b, e, f) {
    //     this._contactServer("generateIUPACName", {
    //         mol: d.molTo(a)
    //     }, b, function(a) {
    //         e(a.iupac)
    //     }, f)
    // };
    // q.getMoleculeFromContent = function(a, b, e, f) {
    //     this._contactServer("getMoleculeFromContent", {
    //         content: a
    //     }, b, function(a) {
    //         let b = !1;
    //         for (let d = 0, e = a.mol.a.length; d < e; d++)
    //             if (0 !== a.mol.a[d].z) {
    //                 b = !0;
    //                 break
    //             } if (b)
    //             for (let b = 0, d = a.mol.a.length; b < d; b++) a.mol.a[b].x /= 20, a.mol.a[b].y /=
    //                 20, a.mol.a[b].z /= 20;
    //         e(d.molFrom(a.mol))
    //     }, f)
    // };
    // q.getMoleculeFromDatabase = function(a, b, e, f) {
    //     this._contactServer("getMoleculeFromDatabase", {
    //         query: a
    //     }, b, function(a) {
    //         if (3 === b.dimension)
    //             for (let b = 0, d = a.mol.a.length; b < d; b++) a.mol.a[b].x /= 20, a.mol.a[b].y /= -20, a.mol.a[b].z /= 20;
    //         e(d.molFrom(a.mol))
    //     }, f)
    // };
    // q.getOptimizedPDBStructure = function(a, b, e, f) {
    //     this._contactServer("getOptimizedPDBStructure", {
    //         id: a
    //     }, b, function(a) {
    //         let b;
    //         b = a.mol ? d.molFrom(a.mol) : new t.Molecule;
    //         b.chains = d.chainsFrom(a.ribbons);
    //         for (let d = 0, e = b.chains.length; d <
    //             e; d++) {
    //             a = b.chains[d];
    //             for (let b = 0, d = a.length - 1; b < d; b++) a[b + 1].arrow && (a[b + 1].arrow = !1, a[b].arrow = !0)
    //         }
    //         b.fromJSON = !0;
    //         e(b)
    //     }, f)
    // };
    // q.getZeoliteFromIZA = function(a, b, d, e) {
    //     this._contactServer("getZeoliteFromIZA", {
    //         query: a
    //     }, b, function(a) {
    //         d(ChemDoodle.readCIF(a.cif, b.xSuper, b.ySuper, b.zSuper))
    //     }, e)
    // };
    // q.isGraphIsomorphism = function(a, b, e, f, h) {
    //     this._contactServer("isGraphIsomorphism", {
    //         arrow: d.molTo(a),
    //         target: d.molTo(b)
    //     }, e, function(a) {
    //         f(a.value)
    //     }, h)
    // };
    // q.isSubgraphIsomorphism = function(a, b, e, f, h) {
    //     this._contactServer("isSubgraphIsomorphism", {
    //         arrow: d.molTo(a),
    //         target: d.molTo(b)
    //     }, e, function(a) {
    //         f(a.value)
    //     }, h)
    // };
    // q.isSupergraphIsomorphism = function(a, b, e, f, h) {
    //     this._contactServer("isSupergraphIsomorphism", {
    //         arrow: d.molTo(a),
    //         target: d.molTo(b)
    //     }, e, function(a) {
    //         f(a.value)
    //     }, h)
    // };
    // q.getSimilarityMeasure = function(a, b, e, f, h) {
    //     this._contactServer("getSimilarityMeasure", {
    //         first: d.molTo(a),
    //         second: d.molTo(b)
    //     }, e, function(a) {
    //         f(a.value)
    //     }, h)
    // };
    // q.kekulize = function(a, b, e, f) {
    //     this._contactServer("kekulize", {
    //         mol: d.molTo(a)
    //     }, b, function(a) {
    //         e(d.molFrom(a.mol))
    //     }, f)
    // };
    // q.maximumCommonSubstructure =
    //     function(a, b, e, f, h) {
    //         this._contactServer("maximumCommonSubstructure", {
    //             m1: d.molTo(a),
    //             m2: d.molTo(b)
    //         }, e, function(a) {
    //             f(a.map)
    //         }, h)
    //     };
    // q.mechanismMatch = function(a, b, d, e, f) {
    //     this._contactServer("matchMechanism", {
    //         arrow: a,
    //         targets: b
    //     }, d, function(a) {
    //         e(a)
    //     }, f)
    // };
    // q.optimize = function(a, b, e, f) {
    //     this._contactServer("optimize", {
    //         mol: d.molTo(a)
    //     }, b, function(f) {
    //         f = d.molFrom(f.mol);
    //         if (2 === b.dimension) {
    //             for (let b = 0, d = f.atoms.length; b < d; b++) a.atoms[b].x = f.atoms[b].x, a.atoms[b].y = f.atoms[b].y;
    //             e()
    //         } else if (3 === b.dimension) {
    //             for (let a =
    //                     0, b = f.atoms.length; a < b; a++) f.atoms[a].x /= 20, f.atoms[a].y /= -20, f.atoms[a].z /= 20;
    //             e(f)
    //         }
    //     }, f)
    // };
    // q.readIUPACName = function(a, b, e, f) {
    //     this._contactServer("readIUPACName", {
    //         iupac: a
    //     }, b, function(a) {
    //         let b = [];
    //         for (let e = 0, f = a.mols.length; e < f; e++) b.push(d.molFrom(a.mols[e]));
    //         e(b, a.warning)
    //     }, f)
    // };
    // q.readSMILES = function(a, b, e, f) {
    //     this._contactServer("readSMILES", {
    //         smiles: a
    //     }, b, function(a) {
    //         e(d.molFrom(a.mol))
    //     }, f)
    // };
    // q.readWLN = function(a, b, e, f) {
    //     this._contactServer("readWLN", {
    //             wln: a
    //         }, b, function(a) {
    //             e(d.contentFrom(a.content))
    //         },
    //         f)
    // };
    // q.resolveCIP = function(a, b, e, f) {
    //     this._contactServer("resolveCIP", {
    //         mol: d.molTo(a)
    //     }, b, function(a) {
    //         e(a.atoms, a.bonds)
    //     }, f)
    // };
    // q.saveFile = function(a, b, e, f) {
    //     this._contactServer("saveFile", {
    //         mol: d.molTo(a)
    //     }, b, function(a) {
    //         e(a.link)
    //     }, f)
    // };
    // q.simulate13CNMR = function(a, b, e, h) {
    //     b.nucleus = "C";
    //     b.isotope = 13;
    //     this._contactServer("simulateNMR", {
    //         mol: d.molTo(a)
    //     }, b, function(a) {
    //         e(f.readJCAMP(a.jcamp))
    //     }, h)
    // };
    // q.simulate1HNMR = function(a, b, e, h) {
    //     b.nucleus = "H";
    //     b.isotope = 1;
    //     this._contactServer("simulateNMR", {
    //             mol: d.molTo(a)
    //         }, b, function(a) {
    //             e(f.readJCAMP(a.jcamp))
    //         },
    //         h)
    // };
    // q.simulateMassParentPeak = function(a, b, e, h) {
    //     this._contactServer("simulateMassParentPeak", {
    //         mol: d.molTo(a)
    //     }, b, function(a) {
    //         e(f.readJCAMP(a.jcamp))
    //     }, h)
    // };
    // q.writeSMILES = function(a, b, e, f) {
    //     this._contactServer("writeSMILES", {
    //         mol: d.molTo(a)
    //     }, b, function(a) {
    //         e(a.smiles)
    //     }, f)
    // };
    // q.version = function(a, b, d) {
    //     this._contactServer("version", {}, a, function(a) {
    //         b(a.value)
    //     }, d)
    // };
    // q.checkForUpdates = function(a) {
    //     this._contactServer("checkForUpdates", {
    //         value: k.href
    //     }, a, function(a) {}, function() {})
    // }
})(ChemDoodle, ChemDoodle.iChemLabs,
    ChemDoodle.io, ChemDoodle.structures, ChemDoodle.lib.jQuery, location);