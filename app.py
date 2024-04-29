import argparse
import yaml
import yt_dlp
import gradio as gr

def load_config(file_path):
    """
    Loads the configuration from the specified file path.

    Args:
        file_path (str): The path to the configuration file.

    Returns:
        dict: The loaded configuration data.
    """
    with open(file_path, "r") as file:
        data = yaml.safe_load(file)
    return data

def download_video(url: str, save_path: str, proxy: str = "127.0.0.1:1080") -> str:
    """
    Download a video from the given URL and save it to the specified path.

    Args:
        url (str): The URL of the video.
        save_path (str): The path where the downloaded video will be saved.
        proxy (str, optional): The proxy to be used for the download. Defaults to "127.0.0.1:1080".

    Returns:
        str: Path of the downloaded video for playback.
    """
    # Set the options for the YouTube downloader
    ydl_opts = {
        "proxy": proxy,
        "format": "best",
        "restrict-filenames": True,
        "outtmpl": f"{save_path}/%(title)s.%(ext)s",
        
    }
    
    # Create a context manager for the YouTube downloader and download the video
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        video_title = ydl.prepare_filename(info_dict)
        ydl.download([url])
        video_title = video_title[:-4]
    # Assuming single video download, format the path for use in the web player
    downloaded_path = ydl.prepare_filename({'title': video_title, 'ext': 'mp4'})
    return downloaded_path

def main(config: dict) -> None:
    """
    Runs the YouTube Video Downloader interface with video playback.

    Args:
        config (dict): Configuration dictionary containing input_url,
        output_path, and proxy.

    Returns:
        None
    """
    config_proxy = "{}:{}".format(config["proxy"], config["port"])

    input_url = gr.Textbox(label="Enter YouTube video URL")
    output_path = gr.Textbox(
        label="Enter save path for video", placeholder=config["output_folder"],visible=False
    )
    proxy = gr.Textbox(label="Enter Proxy", placeholder=config_proxy, visible=False)

    output_video = gr.Video(label="Downloaded Video")

    def wrapper_function(url, path, proxy):
        video_path = download_video(url, path, proxy)
        return video_path

    demo = gr.Interface(
        fn=wrapper_function,
        inputs=[input_url, output_path, proxy],
        outputs=output_video,
        title="YouTube Video Downloader",
        description="Download YouTube videos using yt_dlp and play them.",
        theme="compact",
    )

    demo.launch(share=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config_path",
        type=str,
        default="config.yaml",
        help="configuration file path"
    )
    args = parser.parse_args()
    config = load_config(args.config_path)
    main(config)