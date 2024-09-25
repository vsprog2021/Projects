import net.sf.clipsrules.jni.*;
import javax.swing.*;
import java.awt.*;
import java.awt.event.*;
import java.io.*;
import java.nio.file.*;

class Calculator {
    private static int buttonPressCount = 0;
    private static JFrame mainFrame;
    private boolean finished = false;

    public Calculator() {
        func();
    }

    public void func() {
        mainFrame = new JFrame("Main Window");
        mainFrame.setLayout(null);
        mainFrame.setSize(600, 600);
        mainFrame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);

        JButton startButton = new JButton("Start");
        startButton.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent e) {
                openSizeSelector();}
        });
        int width = (int) (mainFrame.getWidth() * 0.4);
        int height = (int) (mainFrame.getHeight() * 0.4);
        int x = (mainFrame.getWidth() - width) / 2;
        int y = (mainFrame.getHeight() - height) / 2;
        startButton.setBounds(x, y, width, height);
        mainFrame.getContentPane().add(startButton);
        mainFrame.setVisible(true);
    }

    private void openSizeSelector() {
        JFrame sizeSelectorWindow = new JFrame("Select Size");
        sizeSelectorWindow.setSize(200, 200);
        sizeSelectorWindow.setLayout(new GridLayout(3, 1));

        JLabel label = new JLabel("Selectati size-ul", SwingConstants.CENTER);
        sizeSelectorWindow.getContentPane().add(label);

        SpinnerNumberModel model = new SpinnerNumberModel(2, 2, 5, 1);
        JSpinner spinner = new JSpinner(model);
        sizeSelectorWindow.getContentPane().add(spinner);

        JButton confirmButton = new JButton("Confirm");
        confirmButton.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent e) {
                int size = (int) spinner.getValue();
                sizeSelectorWindow.dispose();
                sendSizeToFile(size);
                openCalculator(size);
            }
        });
        sizeSelectorWindow.getContentPane().add(confirmButton);
        sizeSelectorWindow.setVisible(true);
    }

    private static void sendSizeToFile(int size) {
        try (FileWriter writer = new FileWriter("C:\\Programe\\SSS\\PBR\\Proiect_CLIPS\\input-size.txt")) {
            writer.write(String.valueOf(size));
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    private static void sendBoardToFile(String value) {
        try (FileWriter writer = new FileWriter("C:\\Programe\\SSS\\PBR\\Proiect_CLIPS\\input-board.txt", true)) {
            writer.write(String.valueOf(value));
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    private void openCalculator(int size) {
        JFrame calculatorWindow = new JFrame("Calculator");
        calculatorWindow.setSize(600, 600);
        calculatorWindow.setLayout(new GridLayout(5, 3));

        String[] buttons = {"1", "2", "3", "4", "5", "6", "7", "8", "9", "*", "0", "*"};
        StringBuilder inputBuffer = new StringBuilder();
        try (FileWriter writer = new FileWriter("C:\\Programe\\SSS\\PBR\\Proiect_CLIPS\\input-board.txt")) {
            writer.write("");
        } catch (IOException e) {
            e.printStackTrace();
        }


        for (String btnText : buttons) {
            JButton button = new JButton(btnText);
            button.addActionListener(new ActionListener() {
                public void actionPerformed(ActionEvent e) {
                    if (btnText.matches("\\d")) {
                        inputBuffer.append(btnText);
                    }
                    else if (btnText.equals("*")) {
                        buttonPressCount++;
                        if(buttonPressCount < Math.pow(size, 2)) {
                            sendBoardToFile(inputBuffer + " ");
                            inputBuffer.setLength(0);
                        }
                    }
                    if (buttonPressCount >= Math.pow(size, 2)) {
                        sendBoardToFile(inputBuffer + "\n");
                        inputBuffer.setLength(0);
                        calculatorWindow.dispose();
                        mainFrame.dispose();
                        Environment clips = new Environment();
                        try {
                            clips.clear();
                            clips.load("c:\\Programe\\SSS\\PBR\\Proiect_CLIPS\\Proiect_N-Puzzle-Java.clp");
                            clips.reset();
                            clips.run();
                        } catch (CLIPSException f) {
                            f.printStackTrace();
                        }
                    }
                }
            });
            calculatorWindow.getContentPane().add(button);
        }
        calculatorWindow.setVisible(true);
    }
}

public class ClipsRunner {
    public static void main(String[] args) throws InterruptedException {
        Calculator calc = new Calculator();
    }
}
