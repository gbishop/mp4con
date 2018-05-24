import * as React from "react";


export class Upload extends React.Component<any, any> {
    constructor(props: any) {
        super(props);
        this.buttonClickHandler = this.buttonClickHandler.bind(this);
    }


    file: File = null;

    buttonClickHandler() {
        this.props.onClick(this.file);
    }

    fileUploadHandler(event: React.ChangeEvent<HTMLInputElement>): void {
        this.file = event.target.files[0];
    }


    render() {
        return (
            <div>
                <input  type="file" name="video" onChange={(e) => this.fileUploadHandler(e)} />
                <button className="btn-default" onClick={ this.buttonClickHandler }>
                    {"Upload"}
                </button>
                </div>
        );
    }
}