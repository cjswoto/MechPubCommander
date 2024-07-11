# MechPugCommander

**MechPugCommander** is an unofficial indie-developed companion application for the game MechWarrior Online. This tool is designed to help players access information about their friends, teammates, and opponents in-game without disrupting their gameplay.

## Features

- **Real-time combatant analysis**: Provides live data on your opponents to identify strengths and weaknesses.
- **Ally coordination network**: Helps to keep track of your teammates' status and positions.
- **Enemy force composition intel**: Offers detailed information on the composition of enemy forces.
- **Adaptive HUD integration**: Integrates seamlessly with your game's HUD for real-time updates.
- **Stealth hotkey activation**: Allows you to toggle the application visibility without disrupting gameplay.
- **Automatic retrieval of team and enemy names from screenshots**: Uses OCR to automatically extract names from screenshots.
- **Comprehensive stats tracking for friends and foes**: Keeps detailed statistics on both friends and enemies.
- **Customizable settings and user preferences**: Allows users to customize various aspects of the application.

## Installation

1. **Download Tesseract-OCR**: You need to have Tesseract-OCR installed. Download it from [here](https://github.com/tesseract-ocr/tesseract).
2. **Clone the repository**: 
    ```bash
    git clone https://github.com/yourusername/MechPugCommander.git
    ```
3. **Install the required Python packages**:
    ```bash
    pip install -r requirements.txt
    ```
4. **Run the application**:
    ```bash
    python mechpugcommander.py
    ```

## Usage

1. **Setup**:
   - Configure the application settings by specifying the path to the Tesseract-OCR executable and where to save the output files.
   
2. **Capturing Data**:
   - Take a screenshot of your MechWarrior Online HUD.
   - Open MechPugCommander and use the "Browse" button to select the screenshot.
   - Choose whether the screenshot is for "Team" or "Enemy" and enable or disable pre-processing as needed.
   - Click the "Process" button to extract names from the screenshot. The names will be saved in `team.txt` or `enemy.txt` depending on your selection.

3. **Viewing and Using Data**:
   - Start the application and ensure you are logged in with your MechWarrior Online credentials.
   - Use the "Import Teams" button to load team and enemy names from the saved files.
   - Use the "Refresh Stats" button to fetch and display statistics for all players.

4. **Customizing Settings**:
   - Open the settings dialog from the main application window.
   - Set your in-game name, the path to the Tesseract-OCR executable, and the paths to your team and enemy files.
   - Save the settings and restart the application to apply changes.

5. **Advanced Features**:
   - **Stealth Hotkey Activation**: Use the hotkey combination `Ctrl+Alt+Insert` to toggle the visibility of the application window without disrupting gameplay.
   - **Adaptive HUD Integration**: The application integrates with your HUD to provide real-time updates and notifications during gameplay.
   - **Comprehensive Stats Tracking**: Track detailed statistics for both friends and enemies, including win/loss ratios, kill/death ratios, and average match scores.

## Contributing

1. Fork the repository.
2. Create your feature branch:
    ```bash
    git checkout -b feature/AmazingFeature
    ```
3. Commit your changes:
    ```bash
    git commit -m 'Add some AmazingFeature'
    ```
4. Push to the branch:
    ```bash
    git push origin feature/AmazingFeature
    ```
5. Open a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

The code for MechPugCommander was 100% developed by ChatGPT3.54o & Sonnet 3.0.

## Disclaimer

MechPugCommander is an independent development and is not affiliated with MechWarrior Online or PGI. This application is free and intended only for personal use by the developer and the Black Swamp Assassins MWO Unit.
