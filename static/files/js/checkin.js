const app = new Vue({
  el: "#app",
  delimiters: ["<%", "%>"],
  data: {
    imageData: [],
    ImageDetails: {
        url: "",
        file: "",
        service:""
      },
  },
  methods: {
    deleteImage(imageindex) {
      this.imageData.splice(imageindex, 1);
    },
    uploadImgToArray(file,fileName){
        file.lastModifiedDate = Date.now();
      
      var converted_file = new File([file],  fileName,{lastModified: Date.now()});
        console.log("file size is "+converted_file.size)
        this.ImageDetails.url = URL.createObjectURL(converted_file);
        this.ImageDetails.file = converted_file;
        this.imageData.push(this.ImageDetails);
        this.ImageDetails = {
          file: "",
          url: "",
          service:""
          
        };
      },
    async onImageFileChanged(event) {
      console.log(event);
      console.log("orginal file size is" + event.target.files[0].size);
      var file = event.target.files[0];

      const options = {
        maxSizeMB: 1,
        maxWidthOrHeight: 1920,
        useWebWorker: true,
        onProgress: Function(2),
      };
      try {
        const compressedFile = await imageCompression(
          event.target.files[0],
          options
        );
        console.log(
          "compressedFile instanceof Blob",
          compressedFile instanceof Blob
        ); // true
        console.log(
          `compressedFile size ${compressedFile.size / 1024 / 1024} MB`
        ); // smaller than maxSizeMB

        await this.uploadImgToArray(compressedFile, event.target.files[0].name); // write your own logic
      } catch (error) {
        console.log(error);
      }
    },
  },
});
