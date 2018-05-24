import * as React from "react";
import LoadingSpinner from "./Loader";
import { isNullOrUndefined } from "util";

// TODO maybe ajax call in app.tsx, only use selector to display images and whatnot
interface MyStates {
    isLoading: boolean;
    images: (number)[];
    folder: string;
}
interface MyProps {
    images: (string)[];
    selected?: number;
    folder: string;
}

function Image(props: any) {
    return (
        <div key={props.value} className="container" onClick={props.onClick} style={props.style}>
            <img className="frame" src={"static/" + props.folder + "/" + props.value + ".png"} />
            Image at {props.value} milliseconds
            </div>
    );
}

export class Selector extends React.Component<any, MyStates> {

    constructor(props: any) {
        super(props);
        this.state = {
            isLoading: true,
            images: [],
            folder: this.props.folder,
        };
    }
    componentWillReceiveProps(nextProps: any) {
        if (!(nextProps.folder == this.props.folder)) {
            this.setState({images: []});
            this.props = nextProps;
            this.componentDidMount();
        } else {
            this.setState({isLoading: false});
        }
    }

    renderImage(folder: string, value: number, selected: boolean): JSX.Element {
        let style: any = selected ? { background: "Chartreuse" } : {};
        return (<Image value={value} folder={folder} onClick={() => this.props.selected(value)} style={style} />);
    }

    // Thematically it makes more sense to have the app handle this rather than the selector...
    componentDidMount() {
        let xhr: XMLHttpRequest = new XMLHttpRequest();
        xhr.open("GET", "http://127.0.0.1:5000/_get_frames?folder=/" + this.props.folder);
        xhr.addEventListener("load", (e) => {
            // console.log("Folder: " + this.props.folder + "\n images: " + xhr.responseText);
            let images: (number)[] = JSON.parse(xhr.responseText).map((val: number) => val);
            this.setState({
                isLoading: false,
                images: images
            })
        })
        xhr.send();
    }

    render() {
        return (this.state.isLoading ? <LoadingSpinner /> : this.state.images.map((val: number) =>
            this.renderImage(this.props.folder, val, val == this.props.frame)
        ))
    }
}