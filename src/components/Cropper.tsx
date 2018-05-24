import * as React from "react";
import * as ReactCrop from "react-image-crop";

interface MyProps {
    src: string;
    onChange: (crop: ReactCrop.Crop, pixelCrop?: ReactCrop.PixelCrop) => void;
    crop?: ReactCrop.Crop;
    keepSelection?: boolean;
}
interface MyStates {
    src: string;
    onChange: (crop: ReactCrop.Crop, pixelCrop: ReactCrop.PixelCrop) => void;
    crop?: ReactCrop.Crop;
    keepSelection?: boolean;
}
export class Cropper extends React.Component<MyProps, MyStates> {
    // This is just a wrapper for the ReactCrop class
    constructor(props: any) {
        super(props);
    }

    


    render() {
        let crop: ReactCrop.Crop = this.props.crop == null ? {x: null, y: null, width: null, height: null} : this.props.crop;
        return (<div id="crop">
                <ReactCrop src={this.props.src}
                    onChange={this.props.onChange} crop={this.props.crop}
                    keepSelection={true} />
                <br/>
                X
                <input readOnly value={crop['x']|0}/> Y
                <input readOnly value={crop['y']|0}/> W
                <input readOnly value={crop['width']|0}/> H
                <input readOnly value={crop['height']|0}/> 
            </div>
            );

    }

}
