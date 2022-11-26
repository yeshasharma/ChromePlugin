odoo.define('word.word', function (require) {
"use strict";

var core = require('web.core');
var Widget = require('web.Widget');
var AbstractAction = require('web.AbstractAction');
var ControlPanelMixin = require('web.ControlPanelMixin');
var QWeb = core.qweb;

var renderpdf = AbstractAction.extend(ControlPanelMixin, {
    template: "word_template",
    init: function() {
            this._super.apply(this,arguments);
            this.scale = 1.5;
    },

    start: function(){
            var self = this;
            console.log("In start");
            
           
            PDFJS.getDocument("/word/test_pdf/").then(function(pdf){
                self.load_pdf(pdf);
            });
            
    },
    
    load_pdf: function(pdf) {
            var self = this;
            
            this.container = document.getElementById("container");
            console.log("In div_creation"); 
            var text = $("#container");
            text.dblclick(function(e) {
                    var range = window.getSelection() || document.getSelection() || document.selection.createRange();
                    var word = $.trim(range.toString());
                    if(word != '') {
                        console.log(word);
                        self._rpc({
                            route: '/word/meaning',
                            params: {name: word},
                        }).then(function(result){
                             document.getElementById("result").innerHTML = QWeb.render('word_template', result)
                             /*console.log(self);*/
                        });
                        console.log("here",self);
                        /*ajax.jsonRpc("/word/word/meaning" + $("#result").val()).then(function(result)){
                           document.getElementById("result").innerHTML=word;
                        }*/
                    }
                    console.log(range);
                    range.collapse(null);
                    e.stopPropagation();
            });

            for (var i = 1; i <= pdf.numPages; i++) {
                
                pdf.getPage(i).then(function(page){
                    self.load_page(page);
                });
            }
    },

    load_page: function(page) {
            console.log("In load page");        
            var self = this;
            
            var viewport = page.getViewport(this.scale);
            var div = document.createElement("div");

            div.setAttribute("id", "page-" + (page.pageIndex + 1));
            div.setAttribute("style", "position: relative");
            this.container.appendChild(div);

            var canvas = document.createElement("canvas");
            div.appendChild(canvas);

            var context = canvas.getContext('2d');
            canvas.height = viewport.height;
            canvas.width = viewport.width;

            this.renderContext = {
              canvasContext: context,
              viewport: viewport
            };

            page.render(this.renderContext).then(function(){
                return page.getTextContent();
            }).then(function(textContent){
                self.div_creation(viewport, page, div, textContent);
            });
    },

    div_creation: function(viewport, page, div, textContent) {
            var textLayerDiv = document.createElement("div");
            textLayerDiv.setAttribute("class", "textLayer");
            
            div.appendChild(textLayerDiv);

            var textLayer = new TextLayerBuilder({
                textLayerDiv: textLayerDiv, 
                pageIndex: page.pageIndex,
                viewport: viewport
            });

            textLayer.setTextContent(textContent);

            textLayer.render();
            

    }, 
});
core.action_registry.add('word.pdf', renderpdf);
});
