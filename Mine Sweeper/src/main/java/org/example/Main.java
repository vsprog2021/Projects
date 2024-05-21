package org.example;

import java.awt.*;
import java.awt.event.*;
import java.io.Serial;
import java.util.Random;
import javax.swing.*;

class Minesweeper extends JFrame implements ActionListener {
    @Serial
    private static final long serialVersionUID = 1L;
    private final int rows;
    private final int cols;
    private final int bombs;
    private final int[][] board;
    private final JButton[][] buttons;
    private boolean gameOver;

    public Minesweeper(int rows, int cols, int bombs) {
        menu();
        int row = Integer.parseInt(JOptionPane.showInputDialog("Enter the number of rows:"));
        int col = Integer.parseInt(JOptionPane.showInputDialog("Enter the number of columns:"));
        int bomb = Integer.parseInt(JOptionPane.showInputDialog("Enter the number of bombs:"));
        this.rows = row;
        this.cols = col;
        this.bombs = bomb;
        rows = row;
        cols = col;
        bombs = bomb;
        board = new int[rows][cols];
        buttons = new JButton[rows][cols];
        gameOver = false;

        // Set up the frame
        setTitle("Minesweeper");
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setLayout(new GridLayout(rows, cols));

        // Add the buttons
        for (int i = 0; i < rows; i++) {
            for (int j = 0; j < cols; j++) {
                JButton button = new JButton();
                button.addActionListener(this);
                buttons[i][j] = button;
                add(button);
            }
        }

        // Set the size and show the frame
        setSize(500, 500);
        setVisible(true);

        // Generate the board
        generateBoard();
    }

    private void menu() {
        //TODO
    }

    // Reveal the button and its neighbors
    public void reveal(int row, int col) {
        JButton button = buttons[row][col];
        button.setEnabled(false);
        button.setText(Integer.toString(board[row][col]));
        if (board[row][col] == 0) {
            if (row > 0 && col > 0 && buttons[row - 1][col - 1].isEnabled()) reveal(row - 1, col - 1);
            if (row > 0 && buttons[row - 1][col].isEnabled()) reveal(row - 1, col);
            if (row > 0 && col < cols - 1 && buttons[row - 1][col + 1].isEnabled()) reveal(row - 1, col + 1);
            if (col > 0 && buttons[row][col - 1].isEnabled()) reveal(row, col - 1);
            if (col < cols - 1 && buttons[row][col + 1].isEnabled()) reveal(row, col + 1);
            if (row < rows - 1 && col > 0 && buttons[row + 1][col - 1].isEnabled()) reveal(row + 1, col - 1);
            if (row < rows - 1 && buttons[row + 1][col].isEnabled()) reveal(row + 1, col);
            if (row < rows - 1 && col < cols - 1 && buttons[row + 1][col + 1].isEnabled()) reveal(row + 1, col + 1);
        }
    }

    // Handle button clicks
    public void actionPerformed(ActionEvent e) {
        if (gameOver) {
            return;
        }

        JButton button = (JButton) e.getSource();
        int row = getRow(button);
        int col = getCol(button);

        if (board[row][col] == -1) {
            button.setBackground(Color.RED);
            gameOver = true;
            JOptionPane.showMessageDialog(this, "You lose!");
        } else {
            reveal(row, col);
            checkWin();
        }
    }

    // Get the row of a button
    public int getRow(JButton button) {
        for (int i = 0; i < rows; i++) {
            for (int j = 0; j < cols; j++) {
                if (buttons[i][j] == button) {
                    return i;
                }
            }
        }
        return -1;
    }

    // Get the column of a button
    public int getCol(JButton button) {
        for (int i = 0; i < rows; i++) {
            for (int j = 0; j < cols; j++) {
                if (buttons[i][j] == button) {
                    return j;
                }
            }
        }
        return -1;
    }

    // Generate the board
    public void generateBoard() {
        Random random = new Random();

        int bombsPlaced = 0;
        if (bombs > 0)
            while (bombsPlaced < bombs) {
                int row = random.nextInt(0, rows);
                int col = random.nextInt(0, cols);

                if (board[row][col] != -1) {
                    board[row][col] = -1;
                    bombsPlaced++;
                }
            }

        // Fill in the numbers
        for (int i = 0; i < rows; i++) {
            for (int j = 0; j < cols; j++) {
                if (board[i][j] != -1) {
                    int count = 0;
                    if (i > 0 && j > 0 && board[i - 1][j - 1] == -1) count++;
                    if (i > 0 && board[i - 1][j] == -1) count++;
                    if (i > 0 && j < cols - 1 && board[i - 1][j + 1] == -1) count++;
                    if (j > 0 && board[i][j - 1] == -1) count++;
                    if (j < cols - 1 && board[i][j + 1] == -1) count++;
                    if (i < rows - 1 && j > 0 && board[i + 1][j - 1] == -1) count++;
                    if (i < rows - 1 && board[i + 1][j] == -1) count++;
                    if (i < rows - 1 && j < cols - 1 && board[i + 1][j + 1] == -1) count++;
                    board[i][j] = count;
                }
            }
        }
        for(int i = 0; i < rows; i++)
        {
            for(int j = 0; j < cols; j++)
                System.out.print(board[i][j] + " ");
            System.out.println();
        }
    }



    // Check if the player has won
    private void checkWin() {
        int count = 0;
        for (int i = 0; i < rows; i++) {
            for (int j = 0; j < cols; j++) {
                if (buttons[i][j].isEnabled()) {
                    count++;
                }
            }
        }
        if (bombs > 0 && count == bombs) {
            gameOver = true;
            JOptionPane.showMessageDialog(this, "You win!");
        } else if (bombs == 0) {
            gameOver = true;
            JOptionPane.showMessageDialog(this, "You win!");
        }
    }
}
    public class Main {

        public static void main(String[] args) {
            Minesweeper game = new Minesweeper(0, 0, 0);
        }
    }