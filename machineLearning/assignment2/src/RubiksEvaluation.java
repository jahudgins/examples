
import java.util.Random;

import opt.EvaluationFunction;
import shared.Instance;
import util.RandomFactory;
import util.linalg.Vector;

/**
 * A function that counts the ones in the data
 * @author Jonathan Hudgins jhudgins8@gatech.edu
 * @version 1.0
 */
public class RubiksEvaluation implements EvaluationFunction {
    /**
     * Count the number of cubes in the correct position
     * Each 3-bits represents a move:
     *      000 - left ccw
     *      001 - right cw
     *      010 - front ccw
     *      011 - back cw
     *      100 - top ccw
     *      101 - bottom cw
     *
     *      These are unnecessary, but allow us to use all of the 3 bit space
     *      110 - left cw
     *      111 - front cw
     *
     * Pieces:
     *
     * 0-7 corners
     *      0 - front, top, left
     *      1 - front, top, right
     *      2 - front, bottom, left
     *      3 - front, bottom, right
     *      4 - back, top, left
     *      5 - back, top, right
     *      6 - back, bottom, left
     *      7 - back, bottom, right
     *
     * 8-19 sides:
     *      8 - top, left
     *      9 - top, right
     *      10 - bottom, left
     *      11 - bottom, right
     *      12 - front, left
     *      13 - front, right
     *      14 - back, left
     *      15 - back, right
     *      16 - front, top
     *      17 - front, bottom
     *      18 - back, top
     *      19 - back, bottom
     *
     * @see opt.EvaluationFunction#value(opt.OptimizationData)
     */

    private enum Move {
        LeftCounterClockwise,
        RightClockwise,
        FrontCounterClockwise,
        BackClockwise,
        TopCounterClockwise,
        BottomClockwise,
        LeftClockwise,
        FrontClockwise,
    }

    private enum Piece {
        CornerFrontTopLeft,
        CornerFrontTopRight,
        CornerFrontBottomLeft,
        CornerFrontBottomRight,
        CornerBackTopLeft,
        CornerBackTopRight,
        CornerBackBottomLeft,
        CornerBackBottomRight,
        SideTopLeft,
        SideTopRight,
        SideBottomLeft,
        SideBottomRight,
        SideFrontLeft,
        SideFrontRight,
        SideBackLeft,
        SideBackRight,
        SideFrontTop,
        SideFrontBottom,
        SideBackTop,
        SideBackBottom,
    }
    
    public enum ValueType {
        CorrectCountEnd,
        Best,
        BestIfStopped,
        SumCorrect,
    }

    private Piece[] mPieces = new Piece[20];
    private int[] mOrientations = new int[20];
    private Random mRandom = RandomFactory.newRandom();
    private ValueType mValueType = ValueType.SumCorrect;
    private Instance solution;

    public RubiksEvaluation() {
        // initialize all positions
        for (int i=0; i<mPieces.length; i++) {
            mPieces[i] = Piece.values()[i];
            mOrientations[i] = 0;
        }
    }

    public void setValueType(ValueType valueType) {
        mValueType = valueType;
    }

    // perform n random moves scramble 
    public String scramble(int n) {
        StringBuilder stringBuilder = new StringBuilder();
        double[] solutionValues = new double[3 * n];
        for (int i=0; i<n; i++) {
            // apply move 3 times (same as applying opposite of the move)
            int move = mRandom.nextInt(8);
            for (int j=0; j<3; j++) {
                applyMove(mPieces, mOrientations, move);
            }
            stringBuilder.insert(0, (Move.values()[move]).toString()+",");
            // apply moves in reverse
            solutionValues[(n-i-1) * 3 + 0] = move >> 2;
            solutionValues[(n-i-1) * 3 + 1] = (move >> 1) & 0x1;
            solutionValues[(n-i-1) * 3 + 2] = move & 0x1;
        }
        solution = new Instance(solutionValues);
        return stringBuilder.toString();
    }

    public Instance knownSolution() {
        return solution;
    }

