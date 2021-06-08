const app = new Vue({
    el: "#appResource",
    delimiters: ["<%", "%>"],
    mounted() {
      console.log("vue app")
    },
    
    data: {
      solt:[
          {solt:1,check:false},
          {solt:2,check:false},
          {solt:3,check:false},
          {solt:4,check:false},
          {solt:5,check:false},
          {solt:6,check:false},
          {solt:7,check:false},
          {solt:8,check:false},
          {solt:9,check:false},
          {solt:10,check:false},
          {solt:11,check:false},
          {solt:12,check:false},
      ],
    },
    methods:{
      selectSolt(soltNo){
        var pos,prevPos;
        if(soltNo==1){
            pos = 0
            prevPos = null
        }else{
            pos = soltNo-1;
            prevPos = soltNo-2
        }
        var firstFlag = true;
        for(var i=0; i<this.solt.length;i++){
            if(this.solt[i].check){
                firstFlag = false;
                break;
            }
        }
        if(!this.solt[pos].check){
            if(firstFlag){
                this.solt[pos].check = true;
            }else{
                if(prevPos!=null){
                    if(this.solt[prevPos].check || this.solt[soltNo].check){
                        this.solt[pos].check = true;
                    }
                }else{
                    if(this.solt[soltNo].check){
                        this.solt[pos].check = true;
                    }
                }
            }
        }else{
            for(var j = pos;j<this.solt.length;j++){
                this.solt[j].check = false;
            }
        }
      }
    }
   
  });
  
  const app2 = new Vue({
    el: "#appResource2",
    delimiters: ["<%", "%>"],
    mounted() {
      console.log("vue app")
    },
    
    data: {
      solt:[
          {solt:1,check:false},
          {solt:2,check:false},
          {solt:3,check:false},
          {solt:4,check:false},
          {solt:5,check:false},
          {solt:6,check:false},
          {solt:7,check:false},
          {solt:8,check:false},
          {solt:9,check:false},
          {solt:10,check:false},
          {solt:11,check:false},
          {solt:12,check:false},
      ],
    },
    methods:{
      selectSolt(soltNo){
        var pos,prevPos;
        if(soltNo==1){
            pos = 0
            prevPos = null
        }else{
            pos = soltNo-1;
            prevPos = soltNo-2
        }
        var firstFlag = true;
        for(var i=0; i<this.solt.length;i++){
            if(this.solt[i].check){
                firstFlag = false;
                break;
            }
        }
        if(!this.solt[pos].check){
            if(firstFlag){
                this.solt[pos].check = true;
            }else{
                if(prevPos!=null){
                    if(this.solt[prevPos].check || this.solt[soltNo].check){
                        this.solt[pos].check = true;
                    }
                }else{
                    if(this.solt[soltNo].check){
                        this.solt[pos].check = true;
                    }
                }
            }
        }else{
            for(var j = pos;j<this.solt.length;j++){
                this.solt[j].check = false;
            }
        }
      }
    }
   
  });
  
  console.log(app.solt);
  console.log(app2.solt);



