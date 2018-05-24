import * as React from "react";
import { Upload } from "./Upload";
import { Cropper } from "./Cropper";
import * as ReactCrop from 'react-image-crop';
import { Selector } from "./Selector";
import { Router, Route } from "react-router";
import LoadingSpinner from "./Loader";

// export interface UploadProps { }

interface MyStates {
    folders: (string)[]; // Holds history of folders
    frames: (number)[]; //  Holds history of frames
    stage: number;
    current_folder?: string;
    current_frame?: number;
    name?: string;
    isLoading?: boolean;
    narrow_folders?: (string)[];
    crop?: ReactCrop.Crop;
    picdims?: ReactCrop.Crop;
    textdims?: ReactCrop.Crop;
    predicted_textdims?: { 'xmin': number, 'ymin': number, 'xmax': number, 'ymax': number };
    predicted_picdims?: { 'xmin': number, 'ymin': number, 'xmax': number, 'ymax': number };
    narrow: boolean;
    email?: string;
}
enum Stage {
    "upload",
    "select_init",
    "select_end",
    "crop_pic",
    "crop_text",
    "end",
    "crop",
    "narrow",
}
export class App extends React.Component<any, MyStates> {
    constructor(props: any) {
        super(props)
        // https://medium.com/@esamatti/react-js-pure-render-performance-anti-pattern-fb88c101332f
        this.state = {
            stage: 0,
            folders: [],
            frames: [],
            narrow_folders: ['', ''],
            isLoading: false,
            narrow: false,
            email: "Please enter your email",
        }
        this.uploadClickHandler = this.uploadClickHandler.bind(this);
        this.frameSelected = this.frameSelected.bind(this);
        this.reset = this.reset.bind(this);
    }

    uploadClickHandler(file: File): void {
        if (!file) {
            // No file uploaded, do nothing
            return;
        } else {
            let formData: FormData = new FormData();
            formData.append("video", file);
            let xhr: XMLHttpRequest = new XMLHttpRequest();
            xhr.open("POST", "http://127.0.0.1:5000/_upload", true);
            xhr.addEventListener("load", (e) => {
                // File upload completed
                if (xhr.responseText) {
                    const folders: (string)[] = this.state.folders.slice();
                    folders.push(xhr.responseText.split("/")[1])
                    folders.push(xhr.responseText);
                    this.setState({
                        stage: Stage.select_init, folders: folders, name: file.name,
                        isLoading: false, current_folder: folders[folders.length - 1]
                    })
                } else {
                    console.log("failed to split video");
                }
            });
            this.setState({ isLoading: true });
            xhr.send(formData);
        }
    }

    frameSelected(frame: number): void {
        this.setState({
            current_frame: frame
        });
    }

    reset(): void {
        this.setState({
            current_folder: null,
            stage: 0,
            folders: [],
            frames: [],
            narrow_folders: ['', ''],
            isLoading: false,
            narrow: false
        })
    }