    private void movePieces(Piece[] pieces, int[] orientations, int orientationChange, int orientationMod,
            Piece p1, Piece p2, Piece p3, Piece p4)
    {
        Piece tempPiece = pieces[p1.ordinal()];
        pieces[p1.ordinal()] = pieces[p2.ordinal()];
        pieces[p2.ordinal()] = pieces[p3.ordinal()];
        pieces[p3.ordinal()] = pieces[p4.ordinal()];
        pieces[p4.ordinal()] = tempPiece;

        int tempOrientation = orientations[p1.ordinal()];
        orientations[p1.ordinal()] = (orientations[p2.ordinal()] + orientationChange + orientationMod) % orientationMod;
        orientations[p2.ordinal()] = (orientations[p3.ordinal()] + orientationChange + orientationMod) % orientationMod;
        orientations[p3.ordinal()] = (orientations[p4.ordinal()] + orientationChange + orientationMod) % orientationMod;
        orientations[p4.ordinal()] = (tempOrientation + orientationChange + orientationMod) % orientationMod;
    }


    private void applyMove(Piece[] pieces, int[] orientations, int move) {
        switch(Move.values()[move]) {
            case LeftCounterClockwise:
                // corners
                movePieces(pieces, orientations, +1, 4,
                        Piece.CornerFrontTopLeft,
                        Piece.CornerFrontBottomLeft,
                        Piece.CornerBackBottomLeft,
                        Piece.CornerBackTopLeft);

                // sides
                movePieces(pieces, orientations, +1, 2,
                        Piece.SideTopLeft,
                        Piece.SideFrontLeft,
                        Piece.SideBottomLeft,
                        Piece.SideBackLeft);

                break;

            case RightClockwise:
                // corners
                movePieces(pieces, orientations, -1, 4,
                        Piece.CornerFrontTopRight,
                        Piece.CornerFrontBottomRight,
                        Piece.CornerBackBottomRight,
                        Piece.CornerBackTopRight);

                movePieces(pieces, orientations, +1, 2,
                    Piece.SideTopRight,
                    Piece.SideFrontRight,
                    Piece.SideBottomRight,
                    Piece.SideBackRight);

                break;

            case FrontCounterClockwise:
                // corners
                movePieces(pieces, orientations, +1, 4,
                    Piece.CornerFrontTopRight,
                    Piece.CornerFrontBottomRight,
                    Piece.CornerFrontBottomLeft,
                    Piece.CornerFrontTopLeft);

                // sides
                movePieces(pieces, orientations, +1, 2,
                    Piece.SideFrontRight,
                    Piece.SideFrontBottom,
                    Piece.SideFrontLeft,
                    Piece.SideFrontTop);

                break;

            case BackClockwise:
                // corners
                movePieces(pieces, orientations, -1, 4,
                    Piece.CornerBackTopRight,
                    Piece.CornerBackBottomRight,
                    Piece.CornerBackBottomLeft,
                    Piece.CornerBackTopLeft);

                // sides
                movePieces(pieces, orientations, +1, 2,
                    Piece.SideBackRight,
                    Piece.SideBackBottom,
                    Piece.SideBackLeft,
                    Piece.SideBackTop);

                break;
                
            case TopCounterClockwise:
                // corners
                movePieces(pieces, orientations, +1, 4,
                    Piece.CornerFrontTopLeft,
                    Piece.CornerBackTopLeft,
                    Piece.CornerBackTopRight,
                    Piece.CornerFrontTopRight);

                // sides
                movePieces(pieces, orientations, +1, 2,
                    Piece.SideTopLeft,
                    Piece.SideBackTop,
                    Piece.SideTopRight,
                    Piece.SideFrontTop);

                break;
                
            case BottomClockwise:
                // corners
                movePieces(pieces, orientations, -1, 4,
                    Piece.CornerFrontBottomLeft,
                    Piece.CornerBackBottomLeft,
                    Piece.CornerBackBottomRight,
                    Piece.CornerFrontBottomRight);

                // sides
                movePieces(pieces, orientations, +1, 2,
                    Piece.SideBottomLeft,
                    Piece.SideBackBottom,
                    Piece.SideBottomRight,
                    Piece.SideFrontBottom);

                break;

            case LeftClockwise:
                // corners
                movePieces(pieces, orientations, -1, 4,
                    Piece.CornerFrontTopLeft,
                    Piece.CornerBackTopLeft,
                    Piece.CornerBackBottomLeft,
                    Piece.CornerFrontBottomLeft);

                // sides
                movePieces(pieces, orientations, +1, 2,
                    Piece.SideTopLeft,
                    Piece.SideBackLeft,
                    Piece.SideBottomLeft,
                    Piece.SideFrontLeft);

                break;
                
            case FrontClockwise:
                // corners
                movePieces(pieces, orientations, -1, 4,
                    Piece.CornerFrontTopRight,
                    Piece.CornerFrontTopLeft,
                    Piece.CornerFrontBottomLeft,
                    Piece.CornerFrontBottomRight);

                // sides
                movePieces(pieces, orientations, +1, 2,
                    Piece.SideFrontRight,
                    Piece.SideFrontTop,
                    Piece.SideFrontLeft,
                    Piece.SideFrontBottom);

                break;
        }
    }

