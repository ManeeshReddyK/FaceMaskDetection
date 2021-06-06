import { Component, OnInit } from '@angular/core';
import { Title } from '@angular/platform-browser';

@Component({
  selector: 'app-image',
  templateUrl: './image.component.html',
  styleUrls: ['./image.component.css']
})
export class ImageComponent {

  DEFAULT_IMAGE_URL = 'assets/images/placeholder.jpg';
  selectedFile: File;
  inputImgSrc: string | ArrayBuffer = this.DEFAULT_IMAGE_URL;
  outputImgSrc: string | ArrayBuffer = this.DEFAULT_IMAGE_URL;

  constructor(private titleService: Title) { }

  ngOnInit(): void {
    this.titleService.setTitle("Face Mask Detection - Image");
  }

  async onFileChange(event) {
    if (event.target.files[0]) {
      let file: File = event.target.files[0];
      if (!this.imageFileType(file.type)) {
        alert('Please Select Image Files');
        return
      }
      this.selectedFile = file;
      this.inputImgSrc = await this.convertFiletoDataURI(this.selectedFile);
      this.outputImgSrc = this.DEFAULT_IMAGE_URL;
    }
  }

  imageFileType(type) {
    const filetypes = /jpeg|jpg|png/;
    const extname = filetypes.test(type.toLowerCase());
    return extname;
  }

  convertFiletoDataURI(file: File | Blob) {
    return new Promise<string | ArrayBuffer>((resolve) => {
      let reader: FileReader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = (response) => {
        resolve(response.target['result']);
      }
    })
  }

  onSubmit() {

    if (this.selectedFile === undefined) {
      return alert('Please Select A File');
    }

    let form: FormData = new FormData();
    form.append('Image', this.selectedFile);

    fetch("http://localhost:5000/image_feed", {
      method: "POST",
      body: form
    }).then((response) => {
      return response.blob()
    }).then(async (response) => {
      let url = await this.convertFiletoDataURI(response);
      this.outputImgSrc = url;
      this.selectedFile = undefined;
    })
      .catch((error) => {
        this.selectedFile = undefined;
        setTimeout(() => {
          alert(error.message);
        })
      })
  }

  onClear() {
    this.outputImgSrc = this.DEFAULT_IMAGE_URL;
    this.inputImgSrc = this.DEFAULT_IMAGE_URL;
    this.selectedFile = undefined;
  }

}
