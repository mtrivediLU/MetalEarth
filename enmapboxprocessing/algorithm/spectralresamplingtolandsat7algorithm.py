from enmapboxprocessing.algorithm.spectralresamplingbyresponsefunctionconvolutionalgorithmbase import \
    SpectralResamplingByResponseFunctionConvolutionAlgorithmBase
from typeguard import typechecked


@typechecked
class SpectralResamplingToLandsat7Algorithm(SpectralResamplingByResponseFunctionConvolutionAlgorithmBase):
    A_CODE = True

    def displayName(self) -> str:
        return 'Spectral resampling (to Landsat 7 ETM+)'

    def shortDescription(self) -> str:
        link = self.htmlLink(
            'https://www.usgs.gov/core-science-systems/nli/landsat/landsat-satellite-missions',
            'Landsat')
        return super().shortDescription() + f'\nFor more information see the {link} missions website.'

    def code(self):
        from collections import OrderedDict

        responses = OrderedDict()
        responses['Blue'] = [(435, 0.016), (436, 0.027), (437, 0.048), (438, 0.094), (439, 0.167), (440, 0.287),
                             (441, 0.459), (442, 0.605), (443, 0.728), (444, 0.769), (445, 0.792), (446, 0.821),
                             (447, 0.857), (448, 0.857), (449, 0.862), (450, 0.839), (451, 0.845), (452, 0.81),
                             (453, 0.802), (454, 0.804), (455, 0.779), (456, 0.798), (457, 0.816), (458, 0.876),
                             (459, 0.888), (460, 0.901), (461, 0.918), (462, 0.896), (463, 0.903), (464, 0.888),
                             (465, 0.89), (466, 0.863), (467, 0.86), (468, 0.842), (469, 0.866), (470, 0.875),
                             (471, 0.881), (472, 0.888), (473, 0.898), (474, 0.879), (475, 0.884), (476, 0.907),
                             (477, 0.928), (478, 0.932), (479, 0.955), (480, 0.958), (481, 0.948), (482, 0.952),
                             (483, 0.956), (484, 0.98), (485, 0.98), (486, 0.975), (487, 0.973), (488, 0.977),
                             (489, 0.958), (490, 0.965), (491, 0.957), (492, 0.952), (493, 0.973), (494, 0.974),
                             (495, 0.995), (496, 0.986), (497, 0.986), (498, 0.994), (499, 1.0), (500, 0.99),
                             (501, 0.99), (502, 0.976), (503, 0.983), (504, 0.976), (505, 0.983), (506, 0.96),
                             (507, 0.973), (508, 0.964), (509, 0.975), (510, 0.96), (511, 0.932), (512, 0.853),
                             (513, 0.684), (514, 0.486), (515, 0.293), (516, 0.15), (517, 0.073), (518, 0.036),
                             (519, 0.019), (520, 0.009)]
        responses['Green'] = [(502, 0.001), (503, 0.002), (504, 0.002), (505, 0.003), (506, 0.005), (507, 0.009),
                              (508, 0.014), (509, 0.024), (510, 0.026), (511, 0.041), (512, 0.06), (513, 0.088),
                              (514, 0.126), (515, 0.174), (516, 0.236), (517, 0.308), (518, 0.388), (519, 0.472),
                              (520, 0.552), (521, 0.621), (522, 0.676), (523, 0.716), (524, 0.743), (525, 0.759),
                              (526, 0.769), (527, 0.779), (528, 0.79), (529, 0.805), (530, 0.822), (531, 0.842),
                              (532, 0.861), (533, 0.878), (534, 0.893), (535, 0.905), (536, 0.916), (537, 0.924),
                              (538, 0.933), (539, 0.942), (540, 0.947), (541, 0.951), (542, 0.953), (543, 0.952),
                              (544, 0.951), (545, 0.952), (546, 0.951), (547, 0.951), (548, 0.952), (549, 0.952),
                              (550, 0.953), (551, 0.951), (552, 0.95), (553, 0.95), (554, 0.951), (555, 0.954),
                              (556, 0.96), (557, 0.966), (558, 0.968), (559, 0.965), (560, 0.959), (561, 0.951),
                              (562, 0.944), (563, 0.937), (564, 0.932), (565, 0.933), (566, 0.935), (567, 0.937),
                              (568, 0.94), (569, 0.945), (570, 0.951), (571, 0.955), (572, 0.957), (573, 0.956),
                              (574, 0.957), (575, 0.955), (576, 0.952), (577, 0.954), (578, 0.958), (579, 0.963),
                              (580, 0.973), (581, 0.981), (582, 0.988), (583, 0.995), (584, 1.0), (585, 1.0),
                              (586, 0.994), (587, 0.983), (588, 0.969), (589, 0.954), (590, 0.942), (591, 0.936),
                              (592, 0.932), (593, 0.928), (594, 0.924), (595, 0.912), (596, 0.883), (597, 0.834),
                              (598, 0.763), (599, 0.674), (600, 0.574), (601, 0.473), (602, 0.38), (603, 0.3),
                              (604, 0.235), (605, 0.185), (606, 0.146), (607, 0.117), (608, 0.094), (609, 0.077),
                              (610, 0.062), (611, 0.052), (612, 0.042), (613, 0.033), (614, 0.026), (615, 0.021),
                              (616, 0.016), (617, 0.012), (618, 0.009), (619, 0.007), (620, 0.005), (621, 0.004),
                              (622, 0.003), (623, 0.002), (624, 0.001)]
        responses['Red'] = [(619, 0.001), (620, 0.002), (621, 0.003), (622, 0.006), (623, 0.013), (624, 0.025),
                            (625, 0.047), (626, 0.083), (627, 0.137), (628, 0.211), (629, 0.306), (630, 0.419),
                            (631, 0.545), (632, 0.674), (633, 0.788), (634, 0.873), (635, 0.921), (636, 0.941),
                            (637, 0.943), (638, 0.942), (639, 0.939), (640, 0.937), (641, 0.935), (642, 0.935),
                            (643, 0.938), (644, 0.943), (645, 0.949), (646, 0.953), (647, 0.961), (648, 0.968),
                            (649, 0.971), (650, 0.973), (651, 0.974), (652, 0.972), (653, 0.969), (654, 0.963),
                            (655, 0.958), (656, 0.956), (657, 0.955), (658, 0.955), (659, 0.956), (660, 0.962),
                            (661, 0.969), (662, 0.977), (663, 0.983), (664, 0.988), (665, 0.993), (666, 0.996),
                            (667, 0.997), (668, 0.999), (669, 1.0), (670, 1.0), (671, 0.998), (672, 0.996),
                            (673, 0.995), (674, 0.993), (675, 0.992), (676, 0.991), (677, 0.989), (678, 0.988),
                            (679, 0.984), (680, 0.977), (681, 0.97), (682, 0.96), (683, 0.949), (684, 0.94),
                            (685, 0.932), (686, 0.919), (687, 0.898), (688, 0.863), (689, 0.809), (690, 0.729),
                            (691, 0.625), (692, 0.506), (693, 0.382), (694, 0.272), (695, 0.183), (696, 0.12),
                            (697, 0.079), (698, 0.053), (699, 0.036), (700, 0.025), (701, 0.02), (702, 0.014),
                            (703, 0.01), (704, 0.007)]
        responses['NIR'] = [(741, 0.001), (742, 0.002), (743, 0.002), (744, 0.003), (745, 0.004), (746, 0.003),
                            (747, 0.003), (748, 0.002), (749, 0.002), (750, 0.001), (751, 0.014), (752, 0.018),
                            (753, 0.022), (754, 0.027), (755, 0.032), (756, 0.038), (757, 0.047), (758, 0.056),
                            (759, 0.069), (760, 0.069), (761, 0.083), (762, 0.099), (763, 0.121), (764, 0.146),
                            (765, 0.175), (766, 0.209), (767, 0.248), (768, 0.294), (769, 0.346), (770, 0.402),
                            (771, 0.463), (772, 0.523), (773, 0.588), (774, 0.649), (775, 0.705), (776, 0.757),
                            (777, 0.797), (778, 0.827), (779, 0.853), (780, 0.871), (781, 0.884), (782, 0.892),
                            (783, 0.899), (784, 0.903), (785, 0.908), (786, 0.911), (787, 0.916), (788, 0.92),
                            (789, 0.925), (790, 0.926), (791, 0.927), (792, 0.927), (793, 0.929), (794, 0.932),
                            (795, 0.93), (796, 0.926), (797, 0.926), (798, 0.925), (799, 0.928), (800, 0.925),
                            (801, 0.926), (802, 0.928), (803, 0.928), (804, 0.928), (805, 0.923), (806, 0.92),
                            (807, 0.919), (808, 0.914), (809, 0.91), (810, 0.908), (811, 0.905), (812, 0.903),
                            (813, 0.904), (814, 0.902), (815, 0.909), (816, 0.917), (817, 0.92), (818, 0.928),
                            (819, 0.938), (820, 0.946), (821, 0.953), (822, 0.962), (823, 0.969), (824, 0.971),
                            (825, 0.971), (826, 0.97), (827, 0.969), (828, 0.969), (829, 0.97), (830, 0.967),
                            (831, 0.969), (832, 0.968), (833, 0.963), (834, 0.965), (835, 0.967), (836, 0.965),
                            (837, 0.963), (838, 0.958), (839, 0.95), (840, 0.949), (841, 0.943), (842, 0.933),
                            (843, 0.929), (844, 0.928), (845, 0.925), (846, 0.924), (847, 0.927), (848, 0.932),
                            (849, 0.934), (850, 0.943), (851, 0.952), (852, 0.956), (853, 0.966), (854, 0.977),
                            (855, 0.985), (856, 0.99), (857, 0.992), (858, 0.993), (859, 0.994), (860, 0.998),
                            (861, 0.996), (862, 0.992), (863, 0.991), (864, 0.992), (865, 0.994), (866, 0.993),
                            (867, 0.997), (868, 0.997), (869, 0.996), (870, 0.998), (871, 0.999), (872, 1.0),
                            (873, 0.999), (874, 0.996), (875, 0.991), (876, 0.99), (877, 0.991), (878, 0.985),
                            (879, 0.978), (880, 0.969), (881, 0.955), (882, 0.937), (883, 0.916), (884, 0.892),
                            (885, 0.868), (886, 0.845), (887, 0.824), (888, 0.811), (889, 0.807), (890, 0.819),
                            (891, 0.841), (892, 0.868), (893, 0.892), (894, 0.892), (895, 0.854), (896, 0.77),
                            (897, 0.644), (898, 0.501), (899, 0.365), (900, 0.256), (901, 0.177), (902, 0.122),
                            (903, 0.085), (904, 0.061), (905, 0.044), (906, 0.032), (907, 0.025), (908, 0.019),
                            (909, 0.014), (910, 0.011), (911, 0.011), (912, 0.008), (913, 0.006), (914, 0.005)]
        responses['SWIR-1'] = [(1508, 0.001), (1509, 0.001), (1510, 0.001), (1511, 0.007), (1512, 0.013), (1513, 0.01),
                               (1514, 0.006), (1515, 0.012), (1516, 0.008), (1517, 0.003), (1518, 0.009), (1519, 0.015),
                               (1520, 0.013), (1521, 0.012), (1522, 0.018), (1523, 0.024), (1524, 0.032), (1525, 0.04),
                               (1526, 0.041), (1527, 0.049), (1528, 0.057), (1529, 0.067), (1530, 0.076), (1531, 0.087),
                               (1532, 0.097), (1533, 0.109), (1534, 0.12), (1535, 0.148), (1536, 0.176), (1537, 0.196),
                               (1538, 0.215), (1539, 0.244), (1540, 0.274), (1541, 0.306), (1542, 0.339), (1543, 0.393),
                               (1544, 0.428), (1545, 0.462), (1546, 0.481), (1547, 0.499), (1548, 0.529), (1549, 0.558),
                               (1550, 0.578), (1551, 0.598), (1552, 0.616), (1553, 0.634), (1554, 0.65), (1555, 0.667),
                               (1556, 0.686), (1557, 0.704), (1558, 0.714), (1559, 0.724), (1560, 0.737), (1561, 0.75),
                               (1562, 0.764), (1563, 0.778), (1564, 0.793), (1565, 0.808), (1566, 0.817), (1567, 0.825),
                               (1568, 0.838), (1569, 0.851), (1570, 0.859), (1571, 0.867), (1572, 0.872), (1573, 0.878),
                               (1574, 0.884), (1575, 0.893), (1576, 0.902), (1577, 0.901), (1578, 0.901), (1579, 0.899),
                               (1580, 0.896), (1581, 0.896), (1582, 0.897), (1583, 0.893), (1584, 0.89), (1585, 0.895),
                               (1586, 0.899), (1587, 0.891), (1588, 0.884), (1589, 0.88), (1590, 0.876), (1591, 0.872),
                               (1592, 0.867), (1593, 0.87), (1594, 0.873), (1595, 0.873), (1596, 0.872), (1597, 0.875),
                               (1598, 0.879), (1599, 0.877), (1600, 0.874), (1601, 0.868), (1602, 0.861), (1603, 0.86),
                               (1604, 0.859), (1605, 0.868), (1606, 0.877), (1607, 0.878), (1608, 0.879), (1609, 0.889),
                               (1610, 0.899), (1611, 0.897), (1612, 0.895), (1613, 0.893), (1614, 0.896), (1615, 0.9),
                               (1616, 0.898), (1617, 0.897), (1618, 0.907), (1619, 0.917), (1620, 0.919), (1621, 0.921),
                               (1622, 0.924), (1623, 0.926), (1624, 0.928), (1625, 0.929), (1626, 0.937), (1627, 0.945),
                               (1628, 0.946), (1629, 0.947), (1630, 0.947), (1631, 0.948), (1632, 0.951), (1633, 0.955),
                               (1634, 0.954), (1635, 0.952), (1636, 0.961), (1637, 0.969), (1638, 0.964), (1639, 0.96),
                               (1640, 0.961), (1641, 0.962), (1642, 0.961), (1643, 0.959), (1644, 0.969), (1645, 0.978),
                               (1646, 0.969), (1647, 0.96), (1648, 0.957), (1649, 0.955), (1650, 0.954), (1651, 0.952),
                               (1652, 0.951), (1653, 0.951), (1654, 0.951), (1655, 0.952), (1656, 0.952), (1657, 0.954),
                               (1658, 0.956), (1659, 0.95), (1660, 0.944), (1661, 0.939), (1662, 0.935), (1663, 0.934),
                               (1664, 0.933), (1665, 0.931), (1666, 0.928), (1667, 0.935), (1668, 0.942), (1669, 0.945),
                               (1670, 0.948), (1671, 0.945), (1672, 0.942), (1673, 0.938), (1674, 0.933), (1675, 0.939),
                               (1676, 0.944), (1677, 0.946), (1678, 0.948), (1679, 0.947), (1680, 0.945), (1681, 0.944),
                               (1682, 0.943), (1683, 0.947), (1684, 0.951), (1685, 0.955), (1686, 0.96), (1687, 0.964),
                               (1688, 0.965), (1689, 0.967), (1690, 0.969), (1691, 0.971), (1692, 0.972), (1693, 0.974),
                               (1694, 0.982), (1695, 0.991), (1696, 0.993), (1697, 0.995), (1698, 0.997), (1699, 0.999),
                               (1700, 0.998), (1701, 0.996), (1702, 0.995), (1703, 0.994), (1704, 0.997), (1705, 1.0),
                               (1706, 0.997), (1707, 0.994), (1708, 0.988), (1709, 0.983), (1710, 0.987), (1711, 0.99),
                               (1712, 0.989), (1713, 0.988), (1714, 0.987), (1715, 0.989), (1716, 0.992), (1717, 0.989),
                               (1718, 0.986), (1719, 0.984), (1720, 0.981), (1721, 0.982), (1722, 0.983), (1723, 0.979),
                               (1724, 0.976), (1725, 0.978), (1726, 0.97), (1727, 0.969), (1728, 0.968), (1729, 0.964),
                               (1730, 0.96), (1731, 0.952), (1732, 0.944), (1733, 0.933), (1734, 0.921), (1735, 0.902),
                               (1736, 0.883), (1737, 0.864), (1738, 0.845), (1739, 0.818), (1740, 0.791), (1741, 0.751),
                               (1742, 0.711), (1743, 0.674), (1744, 0.638), (1745, 0.608), (1746, 0.577), (1747, 0.547),
                               (1748, 0.505), (1749, 0.462), (1750, 0.428), (1751, 0.393), (1752, 0.359), (1753, 0.325),
                               (1754, 0.296), (1755, 0.267), (1756, 0.239), (1757, 0.212), (1758, 0.193), (1759, 0.175),
                               (1760, 0.159), (1761, 0.142), (1762, 0.127), (1763, 0.111), (1764, 0.097), (1765, 0.084),
                               (1766, 0.08), (1767, 0.077), (1768, 0.067), (1769, 0.058), (1770, 0.053), (1771, 0.049),
                               (1772, 0.045), (1773, 0.042), (1774, 0.041), (1775, 0.039), (1776, 0.036), (1777, 0.034),
                               (1778, 0.027), (1779, 0.02), (1780, 0.021), (1781, 0.021), (1782, 0.021), (1783, 0.022),
                               (1784, 0.016), (1785, 0.011), (1786, 0.012), (1787, 0.012), (1788, 0.008), (1789, 0.004),
                               (1790, 0.006), (1791, 0.008), (1792, 0.004)]
        responses['SWIR-2'] = [(2015, 0.002), (2016, 0.002), (2017, 0.002), (2018, 0.002), (2019, 0.007), (2020, 0.012),
                               (2021, 0.01), (2022, 0.009), (2023, 0.008), (2024, 0.007), (2025, 0.009), (2026, 0.011),
                               (2027, 0.015), (2028, 0.02), (2029, 0.019), (2030, 0.017), (2031, 0.023), (2032, 0.03),
                               (2033, 0.032), (2034, 0.035), (2035, 0.037), (2036, 0.041), (2037, 0.044), (2038, 0.047),
                               (2039, 0.051), (2040, 0.058), (2041, 0.065), (2042, 0.072), (2043, 0.08), (2044, 0.084),
                               (2045, 0.088), (2046, 0.095), (2047, 0.102), (2048, 0.117), (2049, 0.133), (2050, 0.149),
                               (2051, 0.165), (2052, 0.188), (2053, 0.204), (2054, 0.22), (2055, 0.242), (2056, 0.264),
                               (2057, 0.29), (2058, 0.316), (2059, 0.342), (2060, 0.367), (2061, 0.394), (2062, 0.421),
                               (2063, 0.452), (2064, 0.484), (2065, 0.519), (2066, 0.554), (2067, 0.59), (2068, 0.63),
                               (2069, 0.67), (2070, 0.677), (2071, 0.683), (2072, 0.707), (2073, 0.73), (2074, 0.743),
                               (2075, 0.756), (2076, 0.762), (2077, 0.767), (2078, 0.781), (2079, 0.794), (2080, 0.784),
                               (2081, 0.774), (2082, 0.775), (2083, 0.776), (2084, 0.783), (2085, 0.789), (2086, 0.775),
                               (2087, 0.78), (2088, 0.784), (2089, 0.781), (2090, 0.778), (2091, 0.773), (2092, 0.768),
                               (2093, 0.765), (2094, 0.762), (2095, 0.762), (2096, 0.761), (2097, 0.766), (2098, 0.77),
                               (2099, 0.775), (2100, 0.775), (2101, 0.77), (2102, 0.764), (2103, 0.774), (2104, 0.784),
                               (2105, 0.788), (2106, 0.792), (2107, 0.803), (2108, 0.814), (2109, 0.804), (2110, 0.794),
                               (2111, 0.809), (2112, 0.825), (2113, 0.821), (2114, 0.817), (2115, 0.811), (2116, 0.806),
                               (2117, 0.819), (2118, 0.82), (2119, 0.821), (2120, 0.836), (2121, 0.852), (2122, 0.842),
                               (2123, 0.832), (2124, 0.834), (2125, 0.836), (2126, 0.843), (2127, 0.85), (2128, 0.853),
                               (2129, 0.855), (2130, 0.859), (2131, 0.862), (2132, 0.857), (2133, 0.853), (2134, 0.862),
                               (2135, 0.871), (2136, 0.848), (2137, 0.865), (2138, 0.882), (2139, 0.878), (2140, 0.875),
                               (2141, 0.868), (2142, 0.86), (2143, 0.858), (2144, 0.856), (2145, 0.872), (2146, 0.887),
                               (2147, 0.868), (2148, 0.85), (2149, 0.861), (2150, 0.872), (2151, 0.879), (2152, 0.868),
                               (2153, 0.857), (2154, 0.861), (2155, 0.865), (2156, 0.866), (2157, 0.867), (2158, 0.869),
                               (2159, 0.871), (2160, 0.877), (2161, 0.882), (2162, 0.876), (2163, 0.87), (2164, 0.87),
                               (2165, 0.869), (2166, 0.873), (2167, 0.875), (2168, 0.877), (2169, 0.872), (2170, 0.868),
                               (2171, 0.874), (2172, 0.88), (2173, 0.878), (2174, 0.877), (2175, 0.873), (2176, 0.87),
                               (2177, 0.874), (2178, 0.878), (2179, 0.879), (2180, 0.88), (2181, 0.874), (2182, 0.868),
                               (2183, 0.881), (2184, 0.875), (2185, 0.87), (2186, 0.863), (2187, 0.856), (2188, 0.859),
                               (2189, 0.863), (2190, 0.863), (2191, 0.863), (2192, 0.86), (2193, 0.857), (2194, 0.85),
                               (2195, 0.844), (2196, 0.852), (2197, 0.859), (2198, 0.858), (2199, 0.857), (2200, 0.854),
                               (2201, 0.852), (2202, 0.859), (2203, 0.866), (2204, 0.867), (2205, 0.868), (2206, 0.862),
                               (2207, 0.856), (2208, 0.856), (2209, 0.856), (2210, 0.847), (2211, 0.854), (2212, 0.861),
                               (2213, 0.862), (2214, 0.862), (2215, 0.851), (2216, 0.84), (2217, 0.848), (2218, 0.856),
                               (2219, 0.847), (2220, 0.838), (2221, 0.847), (2222, 0.856), (2223, 0.837), (2224, 0.839),
                               (2225, 0.84), (2226, 0.842), (2227, 0.826), (2228, 0.835), (2229, 0.844), (2230, 0.836),
                               (2231, 0.827), (2232, 0.835), (2233, 0.842), (2234, 0.832), (2235, 0.822), (2236, 0.832),
                               (2237, 0.843), (2238, 0.833), (2239, 0.823), (2240, 0.839), (2241, 0.854), (2242, 0.839),
                               (2243, 0.846), (2244, 0.853), (2245, 0.854), (2246, 0.854), (2247, 0.859), (2248, 0.865),
                               (2249, 0.869), (2250, 0.873), (2251, 0.871), (2252, 0.869), (2253, 0.867), (2254, 0.865),
                               (2255, 0.879), (2256, 0.893), (2257, 0.891), (2258, 0.89), (2259, 0.89), (2260, 0.898),
                               (2261, 0.906), (2262, 0.915), (2263, 0.924), (2264, 0.922), (2265, 0.92), (2266, 0.921),
                               (2267, 0.922), (2268, 0.931), (2269, 0.939), (2270, 0.928), (2271, 0.916), (2272, 0.928),
                               (2273, 0.94), (2274, 0.93), (2275, 0.936), (2276, 0.942), (2277, 0.949), (2278, 0.957),
                               (2279, 0.956), (2280, 0.954), (2281, 0.952), (2282, 0.951), (2283, 0.952), (2284, 0.954),
                               (2285, 0.96), (2286, 0.966), (2287, 0.97), (2288, 0.975), (2289, 0.98), (2290, 0.985),
                               (2291, 0.978), (2292, 0.971), (2293, 0.973), (2294, 0.972), (2295, 0.97), (2296, 0.982),
                               (2297, 0.993), (2298, 0.994), (2299, 0.996), (2300, 0.989), (2301, 0.983), (2302, 0.977),
                               (2303, 0.972), (2304, 0.986), (2305, 1.0), (2306, 0.999), (2307, 0.998), (2308, 0.985),
                               (2309, 0.971), (2310, 0.968), (2311, 0.967), (2312, 0.967), (2313, 0.965), (2314, 0.962),
                               (2315, 0.956), (2316, 0.949), (2317, 0.936), (2318, 0.923), (2319, 0.926), (2320, 0.929),
                               (2321, 0.923), (2322, 0.917), (2323, 0.934), (2324, 0.919), (2325, 0.903), (2326, 0.914),
                               (2327, 0.926), (2328, 0.921), (2329, 0.916), (2330, 0.929), (2331, 0.942), (2332, 0.933),
                               (2333, 0.924), (2334, 0.922), (2335, 0.92), (2336, 0.891), (2337, 0.863), (2338, 0.844),
                               (2339, 0.824), (2340, 0.775), (2341, 0.729), (2342, 0.684), (2343, 0.633), (2344, 0.583),
                               (2345, 0.531), (2346, 0.48), (2347, 0.429), (2348, 0.378), (2349, 0.326), (2350, 0.275),
                               (2351, 0.254), (2352, 0.233), (2353, 0.202), (2354, 0.171), (2355, 0.131), (2356, 0.121),
                               (2357, 0.111), (2358, 0.096), (2359, 0.081), (2360, 0.075), (2361, 0.069), (2362, 0.057),
                               (2363, 0.046), (2364, 0.038), (2365, 0.029), (2366, 0.034), (2367, 0.038), (2368, 0.018),
                               (2369, 0.0), (2370, 0.013), (2371, 0.029), (2372, 0.023), (2373, 0.016), (2374, 0.009),
                               (2375, 0.013), (2376, 0.017), (2377, 0.01), (2378, 0.003), (2379, 0.009), (2380, 0.015),
                               (2381, 0.007)]
        # responses['Pan'] = [(502, 0.001), (503, 0.005), (504, 0.008), (505, 0.018), (506, 0.027), (507, 0.046), (508, 0.066), (509, 0.108), (510, 0.15), (511, 0.22), (512, 0.289), (513, 0.368), (514, 0.447), (515, 0.502), (516, 0.556), (517, 0.575), (518, 0.594), (519, 0.596), (520, 0.599), (521, 0.6), (522, 0.6), (523, 0.604), (524, 0.607), (525, 0.609), (526, 0.612), (527, 0.613), (528, 0.615), (529, 0.613), (530, 0.61), (531, 0.607), (532, 0.604), (533, 0.603), (534, 0.602), (535, 0.604), (536, 0.605), (537, 0.61), (538, 0.614), (539, 0.62), (540, 0.627), (541, 0.632), (542, 0.637), (543, 0.64), (544, 0.643), (545, 0.645), (546, 0.646), (547, 0.645), (548, 0.643), (549, 0.638), (550, 0.632), (551, 0.63), (552, 0.627), (553, 0.625), (554, 0.623), (555, 0.625), (556, 0.626), (557, 0.63), (558, 0.634), (559, 0.638), (560, 0.642), (561, 0.648), (562, 0.655), (563, 0.663), (564, 0.672), (565, 0.678), (566, 0.683), (567, 0.688), (568, 0.692), (569, 0.694), (570, 0.697), (571, 0.699), (572, 0.7), (573, 0.701), (574, 0.702), (575, 0.705), (576, 0.708), (577, 0.71), (578, 0.712), (579, 0.712), (580, 0.713), (581, 0.715), (582, 0.716), (583, 0.717), (584, 0.718), (585, 0.718), (586, 0.718), (587, 0.714), (588, 0.71), (589, 0.709), (590, 0.707), (591, 0.706), (592, 0.705), (593, 0.703), (594, 0.701), (595, 0.703), (596, 0.705), (597, 0.711), (598, 0.718), (599, 0.724), (600, 0.73), (601, 0.736), (602, 0.742), (603, 0.746), (604, 0.75), (605, 0.753), (606, 0.757), (607, 0.76), (608, 0.763), (609, 0.763), (610, 0.764), (611, 0.76), (612, 0.755), (613, 0.752), (614, 0.748), (615, 0.745), (616, 0.742), (617, 0.737), (618, 0.733), (619, 0.731), (620, 0.729), (621, 0.729), (622, 0.728), (623, 0.729), (624, 0.73), (625, 0.731), (626, 0.732), (627, 0.732), (628, 0.733), (629, 0.734), (630, 0.734), (631, 0.738), (632, 0.742), (633, 0.745), (634, 0.748), (635, 0.75), (636, 0.751), (637, 0.753), (638, 0.755), (639, 0.757), (640, 0.758), (641, 0.759), (642, 0.76), (643, 0.763), (644, 0.767), (645, 0.768), (646, 0.769), (647, 0.771), (648, 0.773), (649, 0.776), (650, 0.779), (651, 0.78), (652, 0.781), (653, 0.782), (654, 0.783), (655, 0.785), (656, 0.787), (657, 0.789), (658, 0.791), (659, 0.792), (660, 0.793), (661, 0.793), (662, 0.792), (663, 0.791), (664, 0.791), (665, 0.791), (666, 0.792), (667, 0.794), (668, 0.796), (669, 0.797), (670, 0.798), (671, 0.799), (672, 0.801), (673, 0.803), (674, 0.804), (675, 0.806), (676, 0.808), (677, 0.812), (678, 0.815), (679, 0.817), (680, 0.82), (681, 0.824), (682, 0.827), (683, 0.828), (684, 0.829), (685, 0.831), (686, 0.834), (687, 0.836), (688, 0.838), (689, 0.84), (690, 0.842), (691, 0.845), (692, 0.847), (693, 0.85), (694, 0.853), (695, 0.854), (696, 0.856), (697, 0.859), (698, 0.862), (699, 0.865), (700, 0.868), (701, 0.869), (702, 0.871), (703, 0.873), (704, 0.876), (705, 0.88), (706, 0.883), (707, 0.885), (708, 0.886), (709, 0.889), (710, 0.892), (711, 0.893), (712, 0.894), (713, 0.895), (714, 0.896), (715, 0.896), (716, 0.896), (717, 0.895), (718, 0.894), (719, 0.894), (720, 0.894), (721, 0.894), (722, 0.894), (723, 0.895), (724, 0.895), (725, 0.896), (726, 0.896), (727, 0.897), (728, 0.898), (729, 0.899), (730, 0.9), (731, 0.901), (732, 0.903), (733, 0.903), (734, 0.904), (735, 0.903), (736, 0.903), (737, 0.903), (738, 0.902), (739, 0.901), (740, 0.9), (741, 0.898), (742, 0.897), (743, 0.896), (744, 0.896), (745, 0.893), (746, 0.891), (747, 0.885), (748, 0.88), (749, 0.88), (750, 0.879), (751, 0.88), (752, 0.88), (753, 0.877), (754, 0.873), (755, 0.873), (756, 0.873), (757, 0.875), (758, 0.877), (759, 0.878), (760, 0.88), (761, 0.88), (762, 0.88), (763, 0.882), (764, 0.885), (765, 0.887), (766, 0.888), (767, 0.89), (768, 0.892), (769, 0.893), (770, 0.893), (771, 0.898), (772, 0.902), (773, 0.905), (774, 0.908), (775, 0.91), (776, 0.913), (777, 0.916), (778, 0.92), (779, 0.92), (780, 0.92), (781, 0.919), (782, 0.918), (783, 0.917), (784, 0.916), (785, 0.916), (786, 0.916), (787, 0.918), (788, 0.919), (789, 0.919), (790, 0.918), (791, 0.918), (792, 0.917), (793, 0.916), (794, 0.916), (795, 0.916), (796, 0.915), (797, 0.916), (798, 0.918), (799, 0.923), (800, 0.927), (801, 0.928), (802, 0.928), (803, 0.93), (804, 0.932), (805, 0.938), (806, 0.943), (807, 0.947), (808, 0.952), (809, 0.955), (810, 0.957), (811, 0.96), (812, 0.962), (813, 0.965), (814, 0.969), (815, 0.97), (816, 0.97), (817, 0.971), (818, 0.972), (819, 0.975), (820, 0.977), (821, 0.978), (822, 0.979), (823, 0.98), (824, 0.981), (825, 0.984), (826, 0.987), (827, 0.989), (828, 0.992), (829, 0.994), (830, 0.997), (831, 0.998), (832, 0.998), (833, 0.999), (834, 1.0), (835, 0.998), (836, 0.996), (837, 0.995), (838, 0.995), (839, 0.995), (840, 0.994), (841, 0.993), (842, 0.992), (843, 0.992), (844, 0.992), (845, 0.993), (846, 0.994), (847, 0.993), (848, 0.992), (849, 0.989), (850, 0.987), (851, 0.982), (852, 0.978), (853, 0.973), (854, 0.968), (855, 0.965), (856, 0.962), (857, 0.96), (858, 0.957), (859, 0.953), (860, 0.949), (861, 0.943), (862, 0.937), (863, 0.933), (864, 0.928), (865, 0.924), (866, 0.92), (867, 0.916), (868, 0.911), (869, 0.909), (870, 0.907), (871, 0.906), (872, 0.905), (873, 0.905), (874, 0.906), (875, 0.909), (876, 0.911), (877, 0.916), (878, 0.922), (879, 0.931), (880, 0.94), (881, 0.951), (882, 0.962), (883, 0.97), (884, 0.977), (885, 0.978), (886, 0.979), (887, 0.968), (888, 0.957), (889, 0.926), (890, 0.895), (891, 0.841), (892, 0.787), (893, 0.717), (894, 0.647), (895, 0.572), (896, 0.496), (897, 0.429), (898, 0.363), (899, 0.31), (900, 0.258), (901, 0.219), (902, 0.181), (903, 0.154), (904, 0.127), (905, 0.108), (906, 0.089), (907, 0.075), (908, 0.062), (909, 0.053), (910, 0.044)]
        return responses