    public int checkSolution(Piece[] pieces, int[] orientations) {
        int value = 0;
        for (int i=0; i<pieces.length; i++) {
            value += (pieces[i].ordinal() == i) ? 2 : 0;
            // value += (pieces[i].ordinal() == i) ? 1 : 0;
            value += (orientations[i] == 0) ? 1 : 0;
        }
        return value;
    }

    // value is number of correct pieces + number of correct orientations - number of moves
    // (so that we also try to find the shortest solution)
    public double value(Instance instance) {
        Vector data = instance.getData();
        Piece[] pieces = new Piece[mPieces.length];
        int[] orientations = new int[mPieces.length];
        
        System.arraycopy(mPieces, 0, pieces, 0, pieces.length);
        System.arraycopy(mOrientations, 0, orientations, 0, orientations.length);

        // start value at smallest possible
        double bestValue;
        switch (mValueType) {
            case CorrectCountEnd:   bestValue = -data.size()/3; break;
            case Best:              bestValue = -data.size()/3; break;
            case BestIfStopped:     bestValue = 0; break;
            case SumCorrect:        bestValue = 0; break;
            default:                bestValue = 0; break;
        }


        int moveCount;
        int totalMoves = data.size()/3;
        double sumValue = 0;
        for (moveCount = 0; moveCount < totalMoves; moveCount++) {
            int move = 0;
            for (int j=0; j<3; j++) {
                move = (move << 1) | ((int)data.get(3*moveCount+j));
            }
            applyMove(pieces, orientations, move);

            // if we have already reached the solution, we have maximum value for pieces and orientation
            // and only number of moves determines our value
            double value = checkSolution(pieces, orientations);
            if (value == 2 * pieces.length + orientations.length) {
                if (mValueType == ValueType.SumCorrect) {
                    // sum remaining as max value
                    // add an extra bonus to make sure a valid solution always has
                    // higher value than moves that don't solve
                    return sumValue + value * (2 * totalMoves - moveCount);
                } else {
                    return value - moveCount;
                }
            }
            sumValue += value;
            if (mValueType == ValueType.BestIfStopped) {
                value -= moveCount;
            }
            if (value > bestValue) {
                bestValue = value;
            }
        }
        switch (mValueType) {
            case CorrectCountEnd:           return checkSolution(pieces, orientations) - moveCount;
            case Best:          return bestValue - moveCount;
            case BestIfStopped: return bestValue;
            case SumCorrect:    return sumValue;
            default:            return sumValue;
        }
    }

    public boolean solvesPuzzle(Instance instance) {
        Vector data = instance.getData();
        Piece[] pieces = new Piece[mPieces.length];
        int[] orientations = new int[mPieces.length];
        
        System.arraycopy(mPieces, 0, pieces, 0, pieces.length);
        System.arraycopy(mOrientations, 0, orientations, 0, orientations.length);

        int moveCount;
        for (moveCount = 0; moveCount < data.size()/3; moveCount++) {
            int move = 0;
            for (int j=0; j<3; j++) {
                move = (move << 1) | ((int)data.get(3*moveCount+j));
            }
            applyMove(pieces, orientations, move);

            if (checkSolution(pieces, orientations) == 2 * pieces.length + orientations.length) {
                return true;
            }
        }
        return false;
    }

    public String movesToString(Instance instance) {
        StringBuilder stringBuilder = new StringBuilder();
        Vector data = instance.getData();
        int moveCount;
        for (moveCount = 0; moveCount < data.size()/3; moveCount++) {
            int move = 0;
            for (int j=0; j<3; j++) {
                move = (move << 1) | ((int)data.get(3*moveCount+j));
            }
            stringBuilder.append((Move.values()[move]).toString() + ",");
        }
        return stringBuilder.toString();
    }
}
