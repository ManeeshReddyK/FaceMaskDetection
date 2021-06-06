import { Component, OnInit } from '@angular/core';
import { Title } from '@angular/platform-browser';

@Component({
  selector: 'app-video',
  templateUrl: './video.component.html',
  styleUrls: ['./video.component.css']
})
export class VideoComponent implements OnInit {

  DEFAULT_IMAGE_URL = 'assets/images/mask.png';
  videoUrl: any;
  inputImgSrc: string | ArrayBuffer = this.DEFAULT_IMAGE_URL;
  flag: boolean = false;
  on: boolean = false;
  uploadButton: boolean;
  fileSelected: any;
  image: any

  constructor(private titleService: Title) { }

  ngOnInit(): void {
    this.titleService.setTitle("Face Mask Detection - Video");
  }

  onCamera() {
    this.on = true;
    this.flag = true;
    this.videoUrl = "http://localhost:5000/video_feed";
  }

  offCamera() {
    this.on = false;
    this.flag = false;
    fetch("http://localhost:5000/video_release")
      .then(() => { })
      .catch(() => { })
  }

}
