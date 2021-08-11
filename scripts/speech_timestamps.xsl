<?xml version="1.0"?>

<!--
    This script extracts time related data about every word together with 
    basic info about speaker.
    
    The resulting file consists of header row followed by a single row
    for each spoken word. Columns are tab-separated.
-->

<xsl:stylesheet 
    version="1.0" 
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:fn="http://www.w3.org/2005/xpath-functions"
    xmlns:tei="http://www.tei-c.org/ns/1.0">
    <xsl:output method="text" omit-xml-declaration="yes" indent="no"/>

    <!-- Absolute path to the timeline element -->
    <xsl:variable name="timeline_path" select="/tei:TEI/tei:text/tei:body/tei:timeline"/>

    <!-- Tab for each timeline data column
         - start, end, absolute, audio_id, audio_source, audio_url
    -->
    <xsl:variable name="timeline_empty" select="'&#x9;&#x9;&#x9;&#x9;&#x9;&#x9;'"/>

    <!-- Header row -->
    <xsl:template match="/">
        <xsl:text>id&#x9;</xsl:text>
        <xsl:text>word&#x9;</xsl:text>
        <xsl:text>start&#x9;</xsl:text>
        <xsl:text>end&#x9;</xsl:text>
        <xsl:text>absolute&#x9;</xsl:text>
        <xsl:text>audio_id&#x9;</xsl:text>
        <xsl:text>audio_source&#x9;</xsl:text>
        <xsl:text>audio_url&#x9;</xsl:text>
        <xsl:text>speaker&#x9;</xsl:text>
        <xsl:text>role</xsl:text>
        <xsl:text>&#xA;</xsl:text>

        <xsl:apply-templates/>
    </xsl:template>

    <!-- Word row -->
    <xsl:template match="//tei:w">
        <xsl:variable name="word_id" select="@xml:id"/>

        <!-- id -->
        <xsl:value-of select="$word_id"/>
        <xsl:text>&#x9;</xsl:text>

        <!-- word -->
        <xsl:value-of select="."/>
        <xsl:text>&#x9;</xsl:text>

        <!-- time-related data -->
        <xsl:choose>
            <xsl:when test="$timeline_path">
                <xsl:call-template name="timeline">
                    <xsl:with-param name="word_id" select="$word_id"/>
                </xsl:call-template>
            </xsl:when>
            <xsl:otherwise>
                <xsl:value-of select="$timeline_empty"/>
            </xsl:otherwise>
        </xsl:choose>

        <!-- speaker -->
        <xsl:value-of select="substring(ancestor::tei:u/@who,2)"/>
        <xsl:text>&#x9;</xsl:text>

        <!-- role -->
        <xsl:value-of select="substring(ancestor::tei:u/@ana,2)"/>
        <xsl:text>&#xA;</xsl:text>
    </xsl:template>

    <!-- Find proper timeline template -->
    <xsl:template name="timeline">
        <xsl:param name="word_id"/>

        <xsl:variable name="word_start"><xsl:value-of select="$word_id"/>.ab</xsl:variable>
        <xsl:variable name="word_end"><xsl:value-of select="$word_id"/>.ae</xsl:variable>

        <xsl:variable name="word_start_since_hash">
            <xsl:value-of select="$timeline_path/tei:when[@xml:id=$word_start]/@since"/>
        </xsl:variable>
        
        <xsl:variable name="word_end_since_hash">
            <xsl:value-of select="$timeline_path/tei:when[@xml:id=$word_end]/@since"/>
        </xsl:variable>

        <!-- Start and end of word anchors belong to the same audio origin -->
        <xsl:variable name="since_hash">
            <xsl:choose>
                <xsl:when test="$word_start_since_hash != ''">
                    <xsl:value-of select="$word_start_since_hash"/>
                </xsl:when>
                <xsl:otherwise>
                    <xsl:value-of select="$word_end_since_hash"/>
                </xsl:otherwise>
            </xsl:choose>
        </xsl:variable>

        <xsl:variable name="since" select="substring($since_hash,2)"/>

        <!-- Apply proper template-->
        <xsl:choose>
            <xsl:when test="$timeline_path[@origin=$since_hash]">
                <xsl:apply-templates select="$timeline_path[@origin=$since_hash]" mode="called">
                    <xsl:with-param name="word_start" select="$word_start"/>
                    <xsl:with-param name="word_end" select="$word_end"/>
                    <xsl:with-param name="since" select="$since"/>
                </xsl:apply-templates>
            </xsl:when>
            <xsl:otherwise>
                <xsl:value-of select="$timeline_empty"/>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>

    <!-- Timeline data -->
    <xsl:template match="/tei:TEI/tei:text/tei:body/tei:timeline" mode="called">
        <xsl:param name="word_start"/>
        <xsl:param name="word_end"/>
        <xsl:param name="since"/>

        <!-- start -->
        <xsl:value-of select="tei:when[@xml:id=$word_start]/@interval"/>
        <xsl:text>&#x9;</xsl:text>

        <!-- end -->
        <xsl:value-of select="tei:when[@xml:id=$word_end]/@interval"/>
        <xsl:text>&#x9;</xsl:text>

        <!-- absolute -->
        <xsl:value-of select="tei:when[@xml:id=$since]/@absolute"/>
        <xsl:text>&#x9;</xsl:text>

        <!-- audio -->
        <xsl:variable name="corresp_hash"><xsl:value-of select="./@corresp"/></xsl:variable>
        <xsl:variable name="corresp"><xsl:value-of select="substring($corresp_hash,2)"/></xsl:variable>
        
        <xsl:variable 
            name="media_path" 
            select="/tei:TEI/tei:teiHeader/tei:fileDesc/tei:sourceDesc/tei:recordingStmt/tei:recording[@type='audio']"
        />

        <!-- audio_id -->
        <xsl:value-of select="$corresp"/>
        <xsl:text>&#x9;</xsl:text>

        <!-- audio_source -->
        <xsl:value-of select="$media_path/tei:media[@xml:id=$corresp]/@source"/>
        <xsl:text>&#x9;</xsl:text>

        <!-- audio_url -->
        <xsl:value-of select="$media_path/tei:media[@xml:id=$corresp]/@url"/>
        <xsl:text>&#x9;</xsl:text>
    </xsl:template>

    <!-- Remove everything else -->
    <xsl:template match="text()" />

</xsl:stylesheet> 