    next_stage(stage?: number): void {
        if (this.state.isLoading == true) return
        // Determines the next stage. Could potentially change this into a switch 
        // and case statement
        this.setState({ isLoading: true, narrow: false });
        let next_stage = this.state.stage + 1;
        if (stage == Stage.narrow) {
            if (this.state.current_frame == null) return;
            // This is for the narrowing selection. The folder used to narrow the selection IS NOT
            // added into the history
            let xhr: XMLHttpRequest = new XMLHttpRequest();
            xhr.open('POST', 'http://127.0.0.1:5000/_split_mid', true);
            xhr.setRequestHeader('Content-Type', 'application/json');
            xhr.addEventListener('load', (e) => {
                if (xhr.responseText) {
                    const narrow_folders: (string)[] = this.state.narrow_folders.slice();
                    if (next_stage == Stage.select_end) {
                        narrow_folders[0] = xhr.responseText;
                    } else {
                        narrow_folders[1] = xhr.responseText;
                    }
                    this.setState({
                        current_folder: xhr.responseText, current_frame: null, isLoading: false,
                        narrow_folders: narrow_folders, narrow: true
                    });
                }
            });
            xhr.send(JSON.stringify({ name: this.state.name, folder: this.state.folders[0], init: this.state.current_frame }))
        } else if (next_stage == Stage.select_init || next_stage == Stage.select_end) {
            if (this.state.current_frame == null) return;
            let xhr: XMLHttpRequest = new XMLHttpRequest();
            xhr.open('POST', 'http://127.0.0.1:5000/_split_end', true);
            xhr.setRequestHeader('Content-Type', 'application/json');
            xhr.addEventListener('load', (e) => {
                if (xhr.responseText) {
                    const folders: (string)[] = this.state.folders.slice();
                    const frames: (number)[] = this.state.frames.slice();
                    frames.push(this.state.current_frame)
                    folders.push(xhr.responseText);
                    this.setState({
                        folders: folders, current_frame: null, isLoading: false,
                        frames: frames, stage: this.state.stage + 1, current_folder: folders[folders.length - 1]
                    });
                }
            });
            xhr.send(JSON.stringify({ name: this.state.name, folder: this.state.folders[0] }))
        } else if (next_stage == Stage.crop_pic) {
            const frames: (number)[] = this.state.frames.slice();
            frames.push(this.state.current_frame);
            let xhr: XMLHttpRequest = new XMLHttpRequest();
            xhr.open('GET', 'http://127.0.0.1:5000/_predict?folder=' + (this.state.narrow_folders[0] ? this.state.narrow_folders[0] : this.state.folders[1])
                + "&frame=" + this.state.frames[0], true);
            xhr.addEventListener('load', (e) => {
                let dims = JSON.parse(xhr.responseText);
                let pdims = dims['pdims'];
                this.setState({
                    stage: this.state.stage + 1, frames: frames, isLoading: false,
                    predicted_picdims: pdims, predicted_textdims: dims['tdims'],
                    crop: {
                        'x': pdims['xmin'] / 8.54, 'y': pdims['ymin'] / 5.04, 'width': (pdims['xmax'] - pdims['xmin']) / 8.54,
                        'height': (pdims['ymax'] - pdims['ymin']) / 5.04
                    }
                });
            });
            xhr.send();
        } else if (next_stage == Stage.crop_text) {
            let tdims = this.state.predicted_textdims;
            this.setState({
                stage: this.state.stage + 1, isLoading: false, picdims: this.state.crop,
                crop: { 'x': tdims['xmin'] / 8.54, 'y': tdims['ymin'] / 5.04, 'width': (tdims['xmax'] - tdims['xmin']) / 8.54, 'height': (tdims['ymax'] - tdims['ymin']) / 5.04 }
            })
        } else if (next_stage == Stage.end) {
            let xhr = new XMLHttpRequest();
            xhr.open('POST', 'http://127.0.0.1:5000/_to_csv')
            xhr.setRequestHeader('Content-Type', 'application/json');
            xhr.send(JSON.stringify({
                picdims: this.state.picdims, name: this.state.name,
                init: this.state.frames[0], end: this.state.frames[1], folder: this.state.folders[0],
                textdims: this.state.crop,
                email: this.state.email
            }));
            // this.setState({ stage: this.state.stage + 1, isLoading: false, textdims: this.state.crop })
            this.reset();
        }
    }

