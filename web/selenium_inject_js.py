js = '''
window. pre_ex = {
load_js:function(src,success){
    if(success){
        return this._load_js(src,success)
    }else{
        var p = new Promise((resolve,reject)=>{
            this._load_js(src,function(){
                resolve()
            })
        })
        return p
    }
},
_load_js: function(src,success) {
    success = success || function(){};
    var name = src //btoa(src)
    if(!window['__js_hook_'+name]){
        window['__js_hook_'+name]=[]
    }
    window['__js_hook_'+name].push(success)
    var hooks=window['__js_hook_'+name]
    if(window['__js_loaded_'+name]){
        while (hooks.length>0){
            hooks.pop()()
        }
    }
    if(! window['__js_'+name]){
        window['__js_'+name]=true
        var domScript = document.createElement('script');
        domScript.src = src;

        domScript.onload = domScript.onreadystatechange = function() {
            if (!this.readyState || 'loaded' === this.readyState || 'complete' === this.readyState) {
                window['__js_loaded_'+name]=true
                while (hooks.length>0){
                    hooks.pop()()
                }
                this.onload = this.onreadystatechange = null;
                // 让script元素显示出来
                //this.parentNode.removeChild(this);
            }
        }
        document.getElementsByTagName('head')[0].appendChild(domScript);
    }
},
downLoadCanvas(canvas,filename){
    let img = document.createElement('a');
    img.href = canvas.toDataURL("image/jpeg").replace("image/jpeg", "image/octet-stream");
    img.download =  filename;
    img.click();

},
 downLoadImage(downloadName, url) {
    //url是dataurl ,或者 url
    var getImageDataURL = (image)=> {
        // 创建画布
        const canvas = document.createElement('canvas');
        canvas.width = image.width;
        canvas.height = image.height;
        const ctx = canvas.getContext('2d');
        // 以图片为背景剪裁画布
        ctx.drawImage(image, 0, 0, image.width, image.height);
        // 获取图片后缀名
        const extension = image.src.substring(image.src.lastIndexOf('.') + 1).toLowerCase();
        // 某些图片 url 可能没有后缀名，默认是 png
        return canvas.toDataURL('image/' + extension, 1);
    }

    const tag = document.createElement('a');
    // 此属性的值就是下载时图片的名称，注意，名称中不能有半角点，否则下载时后缀名会错误
    tag.setAttribute('download', downloadName.replace(/\./g, '。'));

    const image = new Image();
    // 设置 image 的 url, 添加时间戳，防止浏览器缓存图片
    image.src = url //+ '?time=' + new Date().getTime();
    //重要，设置 crossOrigin 属性，否则图片跨域会报错
    image.setAttribute('crossOrigin', 'Anonymous');
    // 图片未加载完成时操作会报错
    image.onload = () => {
        tag.href = getImageDataURL(image);
        tag.click();
    };
},
}
'''