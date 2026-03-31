function e(e,t,i,s){var n,r=arguments.length,o=r<3?t:null===s?s=Object.getOwnPropertyDescriptor(t,i):s;if("object"==typeof Reflect&&"function"==typeof Reflect.decorate)o=Reflect.decorate(e,t,i,s);else for(var a=e.length-1;a>=0;a--)(n=e[a])&&(o=(r<3?n(o):r>3?n(t,i,o):n(t,i))||o);return r>3&&o&&Object.defineProperty(t,i,o),o}"function"==typeof SuppressedError&&SuppressedError;const t=globalThis,i=t.ShadowRoot&&(void 0===t.ShadyCSS||t.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,s=Symbol(),n=new WeakMap;let r=class{constructor(e,t,i){if(this._$cssResult$=!0,i!==s)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=e,this.t=t}get styleSheet(){let e=this.o;const t=this.t;if(i&&void 0===e){const i=void 0!==t&&1===t.length;i&&(e=n.get(t)),void 0===e&&((this.o=e=new CSSStyleSheet).replaceSync(this.cssText),i&&n.set(t,e))}return e}toString(){return this.cssText}};const o=(e,...t)=>{const i=1===e.length?e[0]:t.reduce((t,i,s)=>t+(e=>{if(!0===e._$cssResult$)return e.cssText;if("number"==typeof e)return e;throw Error("Value passed to 'css' function must be a 'css' function result: "+e+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(i)+e[s+1],e[0]);return new r(i,e,s)},a=i?e=>e:e=>e instanceof CSSStyleSheet?(e=>{let t="";for(const i of e.cssRules)t+=i.cssText;return(e=>new r("string"==typeof e?e:e+"",void 0,s))(t)})(e):e,{is:l,defineProperty:h,getOwnPropertyDescriptor:c,getOwnPropertyNames:d,getOwnPropertySymbols:p,getPrototypeOf:u}=Object,_=globalThis,f=_.trustedTypes,g=f?f.emptyScript:"",m=_.reactiveElementPolyfillSupport,y=(e,t)=>e,v={toAttribute(e,t){switch(t){case Boolean:e=e?g:null;break;case Object:case Array:e=null==e?e:JSON.stringify(e)}return e},fromAttribute(e,t){let i=e;switch(t){case Boolean:i=null!==e;break;case Number:i=null===e?null:Number(e);break;case Object:case Array:try{i=JSON.parse(e)}catch(e){i=null}}return i}},$=(e,t)=>!l(e,t),b={attribute:!0,type:String,converter:v,reflect:!1,useDefault:!1,hasChanged:$};Symbol.metadata??=Symbol("metadata"),_.litPropertyMetadata??=new WeakMap;let x=class extends HTMLElement{static addInitializer(e){this._$Ei(),(this.l??=[]).push(e)}static get observedAttributes(){return this.finalize(),this._$Eh&&[...this._$Eh.keys()]}static createProperty(e,t=b){if(t.state&&(t.attribute=!1),this._$Ei(),this.prototype.hasOwnProperty(e)&&((t=Object.create(t)).wrapped=!0),this.elementProperties.set(e,t),!t.noAccessor){const i=Symbol(),s=this.getPropertyDescriptor(e,i,t);void 0!==s&&h(this.prototype,e,s)}}static getPropertyDescriptor(e,t,i){const{get:s,set:n}=c(this.prototype,e)??{get(){return this[t]},set(e){this[t]=e}};return{get:s,set(t){const r=s?.call(this);n?.call(this,t),this.requestUpdate(e,r,i)},configurable:!0,enumerable:!0}}static getPropertyOptions(e){return this.elementProperties.get(e)??b}static _$Ei(){if(this.hasOwnProperty(y("elementProperties")))return;const e=u(this);e.finalize(),void 0!==e.l&&(this.l=[...e.l]),this.elementProperties=new Map(e.elementProperties)}static finalize(){if(this.hasOwnProperty(y("finalized")))return;if(this.finalized=!0,this._$Ei(),this.hasOwnProperty(y("properties"))){const e=this.properties,t=[...d(e),...p(e)];for(const i of t)this.createProperty(i,e[i])}const e=this[Symbol.metadata];if(null!==e){const t=litPropertyMetadata.get(e);if(void 0!==t)for(const[e,i]of t)this.elementProperties.set(e,i)}this._$Eh=new Map;for(const[e,t]of this.elementProperties){const i=this._$Eu(e,t);void 0!==i&&this._$Eh.set(i,e)}this.elementStyles=this.finalizeStyles(this.styles)}static finalizeStyles(e){const t=[];if(Array.isArray(e)){const i=new Set(e.flat(1/0).reverse());for(const e of i)t.unshift(a(e))}else void 0!==e&&t.push(a(e));return t}static _$Eu(e,t){const i=t.attribute;return!1===i?void 0:"string"==typeof i?i:"string"==typeof e?e.toLowerCase():void 0}constructor(){super(),this._$Ep=void 0,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Em=null,this._$Ev()}_$Ev(){this._$ES=new Promise(e=>this.enableUpdating=e),this._$AL=new Map,this._$E_(),this.requestUpdate(),this.constructor.l?.forEach(e=>e(this))}addController(e){(this._$EO??=new Set).add(e),void 0!==this.renderRoot&&this.isConnected&&e.hostConnected?.()}removeController(e){this._$EO?.delete(e)}_$E_(){const e=new Map,t=this.constructor.elementProperties;for(const i of t.keys())this.hasOwnProperty(i)&&(e.set(i,this[i]),delete this[i]);e.size>0&&(this._$Ep=e)}createRenderRoot(){const e=this.shadowRoot??this.attachShadow(this.constructor.shadowRootOptions);return((e,s)=>{if(i)e.adoptedStyleSheets=s.map(e=>e instanceof CSSStyleSheet?e:e.styleSheet);else for(const i of s){const s=document.createElement("style"),n=t.litNonce;void 0!==n&&s.setAttribute("nonce",n),s.textContent=i.cssText,e.appendChild(s)}})(e,this.constructor.elementStyles),e}connectedCallback(){this.renderRoot??=this.createRenderRoot(),this.enableUpdating(!0),this._$EO?.forEach(e=>e.hostConnected?.())}enableUpdating(e){}disconnectedCallback(){this._$EO?.forEach(e=>e.hostDisconnected?.())}attributeChangedCallback(e,t,i){this._$AK(e,i)}_$ET(e,t){const i=this.constructor.elementProperties.get(e),s=this.constructor._$Eu(e,i);if(void 0!==s&&!0===i.reflect){const n=(void 0!==i.converter?.toAttribute?i.converter:v).toAttribute(t,i.type);this._$Em=e,null==n?this.removeAttribute(s):this.setAttribute(s,n),this._$Em=null}}_$AK(e,t){const i=this.constructor,s=i._$Eh.get(e);if(void 0!==s&&this._$Em!==s){const e=i.getPropertyOptions(s),n="function"==typeof e.converter?{fromAttribute:e.converter}:void 0!==e.converter?.fromAttribute?e.converter:v;this._$Em=s;const r=n.fromAttribute(t,e.type);this[s]=r??this._$Ej?.get(s)??r,this._$Em=null}}requestUpdate(e,t,i,s=!1,n){if(void 0!==e){const r=this.constructor;if(!1===s&&(n=this[e]),i??=r.getPropertyOptions(e),!((i.hasChanged??$)(n,t)||i.useDefault&&i.reflect&&n===this._$Ej?.get(e)&&!this.hasAttribute(r._$Eu(e,i))))return;this.C(e,t,i)}!1===this.isUpdatePending&&(this._$ES=this._$EP())}C(e,t,{useDefault:i,reflect:s,wrapped:n},r){i&&!(this._$Ej??=new Map).has(e)&&(this._$Ej.set(e,r??t??this[e]),!0!==n||void 0!==r)||(this._$AL.has(e)||(this.hasUpdated||i||(t=void 0),this._$AL.set(e,t)),!0===s&&this._$Em!==e&&(this._$Eq??=new Set).add(e))}async _$EP(){this.isUpdatePending=!0;try{await this._$ES}catch(e){Promise.reject(e)}const e=this.scheduleUpdate();return null!=e&&await e,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){if(!this.isUpdatePending)return;if(!this.hasUpdated){if(this.renderRoot??=this.createRenderRoot(),this._$Ep){for(const[e,t]of this._$Ep)this[e]=t;this._$Ep=void 0}const e=this.constructor.elementProperties;if(e.size>0)for(const[t,i]of e){const{wrapped:e}=i,s=this[t];!0!==e||this._$AL.has(t)||void 0===s||this.C(t,void 0,i,s)}}let e=!1;const t=this._$AL;try{e=this.shouldUpdate(t),e?(this.willUpdate(t),this._$EO?.forEach(e=>e.hostUpdate?.()),this.update(t)):this._$EM()}catch(t){throw e=!1,this._$EM(),t}e&&this._$AE(t)}willUpdate(e){}_$AE(e){this._$EO?.forEach(e=>e.hostUpdated?.()),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(e)),this.updated(e)}_$EM(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$ES}shouldUpdate(e){return!0}update(e){this._$Eq&&=this._$Eq.forEach(e=>this._$ET(e,this[e])),this._$EM()}updated(e){}firstUpdated(e){}};x.elementStyles=[],x.shadowRootOptions={mode:"open"},x[y("elementProperties")]=new Map,x[y("finalized")]=new Map,m?.({ReactiveElement:x}),(_.reactiveElementVersions??=[]).push("2.1.2");const w=globalThis,P=e=>e,S=w.trustedTypes,k=S?S.createPolicy("lit-html",{createHTML:e=>e}):void 0,E="$lit$",A=`lit$${Math.random().toFixed(9).slice(2)}$`,M="?"+A,C=`<${M}>`,T=document,z=()=>T.createComment(""),I=e=>null===e||"object"!=typeof e&&"function"!=typeof e,R=Array.isArray,O="[ \t\n\f\r]",D=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,L=/-->/g,H=/>/g,U=RegExp(`>|${O}(?:([^\\s"'>=/]+)(${O}*=${O}*(?:[^ \t\n\f\r"'\`<>=]|("|')|))|$)`,"g"),N=/'/g,V=/"/g,j=/^(?:script|style|textarea|title)$/i,B=e=>(t,...i)=>({_$litType$:e,strings:t,values:i}),q=B(1),F=B(2),W=Symbol.for("lit-noChange"),J=Symbol.for("lit-nothing"),Y=new WeakMap,Z=T.createTreeWalker(T,129);function X(e,t){if(!R(e)||!e.hasOwnProperty("raw"))throw Error("invalid template strings array");return void 0!==k?k.createHTML(t):t}const G=(e,t)=>{const i=e.length-1,s=[];let n,r=2===t?"<svg>":3===t?"<math>":"",o=D;for(let t=0;t<i;t++){const i=e[t];let a,l,h=-1,c=0;for(;c<i.length&&(o.lastIndex=c,l=o.exec(i),null!==l);)c=o.lastIndex,o===D?"!--"===l[1]?o=L:void 0!==l[1]?o=H:void 0!==l[2]?(j.test(l[2])&&(n=RegExp("</"+l[2],"g")),o=U):void 0!==l[3]&&(o=U):o===U?">"===l[0]?(o=n??D,h=-1):void 0===l[1]?h=-2:(h=o.lastIndex-l[2].length,a=l[1],o=void 0===l[3]?U:'"'===l[3]?V:N):o===V||o===N?o=U:o===L||o===H?o=D:(o=U,n=void 0);const d=o===U&&e[t+1].startsWith("/>")?" ":"";r+=o===D?i+C:h>=0?(s.push(a),i.slice(0,h)+E+i.slice(h)+A+d):i+A+(-2===h?t:d)}return[X(e,r+(e[i]||"<?>")+(2===t?"</svg>":3===t?"</math>":"")),s]};class K{constructor({strings:e,_$litType$:t},i){let s;this.parts=[];let n=0,r=0;const o=e.length-1,a=this.parts,[l,h]=G(e,t);if(this.el=K.createElement(l,i),Z.currentNode=this.el.content,2===t||3===t){const e=this.el.content.firstChild;e.replaceWith(...e.childNodes)}for(;null!==(s=Z.nextNode())&&a.length<o;){if(1===s.nodeType){if(s.hasAttributes())for(const e of s.getAttributeNames())if(e.endsWith(E)){const t=h[r++],i=s.getAttribute(e).split(A),o=/([.?@])?(.*)/.exec(t);a.push({type:1,index:n,name:o[2],strings:i,ctor:"."===o[1]?se:"?"===o[1]?ne:"@"===o[1]?re:ie}),s.removeAttribute(e)}else e.startsWith(A)&&(a.push({type:6,index:n}),s.removeAttribute(e));if(j.test(s.tagName)){const e=s.textContent.split(A),t=e.length-1;if(t>0){s.textContent=S?S.emptyScript:"";for(let i=0;i<t;i++)s.append(e[i],z()),Z.nextNode(),a.push({type:2,index:++n});s.append(e[t],z())}}}else if(8===s.nodeType)if(s.data===M)a.push({type:2,index:n});else{let e=-1;for(;-1!==(e=s.data.indexOf(A,e+1));)a.push({type:7,index:n}),e+=A.length-1}n++}}static createElement(e,t){const i=T.createElement("template");return i.innerHTML=e,i}}function Q(e,t,i=e,s){if(t===W)return t;let n=void 0!==s?i._$Co?.[s]:i._$Cl;const r=I(t)?void 0:t._$litDirective$;return n?.constructor!==r&&(n?._$AO?.(!1),void 0===r?n=void 0:(n=new r(e),n._$AT(e,i,s)),void 0!==s?(i._$Co??=[])[s]=n:i._$Cl=n),void 0!==n&&(t=Q(e,n._$AS(e,t.values),n,s)),t}class ee{constructor(e,t){this._$AV=[],this._$AN=void 0,this._$AD=e,this._$AM=t}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(e){const{el:{content:t},parts:i}=this._$AD,s=(e?.creationScope??T).importNode(t,!0);Z.currentNode=s;let n=Z.nextNode(),r=0,o=0,a=i[0];for(;void 0!==a;){if(r===a.index){let t;2===a.type?t=new te(n,n.nextSibling,this,e):1===a.type?t=new a.ctor(n,a.name,a.strings,this,e):6===a.type&&(t=new oe(n,this,e)),this._$AV.push(t),a=i[++o]}r!==a?.index&&(n=Z.nextNode(),r++)}return Z.currentNode=T,s}p(e){let t=0;for(const i of this._$AV)void 0!==i&&(void 0!==i.strings?(i._$AI(e,i,t),t+=i.strings.length-2):i._$AI(e[t])),t++}}class te{get _$AU(){return this._$AM?._$AU??this._$Cv}constructor(e,t,i,s){this.type=2,this._$AH=J,this._$AN=void 0,this._$AA=e,this._$AB=t,this._$AM=i,this.options=s,this._$Cv=s?.isConnected??!0}get parentNode(){let e=this._$AA.parentNode;const t=this._$AM;return void 0!==t&&11===e?.nodeType&&(e=t.parentNode),e}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(e,t=this){e=Q(this,e,t),I(e)?e===J||null==e||""===e?(this._$AH!==J&&this._$AR(),this._$AH=J):e!==this._$AH&&e!==W&&this._(e):void 0!==e._$litType$?this.$(e):void 0!==e.nodeType?this.T(e):(e=>R(e)||"function"==typeof e?.[Symbol.iterator])(e)?this.k(e):this._(e)}O(e){return this._$AA.parentNode.insertBefore(e,this._$AB)}T(e){this._$AH!==e&&(this._$AR(),this._$AH=this.O(e))}_(e){this._$AH!==J&&I(this._$AH)?this._$AA.nextSibling.data=e:this.T(T.createTextNode(e)),this._$AH=e}$(e){const{values:t,_$litType$:i}=e,s="number"==typeof i?this._$AC(e):(void 0===i.el&&(i.el=K.createElement(X(i.h,i.h[0]),this.options)),i);if(this._$AH?._$AD===s)this._$AH.p(t);else{const e=new ee(s,this),i=e.u(this.options);e.p(t),this.T(i),this._$AH=e}}_$AC(e){let t=Y.get(e.strings);return void 0===t&&Y.set(e.strings,t=new K(e)),t}k(e){R(this._$AH)||(this._$AH=[],this._$AR());const t=this._$AH;let i,s=0;for(const n of e)s===t.length?t.push(i=new te(this.O(z()),this.O(z()),this,this.options)):i=t[s],i._$AI(n),s++;s<t.length&&(this._$AR(i&&i._$AB.nextSibling,s),t.length=s)}_$AR(e=this._$AA.nextSibling,t){for(this._$AP?.(!1,!0,t);e!==this._$AB;){const t=P(e).nextSibling;P(e).remove(),e=t}}setConnected(e){void 0===this._$AM&&(this._$Cv=e,this._$AP?.(e))}}class ie{get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}constructor(e,t,i,s,n){this.type=1,this._$AH=J,this._$AN=void 0,this.element=e,this.name=t,this._$AM=s,this.options=n,i.length>2||""!==i[0]||""!==i[1]?(this._$AH=Array(i.length-1).fill(new String),this.strings=i):this._$AH=J}_$AI(e,t=this,i,s){const n=this.strings;let r=!1;if(void 0===n)e=Q(this,e,t,0),r=!I(e)||e!==this._$AH&&e!==W,r&&(this._$AH=e);else{const s=e;let o,a;for(e=n[0],o=0;o<n.length-1;o++)a=Q(this,s[i+o],t,o),a===W&&(a=this._$AH[o]),r||=!I(a)||a!==this._$AH[o],a===J?e=J:e!==J&&(e+=(a??"")+n[o+1]),this._$AH[o]=a}r&&!s&&this.j(e)}j(e){e===J?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,e??"")}}class se extends ie{constructor(){super(...arguments),this.type=3}j(e){this.element[this.name]=e===J?void 0:e}}class ne extends ie{constructor(){super(...arguments),this.type=4}j(e){this.element.toggleAttribute(this.name,!!e&&e!==J)}}class re extends ie{constructor(e,t,i,s,n){super(e,t,i,s,n),this.type=5}_$AI(e,t=this){if((e=Q(this,e,t,0)??J)===W)return;const i=this._$AH,s=e===J&&i!==J||e.capture!==i.capture||e.once!==i.once||e.passive!==i.passive,n=e!==J&&(i===J||s);s&&this.element.removeEventListener(this.name,this,i),n&&this.element.addEventListener(this.name,this,e),this._$AH=e}handleEvent(e){"function"==typeof this._$AH?this._$AH.call(this.options?.host??this.element,e):this._$AH.handleEvent(e)}}class oe{constructor(e,t,i){this.element=e,this.type=6,this._$AN=void 0,this._$AM=t,this.options=i}get _$AU(){return this._$AM._$AU}_$AI(e){Q(this,e)}}const ae=w.litHtmlPolyfillSupport;ae?.(K,te),(w.litHtmlVersions??=[]).push("3.3.2");const le=globalThis;class he extends x{constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){const e=super.createRenderRoot();return this.renderOptions.renderBefore??=e.firstChild,e}update(e){const t=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(e),this._$Do=((e,t,i)=>{const s=i?.renderBefore??t;let n=s._$litPart$;if(void 0===n){const e=i?.renderBefore??null;s._$litPart$=n=new te(t.insertBefore(z(),e),e,void 0,i??{})}return n._$AI(e),n})(t,this.renderRoot,this.renderOptions)}connectedCallback(){super.connectedCallback(),this._$Do?.setConnected(!0)}disconnectedCallback(){super.disconnectedCallback(),this._$Do?.setConnected(!1)}render(){return W}}he._$litElement$=!0,he.finalized=!0,le.litElementHydrateSupport?.({LitElement:he});const ce=le.litElementPolyfillSupport;ce?.({LitElement:he}),(le.litElementVersions??=[]).push("4.2.2");const de={attribute:!0,type:String,converter:v,reflect:!1,hasChanged:$},pe=(e=de,t,i)=>{const{kind:s,metadata:n}=i;let r=globalThis.litPropertyMetadata.get(n);if(void 0===r&&globalThis.litPropertyMetadata.set(n,r=new Map),"setter"===s&&((e=Object.create(e)).wrapped=!0),r.set(i.name,e),"accessor"===s){const{name:s}=i;return{set(i){const n=t.get.call(this);t.set.call(this,i),this.requestUpdate(s,n,e,!0,i)},init(t){return void 0!==t&&this.C(s,void 0,e,t),t}}}if("setter"===s){const{name:s}=i;return function(i){const n=this[s];t.call(this,i),this.requestUpdate(s,n,e,!0,i)}}throw Error("Unsupported decorator location: "+s)};function ue(e){return(t,i)=>"object"==typeof i?pe(e,t,i):((e,t,i)=>{const s=t.hasOwnProperty(i);return t.constructor.createProperty(i,e),s?Object.getOwnPropertyDescriptor(t,i):void 0})(e,t,i)}function _e(e){return ue({...e,state:!0,attribute:!1})}function fe(e){if(!e||e.length<2)return{h:"l",v:"t"};return{h:"m"===e[0]||"r"===e[0]?e[0]:"l",v:"atmsd".includes(e[1])?e[1]:"t"}}const ge={"rbm.ttf":"RobotoMedium","ppb.ttf":"PoppinsBold","DejaVuSans.ttf":"DejaVuSans"},me={"rbm.ttf":"500","ppb.ttf":"700","DejaVuSans.ttf":"normal"};function ye(e){return{family:`${ge[e??""]??"RobotoMedium"}, sans-serif`,weight:me[e??""]??"500"}}let ve=null;function $e(e,t,i){ve||(ve=document.createElement("canvas"));const s=ve.getContext("2d");if(!s)return.6*t*e.length;const{family:n,weight:r}=ye(i);return s.font=`${r} ${t}px ${n}`,s.measureText(e).width}function be(e,t){ve||(ve=document.createElement("canvas"));const i=ve.getContext("2d");if(!i)return{ascent:.8*e,descent:.2*e};const{family:s,weight:n}=ye(t);i.font=`${n} ${e}px ${s}`;const r=i.measureText("M");return{ascent:r.fontBoundingBoxAscent??.8*e,descent:r.fontBoundingBoxDescent??.2*e}}function xe(e){switch(e.type){case"text":case"multiline":{const t=e.size??20,i=e.font;let s;if("multiline"===e.type){const n=e.delimiter??"\n",r=(e.value||"").split(n);s=Math.max(...r.map(e=>$e(e,t,i)),t)}else s=Math.max($e(e.value||"",t,i),t);const{h:n,v:r}=fe(e.anchor);let o=e.x;"m"===n?o=e.x-s/2:"r"===n&&(o=e.x-s);let a=e.y,l=t;if("multiline"===e.type){const i=(e.value||"").split(e.delimiter??"\n").length;l=t+(i-1)*t*1.2}if("m"===r)a=e.y-l/2;else if("s"===r){const s=be(t,i);a=e.y-s.ascent,l=s.ascent+s.descent}else"d"===r&&(a=e.y-l);return{x:o,y:a,width:s,height:l}}case"icon":{const t=e.size??24;return{x:e.x,y:e.y,width:t,height:t}}case"rectangle":case"ellipse":case"progress_bar":return{x:e.x_start,y:e.y_start,width:e.x_end-e.x_start,height:e.y_end-e.y_start};case"line":return{x:Math.min(e.x_start,e.x_end),y:Math.min(e.y_start,e.y_end),width:Math.abs(e.x_end-e.x_start)||2,height:Math.abs(e.y_end-e.y_start)||2};case"circle":{const t=e.radius??10;return{x:e.x-t,y:e.y-t,width:2*t,height:2*t}}case"dlimg":return{x:e.x,y:e.y,width:e.xsize??48,height:e.ysize??48};case"qrcode":{const t=e.size??48;return{x:e.x,y:e.y,width:t,height:t}}default:return{x:0,y:0,width:24,height:24}}}function we(e,t,i){switch(e.type){case"text":case"multiline":{const s=e.size??20,n=e.font;let r;if("multiline"===e.type){const t=e.delimiter??"\n",i=(e.value||"").split(t);r=Math.max(...i.map(e=>$e(e,s,n)),s)}else r=Math.max($e(e.value||"",s,n),s);const{h:o,v:a}=fe(e.anchor);if(e.x="m"===o?Math.round(t+r/2):"r"===o?Math.round(t+r):Math.round(t),"m"===a){let t=s;if("multiline"===e.type){const i=(e.value||"").split(e.delimiter??"\n").length;t=s+(i-1)*s*1.2}e.y=Math.round(i+t/2)}else if("s"===a){const t=be(s,n);e.y=Math.round(i+t.ascent)}else if("d"===a){let t=s;if("multiline"===e.type){const i=(e.value||"").split(e.delimiter??"\n").length;t=s+(i-1)*s*1.2}e.y=Math.round(i+t)}else e.y=Math.round(i);break}case"icon":case"dlimg":case"qrcode":e.x=Math.round(t),e.y=Math.round(i);break;case"circle":e.x=Math.round(t+(e.radius??10)),e.y=Math.round(i+(e.radius??10));break;case"rectangle":case"ellipse":case"progress_bar":{const s=e.x_end-e.x_start,n=e.y_end-e.y_start;e.x_start=Math.round(t),e.y_start=Math.round(i),e.x_end=Math.round(t+s),e.y_end=Math.round(i+n);break}case"line":{const s=t-Math.min(e.x_start,e.x_end),n=i-Math.min(e.y_start,e.y_end);e.x_start=Math.round(e.x_start+s),e.y_start=Math.round(e.y_start+n),e.x_end=Math.round(e.x_end+s),e.y_end=Math.round(e.y_end+n);break}}}const Pe={black:"#000000",white:"#ffffff",red:"#ff0000",yellow:"#ffcc00"};function Se(e,t="#000000"){return e?Pe[e.toLowerCase()]??e:t}const ke={"rbm.ttf":"RobotoMedium","ppb.ttf":"PoppinsBold","DejaVuSans.ttf":"DejaVuSans"},Ee={"rbm.ttf":"500","ppb.ttf":"700","DejaVuSans.ttf":"normal"};function Ae(e){if(!e)return"RobotoMedium, sans-serif";const t=ke[e];return t?`${t}, sans-serif`:"RobotoMedium, sans-serif"}function Me(e){return e?Ee[e]??"500":"500"}function Ce(e,t,i,s){const n=xe(e),r=function(e,t){switch(e.type){case"text":return function(e){const t=e.size??20,i=Se(e.color),{textAnchor:s,baseline:n}=Te(e.anchor);let r=e.y;e.anchor&&"t"===fe(e.anchor).v&&(r=e.y-Ie(t,e.font));return F`
    <text
      x="${e.x}" y="${r}"
      font-size="${t}"
      font-weight="${Me(e.font)}"
      fill="${i}"
      font-family="${Ae(e.font)}"
      dominant-baseline="${n}"
      text-anchor="${s}"
      letter-spacing="${(.02*t).toFixed(2)}"
    >${e.value||""}</text>
  `}(e);case"multiline":return function(e){const t=e.size??20,i=Se(e.color),s=e.delimiter??"\n",n=(e.value||"").split(s),r=1.2*t,{textAnchor:o,baseline:a}=Te(e.anchor);let l=e.y;e.anchor&&"t"===fe(e.anchor).v&&(l=e.y-Ie(t,e.font));return F`
    <text
      x="${e.x}" y="${l}"
      font-size="${t}"
      font-weight="${Me(e.font)}"
      fill="${i}"
      font-family="${Ae(e.font)}"
      dominant-baseline="${a}"
      text-anchor="${o}"
      letter-spacing="${(.02*t).toFixed(2)}"
    >
      ${n.map((t,i)=>F`
          <tspan x="${e.x}" dy="${0===i?0:r}">${t}</tspan>
        `)}
    </text>
  `}(e);case"rectangle":return function(e){return F`
    <rect
      x="${e.x_start}" y="${e.y_start}"
      width="${e.x_end-e.x_start}" height="${e.y_end-e.y_start}"
      fill="${e.fill?Se(e.fill):"none"}"
      stroke="${e.outline?Se(e.outline):"none"}"
      stroke-width="${e.width??1}"
    />
  `}(e);case"line":return function(e){return F`
    <line
      x1="${e.x_start}" y1="${e.y_start}"
      x2="${e.x_end}" y2="${e.y_end}"
      stroke="${Se(e.fill)}"
      stroke-width="${e.width??1}"
    />
  `}(e);case"icon":return function(e,t){const i=e.size??24,s=Se(e.color),n=(e.value||"").replace(/^mdi:/,""),r=t?.get(n);if(r)return F`
      <text x="${e.x}" y="${e.y}"
        font-size="${i}"
        fill="${s}"
        font-family="MaterialDesignIcons"
        dominant-baseline="text-before-edge"
      >${r}</text>
    `;return F`
    <rect x="${e.x}" y="${e.y}" width="${i}" height="${i}"
      fill="none" stroke="${s}" stroke-width="1" stroke-dasharray="2,2" />
    <text x="${e.x+i/2}" y="${e.y+i/2}"
      font-size="${Math.min(.35*i,10)}"
      fill="${s}" text-anchor="middle" dominant-baseline="central"
      font-family="RobotoMedium, sans-serif"
    >${n.length>12?n.slice(0,12)+"…":n}</text>
  `}(e,t);case"dlimg":return function(e){const t=e.xsize??48,i=e.ysize??48,s=e.url;if(s)return F`
      <image href="${s}" x="${e.x}" y="${e.y}" width="${t}" height="${i}"
        preserveAspectRatio="none" />
    `;return F`
    <rect x="${e.x}" y="${e.y}" width="${t}" height="${i}"
      fill="#eee" stroke="#999" stroke-width="1" />
    <text x="${e.x+t/2}" y="${e.y+i/2}"
      font-size="10" fill="#999" text-anchor="middle" dominant-baseline="central"
      font-family="RobotoMedium, sans-serif">IMG</text>
  `}(e);case"circle":return function(e){const t=e.radius??10;return F`
    <circle cx="${e.x}" cy="${e.y}" r="${t}"
      fill="${e.fill?Se(e.fill):"none"}"
      stroke="${e.outline?Se(e.outline):"none"}"
      stroke-width="${e.width??1}"
    />
  `}(e);case"ellipse":return function(e){const t=(e.x_start+e.x_end)/2,i=(e.y_start+e.y_end)/2,s=(e.x_end-e.x_start)/2,n=(e.y_end-e.y_start)/2;return F`
    <ellipse cx="${t}" cy="${i}" rx="${s}" ry="${n}"
      fill="${e.fill?Se(e.fill):"none"}"
      stroke="${e.outline?Se(e.outline):"none"}"
      stroke-width="${e.width??1}"
    />
  `}(e);case"qrcode":return function(e){const t=e.size??48;return F`
    <rect x="${e.x}" y="${e.y}" width="${t}" height="${t}"
      fill="#fff" stroke="#000" stroke-width="1" />
    <text x="${e.x+t/2}" y="${e.y+t/2}"
      font-size="${Math.min(.25*t,10)}"
      fill="#000" text-anchor="middle" dominant-baseline="central"
      font-family="RobotoMedium, sans-serif">QR</text>
  `}(e);case"progress_bar":return function(e){const t=e.x_end-e.x_start,i=e.y_end-e.y_start,s=Math.max(0,Math.min(100,e.progress??0)),n=t*s/100;return F`
    <rect x="${e.x_start}" y="${e.y_start}" width="${t}" height="${i}"
      fill="none" stroke="${e.outline?Se(e.outline):"#000"}"
      stroke-width="${e.width??1}" />
    <rect x="${e.x_start}" y="${e.y_start}" width="${n}" height="${i}"
      fill="${Se(e.fill,"#000")}" />
  `}(e);default:return F``}}(e,s);return F`
    <g class="element-group" data-index="${t}">
      <!-- invisible hit area for pointer events -->
      <rect class="hit-area"
        x="${n.x}" y="${n.y}"
        width="${Math.max(n.width,8)}" height="${Math.max(n.height,8)}"
        fill="transparent" stroke="none" />
      ${r}
      ${i?function(e){const{x:t,y:i,width:s,height:n}=e,r=4;return F`
    <rect x="${t-1}" y="${i-1}" width="${s+2}" height="${n+2}"
      fill="none" stroke="#2196F3" stroke-width="1" stroke-dasharray="3,2" />
    <!-- corner handles -->
    <rect class="handle nw" x="${t-r}" y="${i-r}" width="${2*r}" height="${2*r}" fill="#2196F3" />
    <rect class="handle ne" x="${t+s-r}" y="${i-r}" width="${2*r}" height="${2*r}" fill="#2196F3" />
    <rect class="handle sw" x="${t-r}" y="${i+n-r}" width="${2*r}" height="${2*r}" fill="#2196F3" />
    <rect class="handle se" x="${t+s-r}" y="${i+n-r}" width="${2*r}" height="${2*r}" fill="#2196F3" />
  `}(n):J}
    </g>
  `}function Te(e){const{h:t,v:i}=fe(e);return{textAnchor:"m"===t?"middle":"r"===t?"end":"start",baseline:"m"===i?"central":"s"===i?"auto":"d"===i?"text-after-edge":"text-before-edge"}}let ze=null;function Ie(e,t){ze||(ze=document.createElement("canvas"));const i=ze.getContext("2d");if(!i)return 0;i.font=`${Me(t)} ${e}px ${Ae(t)}`;const s=i.measureText("M"),n=s.fontBoundingBoxAscent,r=s.actualBoundingBoxAscent;return null==n||null==r?0:Math.max(0,n-r)}function Re(e){return JSON.parse(JSON.stringify(e))}class Oe extends he{constructor(){super(...arguments),this._profiles=[],this._activeProfileOptions=[],this._activeProfileId="",this._profileData=[],this._computeLabel=e=>({profile_subentry_id:"Edit Profile",entity:"Display Entity (image.*)",service:"Drawcustom Service (e.g. wolink_esl.drawcustom)",width:"Width (px)",height:"Height (px)",background:"Background",rotate:"Rotation",dither:"Dither"}[e.name]??e.name)}setConfig(e){this._config={...e}}connectedCallback(){super.connectedCallback(),this._fetchProfiles()}async _fetchProfiles(){if(this.hass||(await new Promise(e=>setTimeout(e,300)),this.hass))try{const e=await this.hass.callWS({type:"eink_display_manager/list_profiles"});this._profileData=(e.profiles||[]).map(e=>({subentry_id:e.subentry_id,enabled:!1!==e.enabled,entity_id:e.entity_id||""})),this._profiles=[{value:"",label:"None (standalone)"},...(e.profiles||[]).map(e=>({value:e.subentry_id,label:!1===e.enabled?`${e.title} (inactive)`:e.title}))],this._updateActiveProfileOptions()}catch{}}_updateActiveProfileOptions(){const e=this._config?.entity;if(!e)return this._activeProfileOptions=[],void(this._activeProfileId="");const t=this._profileData.filter(t=>t.entity_id===e);this._activeProfileOptions=t.map(e=>{const t=this._profiles.find(t=>t.value===e.subentry_id);return{value:e.subentry_id,label:t?.label??e.subentry_id}});const i=t.find(e=>e.enabled);this._activeProfileId=i?.subentry_id??""}_getProfileSchema(){return[{name:"profile_subentry_id",selector:{select:{mode:"dropdown",options:this._profiles.length>0?this._profiles:[{value:"",label:"None (standalone)"}]}}}]}_getSchema(){return[{name:"entity",selector:{entity:{filter:{domain:"image"}}}},{name:"service",selector:{text:{}}},{type:"grid",schema:[{name:"width",selector:{number:{min:1,max:1024,mode:"box"}}},{name:"height",selector:{number:{min:1,max:1024,mode:"box"}}}]},{type:"grid",schema:[{name:"background",selector:{select:{options:[{value:"white",label:"White"},{value:"black",label:"Black"},{value:"red",label:"Red"},{value:"yellow",label:"Yellow"}]}}},{name:"rotate",selector:{select:{options:[{value:0,label:"0°"},{value:90,label:"90°"},{value:180,label:"180°"},{value:270,label:"270°"}]}}},{name:"dither",selector:{select:{options:[{value:"floyd-steinberg",label:"Floyd-Steinberg"},{value:"atkinson",label:"Atkinson"},{value:"stucki",label:"Stucki"},{value:"none",label:"None"}]}}}]}]}render(){return this.hass&&this._config?q`
      <p class="section-heading">Edit profile in this card</p>
      <p class="section-desc">Select which profile to load and edit in this card. This only affects this card.</p>
      <ha-form
        .hass=${this.hass}
        .data=${this._config}
        .schema=${this._getProfileSchema()}
        .computeLabel=${this._computeLabel}
        @value-changed=${this._valueChanged}
      ></ha-form>

      ${this._activeProfileOptions.length>0?q`
        <p class="section-heading">Active profile for display</p>
        <p class="section-desc">The active profile is sent to the display on schedule. Only one per display.</p>
        <div class="active-profile-select">
          <ha-select
            .options=${this._activeProfileOptions}
            .value=${this._activeProfileId}
            @selected=${this._onActiveProfileChanged}
            @closed=${e=>e.stopPropagation()}>
          </ha-select>
        </div>
      `:J}

      <ha-form
        .hass=${this.hass}
        .data=${this._config}
        .schema=${this._getSchema()}
        .computeLabel=${this._computeLabel}
        @value-changed=${this._valueChanged}
      ></ha-form>
    `:q``}_valueChanged(e){if(e.stopPropagation(),!this._config)return;const t={...this._config,...e.detail.value};t.profile_subentry_id||delete t.profile_subentry_id,this._config=t,this._updateActiveProfileOptions();const i=new Event("config-changed",{bubbles:!0,composed:!0});i.detail={config:t},this.dispatchEvent(i)}async _onActiveProfileChanged(e){const t=e.detail?.value??e.target.value;if(t&&t!==this._activeProfileId&&this.hass)try{await this.hass.callWS({type:"eink_display_manager/activate_profile",subentry_id:t}),await this._fetchProfiles(),this._config={...this._config,_profileVersion:(this._config._profileVersion??0)+1};const e=new Event("config-changed",{bubbles:!0,composed:!0});e.detail={config:this._config},this.dispatchEvent(e)}catch{}}}Oe.styles=o`
    .section-heading {
      font-size: 0.85em;
      font-weight: 500;
      color: var(--secondary-text-color);
      margin: 16px 0 4px;
    }
    .section-desc {
      font-size: 0.75em;
      color: var(--secondary-text-color);
      margin: 0 0 8px;
    }
    ha-select {
      width: 100%;
    }
    .active-profile-select {
      margin-bottom: 16px;
    }
  `,e([ue({attribute:!1})],Oe.prototype,"hass",void 0),e([_e()],Oe.prototype,"_config",void 0),e([_e()],Oe.prototype,"_profiles",void 0),e([_e()],Oe.prototype,"_activeProfileOptions",void 0),e([_e()],Oe.prototype,"_activeProfileId",void 0),customElements.define("eink-editor-card-editor",Oe);class De extends he{constructor(){super(...arguments),this._config={},this._elements=[],this._selectedIndex=null,this._mode="preview",this._codeText="[]",this._codeError="",this._previewing=!1,this._sending=!1,this._statusMsg="",this._profiles=[],this._profilesLoaded=!1,this._showEditPreview="true"===localStorage.getItem("eink-editor-show-preview"),this._renderTemplates="true"===localStorage.getItem("eink-editor-render-templates"),this._resolvedElements=null,this._profileLoaded=!1,this._previewDebounce=null,this._resolveDebounce=null,this._mdiMap=new Map,this._dragState=null,this._suppressSettingsSync=!1}connectedCallback(){super.connectedCallback(),this._injectFonts(),this._loadMdiMap()}_injectFonts(){if(!document.getElementById("eink-editor-fonts")){const e=document.createElement("style");e.id="eink-editor-fonts",e.textContent='\n        @font-face {\n          font-family: "RobotoMedium";\n          src: url("/wolink_esl/fonts/rbm.ttf") format("truetype");\n          font-weight: 500;\n          font-style: normal;\n        }\n        @font-face {\n          font-family: "PoppinsBold";\n          src: url("/wolink_esl/fonts/ppb.ttf") format("truetype");\n          font-weight: 700;\n          font-style: normal;\n        }\n        @font-face {\n          font-family: "DejaVuSans";\n          src: url("/wolink_esl/fonts/DejaVuSans.ttf") format("truetype");\n          font-weight: normal;\n          font-style: normal;\n        }\n        @font-face {\n          font-family: "MaterialDesignIcons";\n          src: url("/wolink_esl/fonts/materialdesignicons-webfont.ttf") format("truetype");\n          font-weight: normal;\n          font-style: normal;\n        }\n      ',document.head.appendChild(e)}document.fonts.load('500 20px "RobotoMedium"').then(()=>this.requestUpdate()),document.fonts.load('700 20px "PoppinsBold"').then(()=>this.requestUpdate()),document.fonts.load('normal 20px "DejaVuSans"').then(()=>this.requestUpdate()),document.fonts.load('normal 20px "MaterialDesignIcons"').then(()=>this.requestUpdate())}async _loadMdiMap(){try{const e=await fetch("/wolink_esl/fonts/materialdesignicons-webfont_meta.json");if(!e.ok)return;const t=await e.json(),i=new Map;for(const e of t){const t=String.fromCodePoint(parseInt(e.codepoint,16));if(i.set(e.name,t),e.aliases)for(const s of e.aliases)i.set(s,t)}this._mdiMap=i,this.requestUpdate()}catch{}}setConfig(e){const t=e.profile_subentry_id||e.profile_entry_id,i=t!==(this._config?.profile_subentry_id||this._config?.profile_entry_id),s=e._profileVersion!==this._config?._profileVersion,n=t&&!i&&this._config&&(e.dither!==this._config.dither||e.background!==this._config.background||e.rotate!==this._config.rotate);this._config=e,s&&(this._profilesLoaded=!1),e.payload&&Array.isArray(e.payload)&&(this._elements=Re(e.payload),this._codeText=JSON.stringify(this._elements,null,2)),i&&t&&(this._profileLoaded=!1),n&&!this._suppressSettingsSync&&this._syncSettingsToProfile()}updated(){if(!this.hass)return;const e=this._config.profile_subentry_id||this._config.profile_entry_id;if(!this._profileLoaded&&e)return this._profileLoaded=!0,void this._loadProfile();!this._profileLoaded&&this._elements.length>0&&!this._getEntityPicture()&&(this._profileLoaded=!0,this._schedulePreview(),this._scheduleResolveTemplates())}static getConfigElement(){return document.createElement("eink-editor-card-editor")}static getStubConfig(){return{entity:"",service:"wolink_esl.drawcustom",width:296,height:128,background:"white",rotate:0,dither:"none",payload:[{type:"text",value:"Hello",x:10,y:10,size:24,color:"black"}]}}getCardSize(){return 6}get _width(){return this._config.width??296}get _height(){return this._config.height??128}get _background(){return this._config.background??"white"}get _entityId(){return this._config.entity??""}get _service(){return this._config.service??"wolink_esl.drawcustom"}render(){return this._config&&this.hass?q`
      <ha-card>
        <div class="card-header">
          <span class="card-title">
            <ha-icon icon="mdi:palette-outline"></ha-icon>
            E-Ink Editor
          </span>
          <div class="mode-tabs">
            <button
              class="mode-tab ${"preview"===this._mode?"active":""}"
              @click=${()=>this._setMode("preview")}
            >Preview</button>
            <button
              class="mode-tab ${"edit"===this._mode?"active":""}"
              @click=${()=>this._setMode("edit")}
            >Edit</button>
            <button
              class="mode-tab ${"code"===this._mode?"active":""}"
              @click=${()=>this._setMode("code")}
            >Code</button>
          </div>
        </div>

        ${"preview"===this._mode?this._renderPreview():J}
        ${"edit"===this._mode?this._renderEditor():J}
        ${"code"===this._mode?this._renderCode():J}

        ${this._renderProfileBar()}

        <div class="actions">
          <ha-button appearance="outlined"
            ?disabled=${this._previewing}
            @click=${this._onPreview}
          >${this._previewing?"Rendering...":"Preview"}</ha-button>
          <ha-button appearance="filled"
            ?disabled=${this._sending}
            @click=${this._onSend}
          >${this._sending?"Sending...":"Send to Display"}</ha-button>
        </div>

        ${this._statusMsg?q`<div class="status-msg ${this._statusMsg.startsWith("Error")?"error":""}">${this._statusMsg}</div>`:J}
      </ha-card>
    `:q`<ha-card><div class="placeholder">Loading...</div></ha-card>`}_renderPreview(){const e=this._getEntityPicture(),t=e?`${e}${e.includes("?")?"&":"?"}t=${Date.now()}`:null;return q`
      <div class="canvas-container">
        ${t?q`<img class="preview-img" src=${t} alt="Display preview" />`:q`<div class="placeholder">No preview — click Preview to render</div>`}
      </div>
    `}_renderEditor(){return q`
      <div class="toolbar">
        <button @click=${()=>this._addElement("text")}>+ Text</button>
        <button @click=${()=>this._addElement("rectangle")}>+ Rect</button>
        <button @click=${()=>this._addElement("icon")}>+ Icon</button>
        <button @click=${()=>this._addElement("dlimg")}>+ Image</button>
        <button @click=${()=>this._addElement("circle")}>+ Circle</button>
        <button @click=${()=>this._addElement("line")}>+ Line</button>
      </div>

      <div class="canvas-container">
        <div class="inline-preview-toggle">
          <button @click=${this._toggleRenderTemplates}>
            ${this._renderTemplates?"Don't Render Templates":"Render Templates"}
          </button>
        </div>

        <svg
          class="editor-canvas"
          viewBox="0 0 ${this._width} ${this._height}"
          width="${this._width}"
          shape-rendering="crispEdges"
          @pointerdown=${this._onCanvasPointerDown}
        >
          <rect x="0" y="0" width="${this._width}" height="${this._height}"
            fill="${{white:"#ffffff",black:"#000000",red:"#ff0000",yellow:"#ffcc00"}[this._background]??"#ffffff"}" />
          ${(this._renderTemplates&&this._resolvedElements||this._elements).map((e,t)=>Ce(e,t,t===this._selectedIndex,this._mdiMap))}
        </svg>
        
        <div class="toolbar action-bar ${null===this._selectedIndex?"hidden":""}">
          <ha-icon-button .path=${"M19,21H8V7H19M19,5H8A2,2 0 0,0 6,7V21A2,2 0 0,0 8,23H19A2,2 0 0,0 21,21V7A2,2 0 0,0 19,5M16,1H4A2,2 0 0,0 2,3V17H4V3H16V1Z"} @click=${this._duplicateSelected}></ha-icon-button>
          <ha-icon-button .path=${"M13,20H11V8L5.5,13.5L4.08,12.08L12,4.16L19.92,12.08L18.5,13.5L13,8V20Z"} @click=${this._moveUp}></ha-icon-button>
          <ha-icon-button .path=${"M11,4H13V16L18.5,10.5L19.92,11.92L12,19.84L4.08,11.92L5.5,10.5L11,16V4Z"} @click=${this._moveDown}></ha-icon-button>
          <ha-icon-button .path=${"M19,4H15.5L14.5,3H9.5L8.5,4H5V6H19M6,19A2,2 0 0,0 8,21H16A2,2 0 0,0 18,19V7H6V19Z"} @click=${this._deleteSelected}></ha-icon-button>
        </div>
        
      </div>

      ${null!==this._selectedIndex?this._renderPropertyPanel():J}

      <div class="inline-preview-toggle">
        <button @click=${this._toggleEditPreview}>
          ${this._showEditPreview?"Hide Preview":"Show Preview"}
        </button>
      </div>
      ${this._showEditPreview?this._renderPreview():J}
    `}_renderPropertyPanel(){const e=this._selectedIndex,t=this._elements[e];return t?q`
      <div class="prop-panel">
        <h4>${t.type} #${e}</h4>
        ${this._renderCommonProps(t)}
        ${this._renderTypeSpecificProps(t)}
      </div>
    `:J}_renderCommonProps(e){const t="x"in e&&"y"in e,i=t?e.x:xe(e).x,s=t?e.y:xe(e).y,n=!0===e.dither?"floyd-steinberg":!1===e.dither?"none":e.dither??"";return q`
      <div class="prop-row">
        <ha-textfield label="x" type="number"
          .value=${String(i)}
          @change=${e=>this._onPropChange(e,"x")}></ha-textfield>
        <ha-textfield label="y" type="number"
          .value=${String(s)}
          @change=${e=>this._onPropChange(e,"y")}></ha-textfield>
      </div>
      <div class="prop-row">
        <ha-select label="dither"
          .options=${[{value:"",label:"inherit"},{value:"floyd-steinberg",label:"Floyd-Steinberg"},{value:"atkinson",label:"Atkinson"},{value:"stucki",label:"Stucki"},{value:"none",label:"None"}]}
          .value=${n}
          @selected=${e=>this._onPropChange(e,"dither")}
          @closed=${e=>e.stopPropagation()}>
        </ha-select>
      </div>
    `}_renderTypeSpecificProps(e){switch(e.type){case"text":case"multiline":return q`
          <div class="prop-row">
            <ha-textfield label="value"
              .value=${e.value||""}
              @change=${e=>this._onPropChange(e,"value")}></ha-textfield>
          </div>
          <div class="prop-row">
            <ha-textfield label="size" type="number"
              .value=${String(e.size??20)}
              @change=${e=>this._onPropChange(e,"size")}></ha-textfield>
            <ha-select label="color"
              .options=${[{value:"black",label:"black"},{value:"white",label:"white"},{value:"red",label:"red"},{value:"yellow",label:"yellow"}]}
              .value=${e.color??"black"}
              @selected=${e=>this._onPropChange(e,"color")}
              @closed=${e=>e.stopPropagation()}>
            </ha-select>
          </div>
          <div class="prop-row">
            <ha-select label="font"
              .options=${[{value:"rbm.ttf",label:"Roboto Medium"},{value:"ppb.ttf",label:"Poppins Bold"},{value:"DejaVuSans.ttf",label:"DejaVu Sans"}]}
              .value=${e.font??"rbm.ttf"}
              @selected=${e=>this._onPropChange(e,"font")}
              @closed=${e=>e.stopPropagation()}>
            </ha-select>
          </div>
          ${"multiline"===e.type?q`
            <div class="prop-row">
              <ha-textfield label="max width" type="number"
                .value=${String(e.max_width??"")}
                @change=${e=>this._onPropChange(e,"max_width")}></ha-textfield>
            </div>
          `:J}
        `;case"rectangle":case"ellipse":return q`
          <div class="prop-row">
            <ha-textfield label="w" type="number"
              .value=${String(e.x_end-e.x_start)}
              @change=${e=>this._onPropChange(e,"_width")}></ha-textfield>
            <ha-textfield label="h" type="number"
              .value=${String(e.y_end-e.y_start)}
              @change=${e=>this._onPropChange(e,"_height")}></ha-textfield>
          </div>
          <div class="prop-row">
            <ha-select label="fill"
              .options=${[{value:"",label:"none"},{value:"black",label:"black"},{value:"white",label:"white"},{value:"red",label:"red"},{value:"yellow",label:"yellow"}]}
              .value=${e.fill??""}
              @selected=${e=>this._onPropChange(e,"fill")}
              @closed=${e=>e.stopPropagation()}>
            </ha-select>
            <ha-select label="outline"
              .options=${[{value:"",label:"none"},{value:"black",label:"black"},{value:"white",label:"white"},{value:"red",label:"red"},{value:"yellow",label:"yellow"}]}
              .value=${e.outline??""}
              @selected=${e=>this._onPropChange(e,"outline")}
              @closed=${e=>e.stopPropagation()}>
            </ha-select>
          </div>
          <div class="prop-row">
            <ha-textfield label="stroke" type="number"
              .value=${String(e.width??1)}
              @change=${e=>this._onPropChange(e,"width")}></ha-textfield>
          </div>
        `;case"line":return q`
          <div class="prop-row">
            <ha-textfield label="x2" type="number"
              .value=${String(e.x_end)}
              @change=${e=>this._onPropChange(e,"x_end")}></ha-textfield>
            <ha-textfield label="y2" type="number"
              .value=${String(e.y_end)}
              @change=${e=>this._onPropChange(e,"y_end")}></ha-textfield>
          </div>
          <div class="prop-row">
            <ha-select label="color"
              .options=${[{value:"black",label:"black"},{value:"white",label:"white"},{value:"red",label:"red"},{value:"yellow",label:"yellow"}]}
              .value=${e.fill??"black"}
              @selected=${e=>this._onPropChange(e,"fill")}
              @closed=${e=>e.stopPropagation()}>
            </ha-select>
            <ha-textfield label="width" type="number"
              .value=${String(e.width??1)}
              @change=${e=>this._onPropChange(e,"width")}></ha-textfield>
          </div>
        `;case"icon":return q`
          <div class="prop-row">
            <ha-textfield label="icon"
              .value=${e.value||""}
              .placeholder=${"mdi:home"}
              @change=${e=>this._onPropChange(e,"value")}></ha-textfield>
          </div>
          <div class="prop-row">
            <ha-textfield label="size" type="number"
              .value=${String(e.size??24)}
              @change=${e=>this._onPropChange(e,"size")}></ha-textfield>
            <ha-select label="color"
              .options=${[{value:"black",label:"black"},{value:"white",label:"white"},{value:"red",label:"red"},{value:"yellow",label:"yellow"}]}
              .value=${e.color??"black"}
              @selected=${e=>this._onPropChange(e,"color")}
              @closed=${e=>e.stopPropagation()}>
            </ha-select>
          </div>
        `;case"dlimg":return q`
          <div class="prop-row">
            <ha-textfield label="url"
              .value=${e.url||""}
              .placeholder=${"/local/image.png or http://..."}
              @change=${e=>this._onPropChange(e,"url")}></ha-textfield>
          </div>
          <div class="prop-row">
            <ha-textfield label="w" type="number"
              .value=${String(e.xsize??48)}
              @change=${e=>this._onPropChange(e,"xsize")}></ha-textfield>
            <ha-textfield label="h" type="number"
              .value=${String(e.ysize??48)}
              @change=${e=>this._onPropChange(e,"ysize")}></ha-textfield>
          </div>
          <div class="slider-row">
            <label>sat.</label>
            <ha-slider min="0" max="200" step="5"
              .value=${Math.round(100*(e.saturation??1))}
              @change=${e=>this._onPropChange(e,"saturation")}></ha-slider>
          </div>
          <div class="slider-row">
            <label>contr.</label>
            <ha-slider min="0" max="200" step="5"
              .value=${Math.round(100*(e.contrast??1))}
              @change=${e=>this._onPropChange(e,"contrast")}></ha-slider>
          </div>
        `;case"circle":return q`
          <div class="prop-row">
            <ha-textfield label="radius" type="number"
              .value=${String(e.radius??10)}
              @change=${e=>this._onPropChange(e,"radius")}></ha-textfield>
          </div>
          <div class="prop-row">
            <ha-select label="fill"
              .options=${[{value:"",label:"none"},{value:"black",label:"black"},{value:"white",label:"white"},{value:"red",label:"red"},{value:"yellow",label:"yellow"}]}
              .value=${e.fill??""}
              @selected=${e=>this._onPropChange(e,"fill")}
              @closed=${e=>e.stopPropagation()}>
            </ha-select>
            <ha-select label="outline"
              .options=${[{value:"",label:"none"},{value:"black",label:"black"},{value:"white",label:"white"},{value:"red",label:"red"},{value:"yellow",label:"yellow"}]}
              .value=${e.outline??"black"}
              @selected=${e=>this._onPropChange(e,"outline")}
              @closed=${e=>e.stopPropagation()}>
            </ha-select>
          </div>
        `;case"qrcode":return q`
          <div class="prop-row">
            <ha-textfield label="value"
              .value=${e.value||""}
              @change=${e=>this._onPropChange(e,"value")}></ha-textfield>
          </div>
          <div class="prop-row">
            <ha-textfield label="size" type="number"
              .value=${String(e.size??48)}
              @change=${e=>this._onPropChange(e,"size")}></ha-textfield>
          </div>
        `;case"progress_bar":return q`
          <div class="prop-row">
            <ha-textfield label="progress" type="number"
              .value=${String(e.progress??50)}
              @change=${e=>this._onPropChange(e,"progress")}></ha-textfield>
          </div>
          <div class="prop-row">
            <ha-textfield label="w" type="number"
              .value=${String(e.x_end-e.x_start)}
              @change=${e=>this._onPropChange(e,"_width")}></ha-textfield>
            <ha-textfield label="h" type="number"
              .value=${String(e.y_end-e.y_start)}
              @change=${e=>this._onPropChange(e,"_height")}></ha-textfield>
          </div>
        `;default:return J}}_renderCode(){return q`
      <div class="code-container">
        <textarea
          class="code-editor"
          rows="14"
          .value=${this._codeText}
          @input=${this._onCodeInput}
        ></textarea>
        ${this._codeError?q`<div class="code-error">${this._codeError}</div>`:J}
        <div style="margin-top: 6px;">
          <ha-button appearance="outlined" @click=${this._applyCode}>Apply JSON</ha-button>
        </div>
      </div>
    `}_getSvgScale(){const e=this.renderRoot.querySelector("svg.editor-canvas");if(!e)return{sx:1,sy:1};const t=e.getBoundingClientRect();return{sx:this._width/t.width,sy:this._height/t.height}}_onCanvasPointerDown(e){e.stopPropagation(),e.preventDefault();const t=e.target.closest(".element-group");if(!t)return void(this._selectedIndex=null);const i=parseInt(t.getAttribute("data-index")??"-1",10);if(i<0)return;this._selectedIndex=i;const s=this._getSvgScale();this._dragState={index:i,startX:e.clientX,startY:e.clientY,dx:0,dy:0,group:t},e.target.setPointerCapture(e.pointerId);const n=e=>{if(!this._dragState)return;const t=this._dragState;t.dx=(e.clientX-t.startX)*s.sx,t.dy=(e.clientY-t.startY)*s.sy,t.group.setAttribute("transform",`translate(${t.dx}, ${t.dy})`)},r=e=>{e.target.releasePointerCapture(e.pointerId);const t=this.renderRoot.querySelector("svg.editor-canvas");if(t&&(t.removeEventListener("pointermove",n),t.removeEventListener("pointerup",r)),!this._dragState)return;const i=this._dragState;if(Math.abs(i.dx)>.5||Math.abs(i.dy)>.5){const e=this._elements[i.index];if(e){const t=xe(e);we(e,t.x+i.dx,t.y+i.dy),this._elements=[...this._elements],this._syncCodeFromElements(),this._schedulePreview(),this._scheduleResolveTemplates()}}i.group.removeAttribute("transform"),this._dragState=null},o=this.renderRoot.querySelector("svg.editor-canvas");o&&(o.addEventListener("pointermove",n),o.addEventListener("pointerup",r))}_addElement(e){const t=function(e,t,i){const s=Math.round(t/2),n=Math.round(i/2);switch(e){case"text":return{type:"text",value:"Text",x:s-30,y:n,size:20,color:"black"};case"multiline":return{type:"multiline",value:"Line 1\nLine 2",x:s-30,y:n-10,size:16,color:"black"};case"rectangle":return{type:"rectangle",x_start:s-40,y_start:n-20,x_end:s+40,y_end:n+20,outline:"black",width:1};case"line":return{type:"line",x_start:s-40,y_start:n,x_end:s+40,y_end:n,fill:"black",width:1};case"icon":return{type:"icon",value:"mdi:home",x:s-12,y:n-12,size:24,color:"black"};case"dlimg":return{type:"dlimg",url:"",x:s-24,y:n-24,xsize:48,ysize:48};case"circle":return{type:"circle",x:s,y:n,radius:20,outline:"black",width:1};case"ellipse":return{type:"ellipse",x_start:s-30,y_start:n-15,x_end:s+30,y_end:n+15,outline:"black",width:1};case"qrcode":return{type:"qrcode",value:"hello",x:s-24,y:n-24,size:48};case"progress_bar":return{type:"progress_bar",x_start:s-50,y_start:n-5,x_end:s+50,y_end:n+5,progress:50,fill:"black",outline:"black",width:1}}}(e,this._width,this._height);this._elements=[...this._elements,t],this._selectedIndex=this._elements.length-1,this._syncCodeFromElements(),this._schedulePreview(),this._scheduleResolveTemplates()}_deleteSelected(){null!==this._selectedIndex&&(this._elements=this._elements.filter((e,t)=>t!==this._selectedIndex),this._selectedIndex=null,this._syncCodeFromElements(),this._schedulePreview(),this._scheduleResolveTemplates())}_duplicateSelected(){if(null===this._selectedIndex)return;const e=Re(this._elements[this._selectedIndex]),t=xe(e);we(e,t.x+10,t.y+10),this._elements=[...this._elements,e],this._selectedIndex=this._elements.length-1,this._syncCodeFromElements(),this._schedulePreview(),this._scheduleResolveTemplates()}_moveUp(){if(null===this._selectedIndex||this._selectedIndex<=0)return;const e=this._selectedIndex,t=[...this._elements];[t[e-1],t[e]]=[t[e],t[e-1]],this._elements=t,this._selectedIndex=e-1,this._syncCodeFromElements()}_moveDown(){if(null===this._selectedIndex||this._selectedIndex>=this._elements.length-1)return;const e=this._selectedIndex,t=[...this._elements];[t[e],t[e+1]]=[t[e+1],t[e]],this._elements=t,this._selectedIndex=e+1,this._syncCodeFromElements()}_onPropChange(e,t){if(null===this._selectedIndex)return;const i=this._elements[this._selectedIndex],s=e.detail?.value??e.target.value;if("x"===t||"y"===t){const e=parseInt(s,10);if(isNaN(e))return;if("x"in i&&"y"in i)"x"===t?i.x=e:i.y=e;else{const s=xe(i);we(i,"x"===t?e:s.x,"y"===t?e:s.y)}}else if("_width"===t||"_height"===t){const e=parseInt(s,10);if(isNaN(e)||e<=0)return;const n=xe(i);!function(e,t,i){switch(e.type){case"text":case"multiline":e.size=Math.round(i);break;case"icon":case"qrcode":e.size=Math.round(Math.max(t,i));break;case"dlimg":e.xsize=Math.round(t),e.ysize=Math.round(i);break;case"rectangle":case"ellipse":case"progress_bar":case"line":e.x_end=Math.round(e.x_start+t),e.y_end=Math.round(e.y_start+i);break;case"circle":e.radius=Math.round(Math.max(t,i)/2)}}(i,"_width"===t?e:n.width,"_height"===t?e:n.height)}else if("dither"===t)if(""===s||"inherit"===s){if(void 0===i.dither)return;delete i.dither}else{if(i.dither===s)return;i.dither=s}else if("saturation"===t||"contrast"===t){const e=parseInt(s,10);if(isNaN(e))return;i[t]=e/100}else{if(["size","radius","width","x_end","y_end","xsize","ysize","progress","max_width"].includes(t)){const e=parseInt(s,10);if(isNaN(e))return;i[t]=e}else""!==s||"fill"!==t&&"outline"!==t&&"font"!==t?i[t]=s:delete i[t]}this._elements=[...this._elements],this._syncCodeFromElements(),this._schedulePreview(),this._scheduleResolveTemplates()}_onCodeInput(e){this._codeText=e.target.value,this._codeError=""}_applyCode(){const e=function(e){try{const t=JSON.parse(e);if(Array.isArray(t))return t}catch{}return null}(this._codeText);e?(this._elements=e,this._selectedIndex=null,this._codeError="",this._schedulePreview(),this._scheduleResolveTemplates()):this._codeError="Invalid JSON — must be an array of element objects"}_syncCodeFromElements(){this._codeText=JSON.stringify(this._elements,null,2),this._codeError=""}_getEntityPicture(){if(!this._entityId||!this.hass)return null;const e=this.hass.states[this._entityId];return e?.attributes?.entity_picture??null}_schedulePreview(){this._previewDebounce&&clearTimeout(this._previewDebounce),this._previewDebounce=setTimeout(()=>this._onPreview(),500)}async _resolveTemplateValues(){if(this._renderTemplates&&this.hass&&this._elements.length)try{const e=await this.hass.callWS({type:"eink_display_manager/resolve_templates",payload:Re(this._elements)});this._resolvedElements=e.payload??null}catch{this._resolvedElements=null}else this._resolvedElements=null}_scheduleResolveTemplates(){this._resolveDebounce&&clearTimeout(this._resolveDebounce),this._resolveDebounce=setTimeout(()=>this._resolveTemplateValues(),400)}_toggleRenderTemplates(){this._renderTemplates=!this._renderTemplates,localStorage.setItem("eink-editor-render-templates",String(this._renderTemplates)),this._renderTemplates?this._resolveTemplateValues():this._resolvedElements=null}async _callService(e){if(!this._entityId)return void(this._statusMsg="Error: no entity configured");const[t,i]=this._service.split(".");if(t&&i){e?this._previewing=!0:this._sending=!0,this._statusMsg="";try{await this.hass.callService(t,i,{entity_id:this._entityId,payload:Re(this._elements),background:this._background,rotate:this._config.rotate??0,dither:this._config.dither??"none",dry_run:e}),await new Promise(e=>setTimeout(e,500)),this.requestUpdate(),e||(this._statusMsg=`Sent at ${(new Date).toLocaleTimeString()}`)}catch(e){this._statusMsg=`Error: ${e.message||e}`}finally{this._previewing=!1,this._sending=!1}}else this._statusMsg="Error: invalid service format"}_onPreview(){this._callService(!0)}_onSend(){this._callService(!1)}async _fetchProfiles(){if(!this._profilesLoaded&&this.hass)try{const e=await this.hass.callWS({type:"eink_display_manager/list_profiles"});this._profiles=e.profiles||[],this._profilesLoaded=!0}catch{}}_renderProfileBar(){this._profilesLoaded||this._fetchProfiles();const e=this._config.profile_subentry_id||this._config.profile_entry_id;if(!e)return J;const t=this._profiles.find(t=>t.subentry_id===e);return t?q`
      <div class="profile-bar">
        <span class="profile-label">
          Profile: <strong>${t.title}</strong>
          ${!1===t.enabled?q`<span class="profile-inactive">(inactive)</span>`:q`<span class="profile-active">(active)</span>`}
        </span>
        <ha-button appearance="outlined" @click=${this._loadProfile}>Load</ha-button>
        <ha-button appearance="filled" @click=${this._saveProfile}>Save</ha-button>
        ${!1===t.enabled?q`<ha-button appearance="filled" @click=${this._activateProfile}>Activate</ha-button>`:J}
      </div>
    `:J}async _loadProfile(){const e=this._config.profile_subentry_id,t=this._config.profile_entry_id;if((e||t)&&this.hass){this._statusMsg="",this._suppressSettingsSync=!0;try{const i={type:"eink_display_manager/get_payload"};e?i.subentry_id=e:t&&(i.config_entry_id=t);const s=await this.hass.callWS(i);this._elements=s.payload||[],this._syncCodeFromElements(),this._config={...this._config,entity:s.entity_id||this._config.entity,service:s.service||this._config.service,width:s.width??this._config.width,height:s.height??this._config.height,background:s.background||this._config.background,rotate:s.rotate??this._config.rotate,dither:s.dither||this._config.dither},this._statusMsg="Loaded from profile",this._elements.length>0&&(this._schedulePreview(),this._scheduleResolveTemplates())}catch(e){this._statusMsg=`Error: ${e.message||e}`}finally{setTimeout(()=>{this._suppressSettingsSync=!1},500)}}}async _syncSettingsToProfile(){const e=this._config.profile_subentry_id;if(e&&this.hass)try{await this.hass.callWS({type:"eink_display_manager/update_profile_settings",subentry_id:e,dither:this._config.dither??"none",background:this._config.background??"white",rotate:this._config.rotate??0})}catch(e){console.warn("Failed to sync settings to profile:",e)}}async _activateProfile(){const e=this._config.profile_subentry_id;if(e&&this.hass)try{await this.hass.callWS({type:"eink_display_manager/activate_profile",subentry_id:e}),this._profilesLoaded=!1,this._fetchProfiles(),this._statusMsg="Profile activated"}catch(e){this._statusMsg=`Error: ${e.message||e}`}}async _saveProfile(){const e=this._config.profile_subentry_id,t=this._config.profile_entry_id;if((e||t)&&this.hass){this._statusMsg="";try{const i={type:"eink_display_manager/update_payload",payload:Re(this._elements)};e?i.subentry_id=e:t&&(i.config_entry_id=t),await this.hass.callWS(i),this._statusMsg="Saved to profile"}catch(e){this._statusMsg=`Error: ${e.message||e}`}}}_toggleEditPreview(){this._showEditPreview=!this._showEditPreview,localStorage.setItem("eink-editor-show-preview",String(this._showEditPreview))}_setMode(e){"code"===e&&this._syncCodeFromElements(),this._mode=e}}De.styles=o`
    :host {
      display: block;
    }

    .card-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 12px 16px 0;
    }

    .card-title {
      font-size: 1.1em;
      font-weight: 500;
      color: var(--primary-text-color);
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .mode-tabs {
      display: flex;
      gap: 4px;
    }

    .mode-tab {
      padding: 4px 12px;
      border: 1px solid var(--divider-color);
      border-radius: 4px;
      background: transparent;
      color: var(--secondary-text-color);
      font-size: 0.8em;
      cursor: pointer;
    }

    .mode-tab.active {
      background: var(--primary-color);
      color: var(--text-primary-color, #fff);
      border-color: var(--primary-color);
    }

    .canvas-container {
      padding: 12px 12px 0;
      text-align: center;
      overflow: hidden;
    }

    .canvas-container ~ .canvas-container {
      padding-top: 0;
      //padding-bottom: 12px;
    }

    svg.editor-canvas {
      border: 1px solid var(--divider-color);
      border-radius: 4px;
      touch-action: none;
      user-select: none;
      -webkit-touch-callout: none;
      max-width: 100%;
      cursor: crosshair;
    }

    .preview-img {
      max-width: 100%;
      image-rendering: pixelated;
      border: 1px solid var(--divider-color);
      border-radius: 4px;
    }

    .placeholder {
      padding: 32px;
      text-align: center;
      color: var(--secondary-text-color);
      font-style: italic;
    }

    /* Toolbar */

    .toolbar {
      display: flex;
      gap: 4px;
      padding: 0 12px;
      flex-wrap: wrap;
    }

    .toolbar button {
      padding: 4px 8px;
      border: 1px solid var(--divider-color);
      border-radius: 4px;
      background: var(--secondary-background-color, #f5f5f5);
      color: var(--primary-text-color);
      font-size: 0.75em;
      cursor: pointer;
      white-space: nowrap;
      min-height: 36px;
      box-sizing: border-box;
      display: inline-flex;
      align-items: center;
      justify-content: center;
    }

    .toolbar button:hover {
      background: var(--primary-color);
      color: var(--text-primary-color, #fff);
      border-color: var(--primary-color);
    }

    .toolbar.action-bar {
      min-height: 48px;
      align-items: center;
    }

    .toolbar.action-bar.hidden {
      visibility: hidden;
    }

    /* Property panel */

    .prop-panel {
      padding: 8px 12px 8px;
    }

    .prop-panel h4 {
      margin: 0 0 8px;
      font-size: 0.85em;
      color: var(--secondary-text-color);
    }

    .prop-row {
      display: flex;
      gap: 8px;
      margin-bottom: 8px;
      align-items: flex-end;
    }

    .prop-row ha-textfield {
      flex: 1;
      min-width: 0;
    }

    .prop-row ha-textfield[type="number"] {
      flex: 0 0 80px;
    }

    .prop-row ha-select {
      flex: 1;
      min-width: 0;
    }

    .prop-row ha-slider {
      flex: 1;
      min-width: 0;
    }

    .slider-row {
      display: flex;
      align-items: center;
      gap: 8px;
      margin-bottom: 8px;
    }

    .slider-row label {
      font-size: 0.8em;
      color: var(--secondary-text-color);
      min-width: 36px;
      text-align: right;
    }

    /* Code view */

    .code-container {
      padding: 0 12px 12px;
    }

    textarea.code-editor {
      width: 100%;
      box-sizing: border-box;
      font-family: monospace;
      font-size: 12px;
      line-height: 1.4;
      padding: 8px;
      border: 1px solid var(--divider-color);
      border-radius: 4px;
      background: var(--secondary-background-color, #f5f5f5);
      color: var(--primary-text-color);
      resize: vertical;
    }

    .code-error {
      color: var(--error-color, #db4437);
      font-size: 0.8em;
      margin-top: 4px;
    }

    /* Action buttons */

    .actions {
      display: flex;
      gap: 8px;
      padding: 0 12px 12px;
    }

    .actions ha-button {
      flex: 1;
    }

    .status-msg {
      padding: 0 12px 8px;
      font-size: 0.75em;
      color: var(--secondary-text-color);
    }

    .status-msg.error {
      color: var(--error-color, #db4437);
    }

    /* Profile bar */

    .profile-bar {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 12px 12px 8px;
      font-size: 0.85em;
    }

    .profile-label {
      flex: 1;
      color: var(--primary-text-color);
    }

    .profile-active {
      color: var(--success-color, #4caf50);
      font-size: 0.85em;
    }

    .profile-inactive {
      color: var(--error-color, #f44336);
      font-size: 0.85em;
    }

    .inline-preview-toggle {
      text-align: center;
      padding: 8px 12px;
      border-top: 1px solid var(--divider-color);
      //margin-top: 8px;
      padding-bottom: 0;
    }

    .inline-preview-toggle button {
      background: none;
      border: 1px solid var(--divider-color);
      border-radius: 16px;
      color: var(--primary-text-color);
      padding: 4px 14px;
      font-size: 0.8em;
      cursor: pointer;
      opacity: 0.7;
      margin-bottom: 14px;
    }

    .inline-preview-toggle button:hover {
      opacity: 1;
    }

    /* Draggable elements */

    .element-group {
      cursor: move;
    }

    .element-group:hover {
      opacity: 0.85;
    }
  `,e([ue({attribute:!1})],De.prototype,"hass",void 0),e([_e()],De.prototype,"_config",void 0),e([_e()],De.prototype,"_elements",void 0),e([_e()],De.prototype,"_selectedIndex",void 0),e([_e()],De.prototype,"_mode",void 0),e([_e()],De.prototype,"_codeText",void 0),e([_e()],De.prototype,"_codeError",void 0),e([_e()],De.prototype,"_previewing",void 0),e([_e()],De.prototype,"_sending",void 0),e([_e()],De.prototype,"_statusMsg",void 0),e([_e()],De.prototype,"_profiles",void 0),e([_e()],De.prototype,"_profilesLoaded",void 0),e([_e()],De.prototype,"_showEditPreview",void 0),e([_e()],De.prototype,"_renderTemplates",void 0),e([_e()],De.prototype,"_resolvedElements",void 0),customElements.define("eink-editor-card",De),window.customCards=window.customCards||[],window.customCards.push({type:"eink-editor-card",name:"E-Ink Display Editor",description:"Visual WYSIWYG editor for e-ink display templates",preview:!0});