    back(stage: number) {
        this.setState({ isLoading: true });
        switch (stage) {
            case (Stage.select_init):
                if (this.state.narrow) {
                    this.setState({ current_folder: this.state.folders[1], narrow: false, narrow_folders: ["", ""], isLoading: false })
                    return
                } else this.reset();
                break;
            case (Stage.select_end):
                if (this.state.narrow) {
                    const narrow_folders: (string)[] = this.state.narrow_folders.slice();
                    narrow_folders[1] = '';
                    this.setState({ current_folder: this.state.folders[2], narrow: false, narrow_folders: narrow_folders })
                }
                const frames = this.state.frames.slice();
                frames.pop();
                const folders: (string)[] = this.state.folders.slice();
                folders[2] = '';
                this.setState({ stage: stage - 1, frames: frames, current_folder: this.state.folders[1], isLoading: false, folders: folders })
                break;
            case (Stage.crop_pic):
                this.setState({ stage: stage - 1, isLoading: false })
                break;
            case (Stage.crop_text):
                let pdims = this.state.predicted_picdims;
                this.setState({
                    stage: stage - 1, isLoading: false, crop:
                        {
                            'x': pdims['xmin'] / 8.54, 'y': pdims['ymin'] / 5.04, 'width': (pdims['xmax'] - pdims['xmin']) / 8.54,
                            'height': (pdims['ymax'] - pdims['ymin']) / 5.04
                        }
                });

            default:

        }
    }

    updateEmail(email: React.ChangeEvent<HTMLInputElement>) {
        this.setState({ email: email.target.value });
    }

    render() {
        let next_stage = this.state.stage + 1;
        let path: string;
        let source: string;
        const folder = this.state.folders.slice();
        console.log(this.state);
        let component: JSX.Element;
        let instruction: JSX.Element;
        let header: JSX.Element;
        switch (this.state.stage) {
            case Stage.upload:
                header = <h1>Upload</h1>;
                instruction = <p>Pick a mp4 to upload</p>;
                component = <Upload onClick={(file: File) => this.uploadClickHandler(file)} />;
                break;

            case Stage.narrow:
            case Stage.select_end:
            case Stage.select_init:
                header = <h1> Frame selection </h1>;
                instruction = <p> Select the beginning or end frame (The first and last frames where you see text and images).
                    If you want to be more accurate, pick a frame and click narrow. This displays the frames around the selected frame
                    at a 5 ms interval. </p>
                component = <Selector folder={this.state.current_folder}
                    selected={(i: number) => this.frameSelected(i)}
                    frame={this.state.current_frame}
                />;
                break;
            case Stage.crop_pic:
            case Stage.crop_text:
                header = <h1> Crop the image and the text</h1>
                instruction = <p> The cropping is already predicted, just improve it. Enter your email and click submit. After this stage you'll be sent back to the main page. The converted
                    csv will be emailed to you shortly</p>
                path = this.state.narrow_folders[0] ? this.state.narrow_folders[0] : this.state.folders[1]
                source = "static/" + path + "/" + this.state.frames[0] + ".png";
                component = <Cropper src={source}
                    onChange={(crop) => { this.setState({ crop }) }} crop={this.state.crop}
                    keepSelection={true} />
                break;
            case Stage.end:
                component = <div>{JSON.stringify(this.state)}</div>;
                break;
        }

        return (
            <div id="box">
                <div id="header">
                    {header}
                    {instruction}
                    <button id="button_home" onClick={() => this.reset()}>Home</button>
                    <button id="button_next" onClick={() => this.next_stage(next_stage)}>{this.state.stage != Stage.crop_text ? "Next" : "Submit"}</button>
                    {(this.state.stage == Stage.select_init || this.state.stage == Stage.select_end)
                        ? <button id="narrow" onClick={() => this.next_stage(Stage.narrow)}>Narrow</button> : null}
                    {(this.state.stage != Stage.upload) ?
                        <button id="back" onClick={() => {
                            this.back(this.state.stage);
                        }}>Back</button> : null}
                    {this.state.stage == Stage.crop_text ?  <div> Input your email: <input value={this.state.email} onChange={evt => this.updateEmail(evt)} /> </div>: null}
                </div>
                <div id="main">
                    {this.state.isLoading ? <LoadingSpinner /> : component}
                </div>
            </div>)
    }
}