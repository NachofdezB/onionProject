import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

class CalculadoraTest {

    @BeforeEach
    void setUp() {
    }

    @AfterEach
    void tearDown() {
    }

    // Pruebas para el método dividir
    @Test
    /**
     * Método dividir dividir numeros enteros
     */
    public void testDividir() {
        Calculadora calculadora = new Calculadora();
        assertEquals(2.0, calculadora.dividir(6.0, 3.0));
    }

    @Test
    /**
     * Método dividir dividir entre cero
     */
    public void testDividirPorCero() {
        Calculadora calculadora = new Calculadora();
        assertEquals(0.0, calculadora.dividir(6.0, 0.0));
    }

    @Test
    /**
     * Método dividir dividir negtivos entre positivos
     */
    public void testDividirNegativoPositivo() {
        Calculadora calculadora = new Calculadora();
        assertEquals(-1.0, calculadora.dividir(-6.0, 6.0));
    }
}